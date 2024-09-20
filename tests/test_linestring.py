import pytest

from pysfcgal.sfcgal import LineString


@pytest.fixture
def line(c0, c1, c2):
    yield LineString([c0, c1, c2])


@pytest.fixture
def line2(c0, c1, c3):
    yield LineString([c0, c1, c3])


@pytest.fixture
def long_line(c0, c1, c2, c3):
    yield LineString([c0, c1, c2, c3])


@pytest.mark.parametrize(
    "linestring,expected_length", [("line", 4), ("long_line", 9)],
)
def test_linestring_len(linestring, expected_length):
    assert len(linestring) == expected_length


def test_linestring_eq(line, line2):
    assert line != line2
    assert line != line2[:-1]
    assert line[:-1] == line2[:-1]


def test_linestring_getter(line):
    # Indexing with a wrong type
    with pytest.raises(TypeError):
        _ = line["cant-index-with-a-string"]
    # Positive indexing
    for idx, p in enumerate(line):
        assert line[idx] == p
    with pytest.raises(IndexError):
        _ = line[99]
    # Negative indexing
    for idx, p in enumerate(reversed(line)):
        assert line[-(idx + 1)] == p
    with pytest.raises(IndexError):
        _ = line[-99]
    # Slicing
    start_index = 1
    points = line[start_index:start_index+2]
    for idx, p in enumerate(points):
        assert p == line[start_index+idx]
