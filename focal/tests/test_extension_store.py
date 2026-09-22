import pytest
from focal.extension_store import *

# test_df = pd.DataFrame({'A': [0, 1], 'B': [1, 6]})
test_json = {"a": 1, "b": [1, 2, 3], "c": "string"}
test_string = "test_string"
# test_array = np.random.random((10, 10))

# df_comparison = lambda obj, retrieved_df: obj.equals(retrieved_df)
basic_comparison = lambda obj, retrieved_obj: obj == retrieved_obj
# array_comparison = lambda obj, retrieved_obj: np.array_equal(obj, retrieved_obj)

test_tuples = (
    # (test_df, '.csv', df_comparison),
    # (test_df, '.xlsx', df_comparison),
    # (test_df, '.p', df_comparison),
    (test_json, ".json", basic_comparison),
    (test_string, ".txt", basic_comparison),
    # (test_array, '.npy', array_comparison),
)


@pytest.mark.parametrize(
    "object_to_test, extension_to_test, comparison_func", test_tuples
)
def test_store(
    object_to_test,
    extension_to_test,
    comparison_func,
    clean=True,
    filename="test",
):
    # make a temporary folder
    import tempfile

    temp_dir = tempfile.TemporaryDirectory()
    d = MultiFileStore(temp_dir.name)

    # name the file with the proper extension
    name_of_file = filename + extension_to_test
    # save the file
    d[name_of_file] = object_to_test
    # retrieve and compare to original
    retrieved = d[name_of_file]
    res_equl = comparison_func(retrieved, object_to_test)

    # delete the folder if needed
    if clean:
        temp_dir.cleanup()

    # complain if not the same, and see why it is not
    assert res_equl == True, (
        f"For {extension_to_test=}, saved and retrieved are not the same:"
        f" \n{retrieved=}"
        f"\n{object_to_test=}"
    )


def test_is_valid_key_agrees_with_iteration():
    """Regression test for i2mint/focal#5 (dol#83 key-delegation bug class).

    ``is_valid_key``/``validate_key`` must agree with what the store actually
    iterates and holds -- pins the i2mint/dol#85 fix (``mk_relative_path_store``
    installing key-mapping ``is_valid_key``/``validate_key``) against a future
    regression.
    """
    import tempfile

    d = MultiFileStore(tempfile.mkdtemp())
    d["x.json"] = {"a": 1}
    for k in d:
        assert d.is_valid_key(k), f"{k} is in the store but is_valid_key says no"
        d.validate_key(k)  # must not raise
