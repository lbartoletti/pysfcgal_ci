import pytest

from pysfcgal.sfcgal import LineString, MultiLineString


@pytest.fixture
def multilinestring(c0, c1, c2, c3):
    yield MultiLineString([[c0, c1], [c0, c2], [c0, c3]])


@pytest.fixture
def other_multilinestring(c0, c1, c2):
    yield MultiLineString([[c0, c1], [c0, c2]])


@pytest.fixture
def multilinestring_unordered(c0, c1, c2, c3):
    yield MultiLineString([[c0, c3], [c0, c1], [c0, c2]])


@pytest.fixture
def expected_linestrings(c0, c1, c2, c3):
    yield [LineString([c0, c1]), LineString([c0, c2]), LineString([c0, c3])]


def test_multilinestring_iteration(multilinestring, expected_linestrings):
    for linestring, expected_linestring in zip(multilinestring, expected_linestrings):
        assert linestring == expected_linestring


def test_multilinestring_indexing(multilinestring, expected_linestrings):
    for idx in range(len(multilinestring)):
        assert multilinestring[idx] == expected_linestrings[idx]
    assert multilinestring[-1] == expected_linestrings[-1]
    assert multilinestring[1:3] == expected_linestrings[1:3]


def test_multilinestring_equality(
    multilinestring, other_multilinestring, multilinestring_unordered
):
    assert multilinestring != other_multilinestring
    assert multilinestring != multilinestring_unordered  # the order is important
