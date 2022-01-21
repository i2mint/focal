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

>>> my_df = pd.DataFrame({'A': [0, 1], 'B': [1, 6]})
>>> my_jdict = {'a': 1, 'b': [1, 2, 3], 'c': 'string'}
>>> my_string = 'test_string'
>>> my_array = np.random.random((10, 10))

Now we can save each of these in a relevant format:

>>> d['my_df.csv'] = my_df
>>> d['my_jdict.json'] = my_jdict
>>> d['my_string.txt'] = my_string
>>> d['my_array.npy'] = my_array

Our folder now contains those files

>>> assert set(listdir(temp_dir.name)) == {'my_df.csv', 'my_jdict.json', 'my_string.txt', 'my_array.npy'}

We can retrieve each one of those files and check that the python objects are equal to the originals

>>> assert d['my_df.csv'].equals(my_df)
>>> assert d['my_jdict.json'] == my_jdict
>>> assert d['my_string.txt'] == my_string
>>> assert np.array_equal(d['my_array.npy'], my_array)

Finally, we clean up the temporary folder

>>> temp_dir.cleanup()

"""

import pickle
import json
from io import BytesIO
from functools import partial

import pandas as pd
import numpy as np

from dol import wrap_kvs, Pipe
from py2store import LocalBinaryStore

# ---------------------------Object to bytes---------------------------------------------

string_to_bytes = str.encode
obj_to_pickle_bytes = pickle.dumps
jdict_to_bytes = Pipe(json.dumps, str.encode)


def df_to_csv_bytes(df: pd.DataFrame, format='utf-8', index=False):
    return bytes(df.to_csv(index=index), format)


def df_to_xlsx_bytes(df: pd.DataFrame, byte_to_file_func=BytesIO):
    towrite = byte_to_file_func()
    df.to_excel(towrite, index=False)
    towrite.seek(0)
    return towrite.getvalue()


def array_to_bytes(arr: np.ndarray) -> bytes:
    np_bytes = BytesIO()
    np.save(np_bytes, arr)
    return np_bytes.getvalue()


# ------------------------------Bytes to object------------------------------------------

csv_bytes_to_df = Pipe(BytesIO, pd.read_csv)
excel_bytes_to_df = Pipe(BytesIO, pd.read_excel)
pickle_bytes_to_obj = pickle.loads
json_bytes_to_json = json.loads
text_byte_to_string = bytes.decode
bytes_to_array = Pipe(BytesIO, np.load)

extensions_preset_postget = {
    'csv': {'preset': df_to_csv_bytes, 'postget': csv_bytes_to_df},
    'xlsx': {'preset': df_to_xlsx_bytes, 'postget': excel_bytes_to_df},
    'p': {'preset': obj_to_pickle_bytes, 'postget': pickle_bytes_to_obj},
    'json': {'preset': jdict_to_bytes, 'postget': json_bytes_to_json},
    'txt': {'preset': string_to_bytes, 'postget': text_byte_to_string},
    'npy': {'preset': array_to_bytes, 'postget': bytes_to_array},
}

import importlib


def add_package_dependent_extensions(
    imports=('numpy', 'pandas'),
    updates=(
        {'npy': {'preset': array_to_bytes, 'postget': bytes_to_array}},
        {
            'csv': {'preset': df_to_csv_bytes, 'postget': csv_bytes_to_df},
            'xlsx': {'preset': df_to_xlsx_bytes, 'postget': excel_bytes_to_df},
        },
    ),
):
    for module_name, update in zip(imports, updates):
        try:
            importlib.import_module(module_name)
            extensions_preset_postget.update(update)
        except Exception as E:
            print(f'Module {module_name} not found')
    return extensions_preset_postget


extensions_preset_postget = add_package_dependent_extensions()


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
