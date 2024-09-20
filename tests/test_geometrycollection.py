import pytest

from pysfcgal.sfcgal import GeometryCollection, LineString, Point, Polygon


@pytest.fixture
def expected_geometries(c0, c1, c2, c3):
    yield [Point(*c0), LineString([c1, c2, c3]), Polygon([c0, c1, c2])]


@pytest.fixture
def collection(expected_geometries):
    geom_collec = GeometryCollection()
    for geom in expected_geometries:
        geom_collec.addGeometry(geom)
    yield geom_collec


@pytest.fixture
def other_collection(expected_geometries):
    geom_collec = GeometryCollection()
    for _ in range(3):
        geom_collec.addGeometry(expected_geometries[0])
    yield geom_collec


@pytest.fixture
def collection_unordered(expected_geometries):
    geom_collec = GeometryCollection()
    for geom in expected_geometries[::-1]:
        geom_collec.addGeometry(geom)
    yield geom_collec


def test_geometry_collection_len(collection):
    assert len(collection) == 3


def test_geometry_collection_iteration(collection, expected_geometries):
    for geometry, expected_geometry in zip(collection, expected_geometries):
        assert geometry == expected_geometry


def test_geometry_collection_indexing(collection, expected_geometries):
    assert isinstance(collection[1], LineString)
    assert isinstance(collection[-1], Polygon)
    assert len(collection[:2]) == 2
    for idx in range(len(collection)):
        assert collection[idx] == expected_geometries[idx]
    assert collection[-1] == expected_geometries[-1]
    assert collection[1:3] == expected_geometries[1:3]


def test_geometry_collection_equality(
    collection, other_collection, collection_unordered
):
    assert collection != other_collection
    assert collection != collection_unordered
