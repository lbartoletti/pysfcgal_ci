import pytest

from pysfcgal.sfcgal import GeometryCollection, LineString, Point, Polygon


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
def point_in_poly():
    yield Point(2., 3.)


@pytest.fixture
def polygon1(ext_ring1):
    yield Polygon(ext_ring1)


@pytest.fixture
def polygon2(ext_ring2):
    yield Polygon(ext_ring2)


@pytest.fixture
def polygon_with_hole(ext_ring1, int_ring1, int_ring2):
    yield Polygon(exterior=ext_ring1, interiors=[int_ring1, int_ring2])


@pytest.fixture
def polygon_with_hole_unclosed(ext_ring1, int_ring1, int_ring2):
    yield Polygon(exterior=ext_ring1[:-1], interiors=[int_ring1[:-1], int_ring2[:-1]])


@pytest.fixture
def linestring1(ext_ring1):
    yield LineString(ext_ring1)


@pytest.fixture
def linestring2(int_ring1):
    yield LineString(int_ring1)


@pytest.fixture
def linestring3(int_ring2):
    yield LineString(int_ring2)


def test_polygon_rings(polygon_with_hole, linestring1, linestring2, linestring3):
    # exterior ring
    assert polygon_with_hole.exterior == linestring1
    # interior rings
    assert polygon_with_hole.n_interiors == 2
    assert polygon_with_hole.interiors == [linestring2, linestring3]
    assert polygon_with_hole.rings == [linestring1, linestring2, linestring3]


def test_polygon_iteration(polygon_with_hole, linestring1, linestring2, linestring3):
    for line, ring in zip([linestring1, linestring2, linestring3], polygon_with_hole):
        assert line == ring


def test_polygon_indexing(polygon_with_hole, linestring1, linestring2, linestring3):
    assert polygon_with_hole[0] == linestring1
    assert polygon_with_hole[1] == linestring2
    assert polygon_with_hole[-1] == linestring3
    assert polygon_with_hole[:] == [linestring1, linestring2, linestring3]
    assert polygon_with_hole[-1:-3:-1] == [linestring3, linestring2]


def test_polygon_equality(polygon_with_hole, polygon1, polygon_with_hole_unclosed):
    assert polygon_with_hole == polygon_with_hole_unclosed
    assert polygon_with_hole != polygon1


def test_point_in_polygon(point_in_poly, polygon1, polygon2):
    """Tests the intersection between a point and a polygon"""
    point = Point(2, 3)
    assert polygon1.intersects(point)
    assert point.intersects(polygon1)
    assert not polygon2.intersects(point)
    assert not point.intersects(polygon2)
    result = point.intersection(polygon1)
    assert isinstance(result, Point)
    assert not result.is_empty
    assert result.x == point.x
    assert result.y == point.y
    result = point.intersection(polygon2)
    assert isinstance(result, GeometryCollection)
    assert result.is_empty


def test_intersection_polygon_polygon(polygon1, polygon2):
    """Tests the intersection between two polygons"""
    assert polygon1.intersects(polygon2)
    assert polygon2.intersects(polygon1)
    polygon3 = polygon1.intersection(polygon2)
    assert polygon3.area == 1.0
    # TODO: check coordinates
