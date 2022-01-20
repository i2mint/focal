"""Stores that are extension-aware when reading and writing.

TODO: A few doctest examples

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

# def string_to_bytes(s: str, format="utf-8"):
#     return bytes(s, format)

# def jdict_to_bytes(jdict, format='utf-8'):
#     return bytes(json.dumps(jdict), format)

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

# def preset(k, v):
#     extension = get_extension(k)
#     obj_to_byte = extensions_preset_postget[extension]['preset']
#
#     return obj_to_byte(v)
#
#
# def postget(k, v):
#     extension = get_extension(k)
#     byte_to_obj = extensions_preset_postget[extension]['postget']
#
#     return byte_to_obj(v)

multi_extension_wrap = partial(wrap_kvs, postget=postget, preset=preset)
MultiFileStore = multi_extension_wrap(LocalBinaryStore)