import pytest

from pysfcgal.sfcgal import Polygon, PolyhedralSurface


@pytest.fixture
def polyhedralsurface(c0, c1, c2, c3):
    yield PolyhedralSurface(
        [[[c0, c1, c2]], [[c0, c1, c3]], [[c0, c2, c3]], [[c1, c2, c3]]]
    )


@pytest.fixture
def other_polyhedralsurface(c0, c1, c2, c3):
    yield PolyhedralSurface(
        [[[c0, c1, c2]], [[c0, c1, c3]], [[c0, c2, c3]]]
    )


@pytest.fixture
def polyhedralsurface_unordered(c0, c1, c2, c3):
    yield PolyhedralSurface(
        [[[c1, c2, c3]], [[c0, c1, c2]], [[c0, c1, c3]], [[c0, c2, c3]]]
    )


@pytest.fixture
def expected_polygons(c0, c1, c2, c3):
    yield [
        Polygon([c0, c1, c2]),
        Polygon([c0, c1, c3]),
        Polygon([c0, c2, c3]),
        Polygon([c1, c2, c3]),
    ]


def test_polyhedralsurface_len(polyhedralsurface):
    assert len(polyhedralsurface) == 4


def test_polyhedralsurface_iteration(polyhedralsurface, expected_polygons):
    for polygon, expected_polygon in zip(polyhedralsurface, expected_polygons):
        assert polygon == expected_polygon


def test_polyhedralsurface_indexing(polyhedralsurface, expected_polygons):
    for idx in range(len(polyhedralsurface)):
        assert polyhedralsurface[idx] == expected_polygons[idx]
    assert polyhedralsurface[-1] == expected_polygons[-1]
    assert polyhedralsurface[1:3] == expected_polygons[1:3]


def test_polyhedralsurface_equality(
    polyhedralsurface, other_polyhedralsurface, polyhedralsurface_unordered
):
    assert not other_polyhedralsurface.is_valid()
    assert polyhedralsurface != other_polyhedralsurface
    assert polyhedralsurface != polyhedralsurface_unordered
