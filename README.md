# SyJson - Sync variables to a json file in a simple way

### What this library do?

This library make simple create a json file and read/write directly from this. This can be very useful and easy to use when we need to create small files such as a settings file, avoiding to write and read this manualy.

### Example of use

```python
from syjson import SyJson
import time

syfile = SyJson("/path/to/file.json")
TIMEOUT = syfile.create("timeout_counter",1000)
RANGE_C = syfile.create("counter_range",[-100,100])
TO_PRINT = syfile.create("to_print",{"prefix":"","postfix":"num"})

if __name__ == "__main__":
    if TIMEOUT > 10:
        TIMEOUT.sync(10)
        print("Can't use a timeout > 10, timeout was setted to 10")
    if RANGE_C[0] < 0:
        RANGE_C[0] = 0
        print("Counter can't start from a negative value, start was setted to 0")
    if RANGE_C[0] > RANGE_C[1]:
        exit("Illegal values! Exiting")
    for i in range(RANGE_C[0].var(),RANGE_C[1].var()):
        print(TO_PRINT["prefix"].var(),i,TO_PRINT["postfix"].var())
        time.sleep(TIMEOUT.var())
"""
You can change in the json file the values during the execution,
values will change during the execution and modify the behavior of the cycle
"""
```

### How to Install

You can install this library using PyPi (pip)

###### Linux / Windows / MacOs

```bash
pip3 install syjson
```

This library is compatible with ujson module, you can inall ujson with:

```bash
pip3 install ujson
```

and the library will automaticaly use ujson module instead of python json module

### How to use

At first you can import SyJson class writing:

```python
from syjson import SyJson
```

now we can use this class for create/read a json file

```python
synced_json = SyJson(
    "file.json",           #Path of the json file
    create_file = True,    #If the file does not exists,
                           #this will automatically create that file
    pretty = None          #If setted to a number, the file will have an
                           #indentation of 'pretty' spaces
    get_primitives = False #non-iterable variables will be not return
                           #synced object but primitive python objects
)
```

the values setted previusly are setted by default except the path that is an obbligatory paramether.

After created SyJson object, we can start to use this object as it is a python dict. Every object readed and writed from SyJson object it's a subclass of SyJsonObj. This because every write or read from these variable will be readed/writed directly from the target file. The file is opened and closed at every operation, so no close function is needed to be called at the end of the use of this class.

---

There are some particular function added for particular use

#### --> synced_json.var()

With var function we can read from file the informations and we get a normal python object, so this python object have to be synced in a next step

#### --> synced_json.sync( value )

With sync function you can assign a variable and sync these informations in the target file

All SyJson object have these functionalityes

---

In dicts SyJsonObj there is an additional function that can be usefull in a lot of situation

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
