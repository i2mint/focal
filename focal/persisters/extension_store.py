from dol.trans import wrap_kvs
from py2store.stores.local_store import LocalBinaryStore

import numpy as np
import pickle
import json
from io import BytesIO
import pandas as pd
from functools import partial


#-------------------------------------------------Object to bytes-------------------------------------------------------

def df_to_csv_bytes(df: pd.DataFrame, format='utf-8', index=False):
    return bytes(df.to_csv(index=index), format)


def df_to_xlsx_bytes(df: pd.DataFrame, byte_to_file_func=BytesIO):
    towrite = byte_to_file_func()
    df.to_excel(towrite, index=False)
    towrite.seek(0)
    return towrite.getvalue()


def string_to_bytes(s: str, format='utf-8'):
    return bytes(s, format)


def obj_to_pickle_bytes(obj):
    return pickle.dumps(obj)


def jdict_to_bytes(jdict, format='utf-8'):
    return bytes(json.dumps(jdict), format)


def array_to_bytes(arr: np.ndarray) -> bytes:
    np_bytes = BytesIO()
    np.save(np_bytes, arr)
    return np_bytes.getvalue()

#-------------------------------------------------Bytes to Object-------------------------------------------------------


def csv_bytes_to_df(b: bytes):
    return pd.read_csv(BytesIO(b))


def excel_bytes_to_df(b: bytes):
    return pd.read_excel(BytesIO(b))


def pickle_bytes_to_obj(b: bytes):
    return pickle.loads(b)


def json_bytes_to_json(b: bytes):
    return json.loads(b)


def text_byte_to_string(b: bytes, format="utf-8"):
    return b.decode(format)


def bytes_to_array(b: bytes) -> np.ndarray:
    np_bytes = BytesIO(b)
    return np.load(np_bytes)


extensions_preset_postget = {'csv': {'preset': df_to_csv_bytes, 'postget': csv_bytes_to_df},
                             'xlsx': {'preset': df_to_xlsx_bytes, 'postget': excel_bytes_to_df},
                             'p': {'preset': obj_to_pickle_bytes, 'postget': pickle_bytes_to_obj},
                             'json': {'preset': jdict_to_bytes, 'postget': json_bytes_to_json},
                             'txt': {'preset': string_to_bytes, 'postget': text_byte_to_string},
                             'npy': {'preset': array_to_bytes, 'postget': bytes_to_array}}


def get_extension(k):
    return k.split('.')[-1]

def make_conversion_for_obj(k, v, extensions_preset_postget, func_type='preset'):
    extension = get_extension(k)
    conv_func = extensions_preset_postget[extension][func_type]
    return conv_func(v)

postget = partial(make_conversion_for_obj, extensions_preset_postget=extensions_preset_postget, func_type='postget')
preset = partial(make_conversion_for_obj, extensions_preset_postget=extensions_preset_postget, func_type='preset')

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
