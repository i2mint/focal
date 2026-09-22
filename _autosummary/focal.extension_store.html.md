# focal.extension_store

Stores that are extension-aware when reading and writing.

Make a temporary folder

```pycon
>>> import tempfile
>>> temp_dir = tempfile.TemporaryDirectory()
```

Check that it is empty for now

```pycon
>>> from os import  listdir
>>> listdir(temp_dir.name)
[]
```

Instantiate a store, persisting in our local temporary folder

```pycon
>>> d = MultiFileStore(temp_dir.name)
```

Here are a few objects to save into our folder:

```pycon
>>> my_jdict = {'a': 1, 'b': [1, 2, 3], 'c': 'string'}
>>> my_string = 'test_string'
```

Now we can save each of these in a relevant format:

```pycon
>>> d['my_jdict.json'] = my_jdict
>>> d['my_string.txt'] = my_string
```

Our folder now contains those∑ files

```pycon
>>> assert set(listdir(temp_dir.name)) == {'my_jdict.json', 'my_string.txt'}
```

We can retrieve each one of those files and check that the python objects are equal to the originals

```pycon
>>> assert d['my_jdict.json'] == my_jdict
>>> assert d['my_string.txt'] == my_string
```

Finally, we clean up the temporary folder

```pycon
>>> temp_dir.cleanup()
```

### Functions

| `get_extension`(k)                                |    |
|---------------------------------------------------|----|
| `make_conversion_for_obj`(k, v, ...[, func_type]) |    |

### Classes

| [`LocalBinaryStore`](#focal.extension_store.LocalBinaryStore)(path_format[, max_levels])   |    |
|------------------------------------------------------------------------------------------------|----|
| [`MultiFileStore`](#focal.extension_store.MultiFileStore)                                |    |

### *class* focal.extension_store.LocalBinaryStore(path_format, max_levels=None)

Bases: `Files`

### focal.extension_store.MultiFileStore

alias of [`LocalBinaryStore`](#focal.extension_store.LocalBinaryStore)

### focal.extension_store.string_to_bytes(self, , encoding='utf-8', errors='strict')

Encode the string using the codec registered for encoding.

encoding
: The encoding in which to encode the string.

errors
: The error handling scheme to use for encoding errors.
  The default is ‘strict’ meaning that encoding errors raise a
  UnicodeEncodeError.  Other possible values are ‘ignore’, ‘replace’ and
  ‘xmlcharrefreplace’ as well as any other name registered with
  codecs.register_error that can handle UnicodeEncodeErrors.

### focal.extension_store.text_byte_to_string(self, , encoding='utf-8', errors='strict')

Decode the bytes using the codec registered for encoding.

encoding
: The encoding with which to decode the bytes.

errors
: The error handling scheme to use for the handling of decoding errors.
  The default is ‘strict’ meaning that decoding errors raise a
  UnicodeDecodeError. Other possible values are ‘ignore’ and ‘replace’
  as well as any other name registered with codecs.register_error that
  can handle UnicodeDecodeErrors.
