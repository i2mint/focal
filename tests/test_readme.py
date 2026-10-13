"""The README examples are real: run them as doctests."""

import doctest
import pathlib

README = pathlib.Path(__file__).parent.parent / "README.md"


def test_readme_examples():
    result = doctest.testfile(
        str(README),
        module_relative=False,
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
    )
    assert result.attempted > 0
    assert result.failed == 0
