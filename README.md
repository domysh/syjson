# SyJson - Sync variables to a json file in a simple way

### What this library do?

This library make simple create a json file and read/write directly from this. This can be very useful and easy to use when we need to create small files such as a settings file, avoiding to write and read this manualy.

### How to Install

You can install this library using PyPi (pip)

###### Linux / Windows / MacOs

```bash
pip3 install syjson
```

### How to use

At first you can import SyJson class writing:

```python
from syjson import SyJson
```

now we can use this class for create/read a json file
pretty:int=None, bson:bool=False, cache:bool = True
```python
synced_json = SyJson(
    "file.json",           #Path of the json file
    create_file = True,    #If the file does not exists,
                           #this will automatically create that file
    pretty = None          #If setted to a number, the file will have an
                           #indentation of 'pretty' spaces
    cache = True           #The file is readed only the first time with this option set to
                           #True, if your file have to be modified during the execution set this to false
                           #(Useful for debugging)
)
```

This library use orjson for load and dump json files

---

There are some particular function added for particular use

#### --> synced_json.var()

With var function we can read from file the informations and we get a normal python object, so this python object have to be synced in a next step

#### --> synced_json.sync( value )

With sync function you can assign a variable and sync these informations in the target file

All SyJson object have these functionalityes

---

In Synced dicts there is an additional function that can be usefull in a lot of situation

#### --> synced_json.create( key, default_value )

This function create a pair of key and value if that key is not used in the json file and return the synced object, instead this function will simply return the synced object without overriding existing values.

---

Can bypass the use of sync function when you assign a value to a synced array of a synced dict in the json

```python
f = SyJson("/path/to/file.json")

f["dict"] = {"num":0}
f["list"] = [1]

#Some operation that you can do without using sync function
f["dict"]["num"] = 1
f["dict"].keys()
f["dict"].values()
f["dict"].items()

f["list"][0] = 0
f["list"].append(1)
f["list"].pop()
f["list"].index(0)
```

---

### By DomySh - <a href="mailto::me@domysh.com">me@domysh.com</a>

### --> <a href="https://domysh.com">https://domysh.com</a> <--

---
