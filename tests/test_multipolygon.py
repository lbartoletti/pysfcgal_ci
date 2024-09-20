import pytest

from pysfcgal.sfcgal import MultiPolygon, Polygon


@pytest.fixture
def ext_ring1():
    yield [(0., 0.), (10., 0.), (10., 10.), (0., 10.), (0., 0.)]


@pytest.fixture
def ext_ring2():
    yield [(-1., -1.), (1., -1.), (1., 1.), (-1., 1.), (-1., -1.)]


@pytest.fixture
def int_ring1():
    yield [(2., 2.), (3., 2.), (3., 3.), (2., 2.)]


@pytest.fixture
def int_ring2():
    yield [(5., 5.), (5., 6.), (6., 6.), (5., 5.)]


@pytest.fixture
def multipolygon(ext_ring1, int_ring1, int_ring2):
    yield MultiPolygon([[ext_ring1], [int_ring1], [int_ring2]])


@pytest.fixture
def other_multipolygon(ext_ring1, int_ring1, ext_ring2):
    yield MultiPolygon([[ext_ring1], [int_ring1], [ext_ring2]])


@pytest.fixture
def multipolygon_unordered(ext_ring1, int_ring1, int_ring2):
    yield MultiPolygon([[int_ring2], [ext_ring1], [int_ring1]])


@pytest.fixture
def expected_polygons(ext_ring1, int_ring1, int_ring2):
    yield [Polygon(ext_ring1), Polygon(int_ring1), Polygon(int_ring2)]


def test_multipolygon_iteration(multipolygon, expected_polygons):
    for polygon, expected_polygon in zip(multipolygon, expected_polygons):
        assert polygon == expected_polygon


def test_multipolygon_indexing(multipolygon, expected_polygons):
    for idx in range(len(multipolygon)):
        assert multipolygon[idx] == expected_polygons[idx]
    assert multipolygon[-1] == expected_polygons[-1]
    assert multipolygon[1:3] == expected_polygons[1:3]


def test_multipolygon_equality(
    multipolygon, other_multipolygon, multipolygon_unordered
):
    assert multipolygon != other_multipolygon
    assert multipolygon != multipolygon_unordered  # the order is important
