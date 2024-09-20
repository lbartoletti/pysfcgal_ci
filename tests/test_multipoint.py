import pytest

from pysfcgal.sfcgal import MultiPoint, Point


@pytest.fixture
def multipoint(c0, c1, c2):
    yield MultiPoint((c0, c1, c2))


@pytest.fixture
def other_multipoint(c1, c2, c3):
    yield MultiPoint((c1, c2, c3))


@pytest.fixture
def multipoint_unordered(c0, c1, c2):
    yield MultiPoint((c1, c2, c0))


@pytest.fixture
def expected_points(c0, c1, c2):
    yield [Point(*c0), Point(*c1), Point(*c2)]


def test_multipoint_iteration(multipoint, expected_points):
    for point, expected_point in zip(multipoint, expected_points):
        assert point == expected_point


def test_multipoint_indexing(multipoint, expected_points):
    for idx in range(len(multipoint)):
        assert multipoint[idx] == expected_points[idx]
    assert multipoint[-1] == expected_points[-1]
    assert multipoint[1:3] == expected_points[1:3]


def test_multipoint_equality(multipoint, other_multipoint, multipoint_unordered):
    assert multipoint != other_multipoint
    assert multipoint[1:] == other_multipoint[:2]
    # the point order is important (be compliant with other GIS softwares)
    assert multipoint != multipoint_unordered
