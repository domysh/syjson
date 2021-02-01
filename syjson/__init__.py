import threading, os
try:
    import ujson as json
except ImportError:
    import json

class SyJsonObj:
    """ Abstract class for identify an object linked to a file """

    #Methods that must be overrided
    def __init__(self):
        self.request_lock = None 
        self.get_primitives = None
        raise Exception('Abstract Class')

    def __getitem__(self,key):
        raise Exception('Abstract Class')

    def _read(self):
        raise Exception('Abstract Class')

    def _write(self,var):
        raise Exception('Abstract Class')

    def var(self):
        """ read from file actual value of the var """
        self.request_lock.acquire()
        try:
            return self._read()
        finally:
            self.request_lock.release()

    def sync(self,var):
        """ write on file new value of a paramether """
        self.request_lock.acquire()
        try:
            return self._write(var)
        finally:
            self.request_lock.release()
    
    def _syncing(self,key,v):
        """ tranform traditional classes object in synced object """
        if type(v) in (list,tuple):
            v = SyncedList(self,key)
        elif type(v) in (dict,):
            v = SyncedDict(self,key)
        elif not self.get_primitives:
            v = InnerObject(self,key)
        return v

    def _desyncing(self,v):
        """ tranform synced object in traditional classes """
        if issubclass(v.__class__,SyJsonObj):
            return v.var()
        return v

class InnerObject(SyJsonObj):
    """ A general Synced variable """

    def __init__(self,root:SyJsonObj,key):
        self.root = root
        self.request_lock = self.root.request_lock
        self.get_primitives = self.root.get_primitives
        self.root_key = key

    def _read(self):
        """ read function without mutex lock (unsafe to use, but used internaly) """
        return self.root._read()[self.root_key]

    def _write(self,var):
        """ write function without mutex lock (unsafe to use, but used internaly) """
        var = self.root._desyncing(var)
        val = self.root._read() 
        val[self.root_key] = var
        self.root._write(val)
    
    def __ge__(self,compare_to):
        return self.var().__ge__(self._desyncing(compare_to))
    def __le__(self,compare_to):
        return self.var().__le__(self._desyncing(compare_to))
    def __gt__(self,compare_to):
        return self.var().__gt__(self._desyncing(compare_to))
    def __lt__(self,compare_to):
        return self.var().__lt__(self._desyncing(compare_to))
    def __eq__(self,compare_to):
        return self.var().__eq__(self._desyncing(compare_to))

    def __str__(self):return self.var().__str__()

class InnerIterObject(InnerObject):
    """ A general Synced iterable variable """

    def __init__(self,root:SyJsonObj,key):
        InnerObject.__init__(self,root,key)

    def __getitem__(self,key):
        return self._syncing(key,self.var()[key])

    def __setitem__(self, key, value):
        value = self._desyncing(value)
        val = self.var() 
        val[key] = value
        self.sync(val)
    
    def __len__(self):
        return self.var().__len__()

class SyncedList(InnerIterObject):
    """ A Synced list variable """

    def __init__(self,root:SyJsonObj,key):
        InnerIterObject.__init__(self,root,key)

    def append(self,v):
        v = self._desyncing(v)
        val = self.var()
        res = val.append(v)
        self.sync(val)
        return res

    def __delitem__(self,name):
        val = self.var()
        del val[name]
        self.sync(val)

    def pop(self,num=-1):
        val = self.var()
        res = val.pop(num)
        res = self._desyncing(res)
        self.sync(val)
        return res

    def index(self,arg):return self.var().index(arg)

class SyncedDict(InnerIterObject):
    """ A Synced dict variable """

    def __init__(self,root:SyJsonObj,key):
        InnerIterObject.__init__(self,root,key)
    
    def create(self,key,default):
        """ With this method, you can create a synced variable
        giving a default value if there isn't the key in the dict """
        if key not in self.keys():
            self[key] = default
        return self[key]
        
    def keys(self):return self.var().keys()
    def values(self):return self.var().values()
    def items(self):return self.var().items()


class SyJson(SyncedDict):
    """ create a variable directly linked with a file,
    you can write values directly into the file and read in the sameway
    Paramathers:
        path - path for the json file
        create-file - create the file if the parh don't have a file
        pretty - insert a number of spaces for indent the json file
        get-primitives - non-iterable variables will be not synced object"""

    def __init__(self,path:str, create_file:bool=True, pretty:int=None, get_primitives:bool=False):
        self.file_path = os.path.abspath(path)
        if not os.path.exists(self.file_path):
            if create_file:
                with open(self.file_path,'wt') as fl:
                    fl.write('')
            else:
                raise Exception(f'The file {path} doesn\'t exist!')
        self.f_lock = threading.Lock()
        self.request_lock = threading.Lock()
        self.prittyfy = pretty
        self.get_primitives = get_primitives
    
    def _read(self):
        """ read function without mutex lock (unsafe to use, but used internaly) """
        self.f_lock.acquire()
        try:
            with open(self.file_path,'rt') as fl:
                f = fl.read()
            if f != '': return json.loads(f)
            else: return {}
        finally:
            self.f_lock.release()

    def _write(self,dic):
        """ write on file new value of a paramether """
        dic = self._desyncing(dic)
        self.f_lock.acquire()
        try:
            with open(self.file_path,'wt') as fl:
                if self.prittyfy:
                    fl.write(json.dumps(dic,indent=self.prittyfy))
                else: 
                    fl.write(json.dumps(dic))
        finally:
            self.f_lock.release()
    
    def __str__(self):return self.var().__str__()

    def __getitem__(self,key):
        d = self._read()
        return self._syncing(key,d[key])
        
    def __setitem__(self, key, value):
        value = self._desyncing(value)
        d = self._read()
        d[key] = value
        self._write(d)
