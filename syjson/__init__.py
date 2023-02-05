import threading, os, orjson

class InnerObject:
    """ A general Synced variable """

    def __init__(self,root,keychain):
        self.root = root
        self.keychain = keychain

    def var(self):
        """ read function without mutex lock (unsafe to use, but used internaly) """
        return self.root.var(self.keychain)

    def sync(self,val):
        self.root.sync(val, keychain=self.keychain)
    
    def __ge__(self,compare_to):
        return self.var().__ge__(self.desynced(compare_to))
    def __le__(self,compare_to):
        return self.var().__le__(self.desynced(compare_to))
    def __gt__(self,compare_to):
        return self.var().__gt__(self.desynced(compare_to))
    def __lt__(self,compare_to):
        return self.var().__lt__(self.desynced(compare_to))
    def __eq__(self,compare_to):
        return self.var().__eq__(self.desynced(compare_to))
    def __str__(self):return self.var().__str__()

    def synced(self,v, key):
        """ tranform traditional classes object in synced object """
        if type(v) in (list,tuple):
            v = SyncedList(self.root,self.keychain+[key])
        elif type(v) in (dict,):
            v = SyncedDict(self.root,self.keychain+[key])
        return v

    @staticmethod
    def desynced(v):
        """ tranform synced object in traditional classes """
        if issubclass(v.__class__,InnerObject):
            return v.var()
        return v

class InnerIterObject(InnerObject):
    """ A general Synced iterable variable """

    def __init__(self,root:InnerObject,keychain):
        InnerObject.__init__(self,root,keychain)

    def __contains__(self, key):
        return key in self.var()
    
    def __getitem__(self,key):
        return self.synced(self.var()[key],key)

    def __setitem__(self, key, value):
        self.root.sync(self.desynced(value),keychain=self.keychain+[key])
    
    def __delitem__(self,name):
        val = self.var()
        del val[name]
        self.sync(val)

    def __len__(self):
        return self.var().__len__()

class SyncedList(InnerIterObject):
    """ A Synced list variable """

    def __init__(self,root:InnerObject,keychain):
        InnerIterObject.__init__(self,root,keychain)

    def append(self,v):
        v = self.desynced(v)
        val = self.var()
        res = val.append(v)
        self.sync(val)
        return res

    def pop(self,*args,**kargs):
        val = self.var()
        res = val.pop(*args,**kargs)
        self.sync(val)
        return res
        
    def remove(self,*args,**kargs):
        val = self.var()
        res = val.remove(*args,**kargs)
        self.sync(val)
        return res

    def index(self,arg): return self.var().index(arg)

class SyncedDict(InnerIterObject):
    """ A Synced dict variable """

    def __init__(self,root:InnerObject,keychain):
        InnerIterObject.__init__(self,root,keychain)
    
    def create(self,key,default):
        """ With this method, you can create a synced variable
        giving a default value if there isn't the key in the dict """
        if key not in self.keys():
            self[key] = default
        return self[key]
        
    def keys(self):return self.root.var(keychain=self.keychain).keys()
    def values(self):return self.root.var(keychain=self.keychain).values()
    def items(self):return self.root.var(keychain=self.keychain).items()


class SyJson(SyncedDict):
    """ create a variable directly linked with a file,
    you can write values directly into the file and read in the sameway"""

    def __init__(self,path:str, create_file:bool=True, pretty:bool=False, cache:bool = True):
        self.file_path = os.path.abspath(path)
        if not os.path.exists(self.file_path):
            if create_file:
                with open(self.file_path,'wt') as fl:
                    fl.write('')
            else:
                raise FileNotFoundError(f'The file {path} doesn\'t exist!')
        self.f_lock = threading.Lock()
        self.prittyfy = pretty
        self.cache = cache
        self._cached = None
        #Make compatible this class with the uppers
        self.keychain = []
        self.root = self

    def var(self,keychain=None):
        """ read function without mutex lock (unsafe to use, but used internaly) """
        if self.cache: 
            if self._cached is None:
                self._cached = self._file_read()
            return self._resolve_read_keychain(dict(self._cached),keychain)
        else:
            return self._resolve_read_keychain(self._file_read(),keychain)
    
    @staticmethod
    def _resolve_read_keychain(dictionary,keychain):
        res = dictionary
        if not keychain is None:
            for k in keychain:
                res = res[k]
        return res

    @staticmethod
    def _resolve_write_keychain(dictionary,value,keychain):
        res = dictionary
        for k in keychain[:-1]:
            res = res[k]
        res[keychain[-1]] = value       

    def _file_read(self):
        self.f_lock.acquire()
        try:
            with open(self.file_path,'r') as fl:
                f = fl.read()
            if f != '': return orjson.loads(f)
            else: return {}
        finally:
            self.f_lock.release()

    def reload(self):
        if self.cache: self._cached = self._file_read()

    def sync(self,value,keychain=None):
        """ write on file new value of a paramether """
        value = self.desynced(value)
        if not keychain is None:
            dic = self.var()
            self._resolve_write_keychain(dic,value,keychain)
        else:
            dic = value
        self.f_lock.acquire()
        try:
            if self.prittyfy:
                value = orjson.dumps(dic,option=orjson.OPT_INDENT_2)
            else: 
                value = orjson.dumps(dic)
            with open(self.file_path,'wb') as fl:
                fl.write(value)
            if self.cache: self._cached = dic
        finally:
            self.f_lock.release()
    
    def __str__(self):return self.var().__str__()
        
