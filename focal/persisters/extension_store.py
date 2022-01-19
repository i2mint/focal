from dol.trans import wrap_kvs
from py2store.stores.local_store import LocalBinaryStore

import numpy as np
import pickle
import json
from io import BytesIO
import pandas as pd
from functools import partial


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


def json_to_bytes(json, format='utf-8'):
    return bytes(json.dumps(json), format)


def array_to_bytes(arr: np.ndarray) -> bytes:
    np_bytes = BytesIO()
    np.save(np_bytes, arr)
    return np_bytes.getvalue()


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


def preset(k, v):
    if k.endswith('.csv'):
        return df_to_csv_bytes(v)

    if k.endswith('.xlsx'):
        return df_to_xlsx_bytes(v)

    if k.endswith('.p'):
        return obj_to_pickle_bytes(v)

    # def json_to_bytes(json, format='utf-8'):
    #     return bytes(json.dumps(json), format)

    if k.endswith('.json'):
        return bytes(json.dumps(v), 'utf-8')
        #return json_to_bytes(v)

    if k.endswith('.txt'):
        return string_to_bytes(v)

    if k.endswith('.npy'):
        return array_to_bytes(v)


def postget(k, v):
    if k.endswith('.csv'):
        return csv_bytes_to_df(v)

    if k.endswith('.xlsx'):
        return excel_bytes_to_df(v)

    if k.endswith('.p'):
        return pickle_bytes_to_obj(v)

    if k.endswith('.json'):
        return json_bytes_to_json(v)

    if k.endswith('.txt'):
        return text_byte_to_string(v)

    if k.endswith('.npy'):
        return bytes_to_array(v)


multi_extension_wrap = partial(wrap_kvs, postget=postget, preset=preset)
MultiFileStore = multi_extension_wrap(LocalBinaryStore)
