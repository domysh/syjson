import threading, os
try:
    import ujson as json
except ImportError:
    import json

class SyJsonObj:
    def __init__(self):
        #For delete stange error on pylint
        self.request_lock = None 
        raise Exception('Abstract Class')

    def __getitem__(self,key):
        raise Exception('Abstract Class')

    def _read(self):
        raise Exception('Abstract Class')

    def _write(self,var):
        raise Exception('Abstract Class')

    def var(self):
        self.request_lock.acquire()
        try:
            return self._read()
        finally:
            self.request_lock.release()

    def sync(self,var):
        self.request_lock.acquire()
        try:
            return self._write(var)
        finally:
            self.request_lock.release()
    
    def _get_synced_item(self,key,v):
        if type(v) in (list,tuple):
            v = SyncedList(self,key)
        elif type(v) in (dict,):
            v = SyncedDict(self,key)
        return v

    def _get_desynced_item(self,v):
        if issubclass(v.__class__,SyJsonObj):
            return v.var()
        return v

class SyJson(SyJsonObj):
    def __init__(self,path:str, create_file=True, pretty=False):
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
    
    def _read(self):
        self.f_lock.acquire()
        try:
            with open(self.file_path,'rt') as fl:
                f = fl.read()
            if f != '': return json.loads(f)
            else: return {}
        finally:
            self.f_lock.release()

    def _write(self,dic):
        dic = self._get_desynced_item(dic)
        self.f_lock.acquire()
        try:
            with open(self.file_path,'wt') as fl:
                if(self.prittyfy):
                    fl.write(json.dumps(dic,indent=3))
                else: 
                    fl.write(json.dumps(dic))
                fl.flush()
        finally:
            self.f_lock.release()
    
    def __str__(self):return self.var().__str__()

    def __getitem__(self,key):
        d = self._read()
        return self._get_synced_item(key,d[key])
        
    def __setitem__(self, key, value):
        value = self._get_desynced_item(value)
        d = self._read()
        d[key] = value
        self._write(d)

    def keys(self):return self.var().keys()
    def items(self):return self.var().items()
    def values(self):return self.var().values()

class InnerIterObject(SyJsonObj):
    def __init__(self,root:SyJsonObj,key):
        self.root = root
        self.request_lock = self.root.request_lock
        self.root_key = key

    def _read(self):
        return self.root._read()[self.root_key]

    def _write(self,var):
        var = self.root._get_desynced_item(var)
        val = self.root._read() 
        val[self.root_key] = var
        self.root._write(val)

    def __str__(self):return self.var().__str__()

    def __getitem__(self,key):
        return self._get_synced_item(key,self.var()[key])

    def __setitem__(self, key, value):
        value = self._get_desynced_item(value)
        val = self.var() 
        val[key] = value
        self.sync(val)
    
    def __len__(self):
        return self.var().__len__()

class SyncedList(InnerIterObject):
    def __init__(self,root:SyJsonObj,key):
        InnerIterObject.__init__(self,root,key)

    def append(self,v):
        v = self._get_desynced_item(v)
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
        res = self._get_desynced_item(res)
        self.sync(val)
        return res

    def index(self,arg):return self.var().index(arg)

class SyncedDict(InnerIterObject):
    def __init__(self,root:SyJsonObj,key):
        InnerIterObject.__init__(self,root,key)
        
    def keys(self):return self.var().keys()
    def values(self):return self.var().values()
    def items(self):return self.var().items()

