"""Stores that are extension-aware when reading and writing.

Make a temporary folder

>>> import tempfile
>>> temp_dir = tempfile.TemporaryDirectory()

Check that it is empty for now

>>> from os import  listdir
>>> listdir(temp_dir.name)
[]

Instantiate a store, persisting in our local temporary folder

>>> d = MultiFileStore(temp_dir.name)

Here are a few objects to save into our folder:

>>> my_jdict = {'a': 1, 'b': [1, 2, 3], 'c': 'string'}
>>> my_string = 'test_string'

Now we can save each of these in a relevant format:

>>> d['my_jdict.json'] = my_jdict
>>> d['my_string.txt'] = my_string

Our folder now contains those∑ files

>>> assert set(listdir(temp_dir.name)) == {'my_jdict.json', 'my_string.txt'}

We can retrieve each one of those files and check that the python objects are equal to the originals

>>> assert d['my_jdict.json'] == my_jdict
>>> assert d['my_string.txt'] == my_string

Finally, we clean up the temporary folder

>>> temp_dir.cleanup()

"""
import os
import pickle
import json
from io import BytesIO
from functools import partial
from contextlib import suppress

from dol import wrap_kvs, Pipe
from dol.filesys import Files


# TODO: Empty {} do not work, fix that
class LocalBinaryStore(Files):
    def __init__(self, path_format, max_levels=None):
        dirs = path_format.split(os.sep)

        first_bracket_idx = None
        for idx, dir in enumerate(dirs):
            if (
                '{' in dir
            ):  # TODO: Replace that hack, may be using regex or string.Formatter
                first_bracket_idx = idx
                break

        if first_bracket_idx is not None:
            rootdir = os.sep.join(dirs[:first_bracket_idx])
            subpath = os.sep.join(dirs[first_bracket_idx:])

        else:
            rootdir = path_format
            subpath = ''

        super().__init__(rootdir=rootdir, subpath=subpath, max_levels=max_levels)


# ---------------------------Object to bytes---------------------------------------------------------------------------

string_to_bytes = str.encode
obj_to_pickle_bytes = pickle.dumps
jdict_to_bytes = Pipe(json.dumps, str.encode)

# ------------------------------Bytes to object------------------------------------------------------------------------

pickle_bytes_to_obj = pickle.loads
json_bytes_to_json = json.loads
text_byte_to_string = bytes.decode

extensions_preset_postget = {
    'p': {'preset': obj_to_pickle_bytes, 'postget': pickle_bytes_to_obj},
    'json': {'preset': jdict_to_bytes, 'postget': json_bytes_to_json},
    'txt': {'preset': string_to_bytes, 'postget': text_byte_to_string},
}

# ------------------------------Extra extensions, added only if needed package are found--------------------------------


with suppress(ModuleNotFoundError):
    import numpy as np

    def array_to_bytes(arr: np.ndarray) -> bytes:
        np_bytes = BytesIO()
        np.save(np_bytes, arr)
        return np_bytes.getvalue()

    bytes_to_array = Pipe(BytesIO, np.load)
    extensions_preset_postget.update(
        {'npy': {'preset': array_to_bytes, 'postget': bytes_to_array}}
    )

with suppress(ModuleNotFoundError):
    import pandas as pd

    def df_to_csv_bytes(df: pd.DataFrame, format='utf-8', index=False):
        return bytes(df.to_csv(index=index), format)

    def df_to_xlsx_bytes(df: pd.DataFrame, byte_to_file_func=BytesIO):
        towrite = byte_to_file_func()
        df.to_excel(towrite, index=False)
        towrite.seek(0)
        return towrite.getvalue()

    csv_bytes_to_df = Pipe(BytesIO, pd.read_csv)
    excel_bytes_to_df = Pipe(BytesIO, pd.read_excel)
    extensions_preset_postget.update(
        {
            'xlsx': {'preset': df_to_xlsx_bytes, 'postget': excel_bytes_to_df},
            'csv': {'preset': df_to_csv_bytes, 'postget': csv_bytes_to_df},
        }
    )


def get_extension(k):
    return k.split('.')[-1]


def make_conversion_for_obj(k, v, extensions_preset_postget, func_type='preset'):
    extension = get_extension(k)
    conv_func = extensions_preset_postget[extension][func_type]
    return conv_func(v)


postget = partial(
    make_conversion_for_obj,
    extensions_preset_postget=extensions_preset_postget,
    func_type='postget',
)
preset = partial(
    make_conversion_for_obj,
    extensions_preset_postget=extensions_preset_postget,
    func_type='preset',
)

multi_extension_wrap = partial(wrap_kvs, postget=postget, preset=preset)
MultiFileStore = multi_extension_wrap(LocalBinaryStore)
