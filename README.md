
# focal
Data Access Objects for local files.

# Examples

## quick store

```pydocstring
>>> from py2store import QuickStore
>>>
>>> store = QuickStore()  # will print what (tmp) rootdir it is choosing
>>> # Write something and then read it out again
>>> store['foo'] = 'baz'
>>> 'foo' in store  # do you have the key 'foo' in your store?
True
>>> store['foo']  # what is the value for 'foo'?
'baz'
>>>
>>> # Okay, it behaves like a dict, but go have a look in your file system,  
>>> # and see that there is now a file in the rootdir, named 'foo'!
>>> 
>>> # Write something more complicated
>>> store['hello/world'] = [1, 'flew', {'over': 'a', "cuckoo's": map}]
>>> stored_val = store['hello/world']
>>> stored_val == [1, 'flew', {'over': 'a', "cuckoo's": map}]  # was it retrieved correctly?
True
>>>
>>> # how many items do you have now?
>>> assert len(store) >= 2  # can't be sure there were no elements before, so can't assert == 2
>>> 
>>> # delete the stuff you've written
>>> del store['foo']
>>> del store['hello/world']
```

## iterate over files

```pydocstring
>>> import os
>>> filepath = __file__  # path to this module
>>> dirpath = os.path.dirname(__file__)  # path of the directory where I (the module file) am
>>> s = FileCollection(dirpath, max_levels=0)
>>>
>>> files_in_this_dir = list(s)
>>> filepath in files_in_this_dir
True
```
##  bytes contents of the file

```pydocstring
>>> import os
>>> filepath = __file__
>>> dirpath = os.path.dirname(__file__)  # path of the directory where I (the module file) am
>>> s = FileBytesReader(dirpath, max_levels=0)
>>>
>>> ####### Get the first 9 characters (as bytes) of this module #####################
>>> s[filepath][:9]
b'import os'
>>>
>>> ####### Test key validation #####################
>>> s['not_a_valid_key']  # this key is not valid since not under the dirpath folder
Traceback (most recent call last):
    ...
filesys.KeyValidationError: 'Key not valid (usually because does not exist or access not permitted): not_a_valid_key'
>>>
>>> ####### Test further exceptions (that should be wrapped in KeyError) #####################
>>> # this key is valid, since under dirpath, but the file itself doesn't exist (hopefully for this test)
>>> non_existing_file = os.path.join(dirpath, 'non_existing_file')
>>> try:
...     s[non_existing_file]
... except KeyError:
...     print("KeyError (not FileNotFoundError) was raised.")
KeyError (not FileNotFoundError) was raised.
```
