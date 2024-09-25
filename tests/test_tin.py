import pytest

from pysfcgal.sfcgal import MultiPolygon, Tin, Triangle


@pytest.fixture
def expected_triangles(c0, c1, c2, c3):
    yield [
        Triangle([c0, c1, c2]),
        Triangle([c0, c1, c3]),
        Triangle([c0, c2, c3]),
        Triangle([c1, c2, c3]),
    ]


@pytest.fixture
def tin_coordinates(c0, c1, c2, c3):
    yield [[c0, c1, c2], [c0, c1, c3], [c0, c2, c3], [c1, c2, c3]]


@pytest.fixture
def expected_multipolygon(c0, c1, c2, c3):
    yield MultiPolygon([[[c0, c1, c2]], [[c0, c1, c3]], [[c0, c2, c3]], [[c1, c2, c3]]])


@pytest.fixture
def tin(tin_coordinates):
    yield Tin(tin_coordinates)


@pytest.fixture
def tin_unclosed(c0, c1, c2, c3):
    yield Tin([[c0, c1, c2], [c0, c1, c3], [c0, c2, c3]])


@pytest.fixture
def tin_unordered(c0, c1, c2, c3):
    yield Tin([[c0, c1, c2], [c0, c1, c3], [c0, c2, c3]])


def test_tin(tin, expected_triangles, tin_unclosed, tin_unordered):
    assert len(tin) == 4
    # iteration
    for triangle, expected_triangle in zip(tin, expected_triangles):
        assert triangle == expected_triangle
    # indexing
    for idx in range(len(tin)):
        assert tin[idx] == expected_triangles[idx]
    assert tin[-1] == expected_triangles[-1]
    assert tin[1:3] == expected_triangles[1:3]
    # equality
    assert not tin_unclosed.is_valid()
    assert tin != tin_unclosed
    assert tin != tin_unordered


def test_tin_wkt(tin, tin_coordinates):
    assert tin.wktDecim(0) == (
        "TIN Z ("
        "((0 0 0,1 0 0,0 1 0,0 0 0)),"
        "((0 0 0,1 0 0,0 0 1,0 0 0)),"
        "((0 0 0,0 1 0,0 0 1,0 0 0)),"
        "((1 0 0,0 1 0,0 0 1,1 0 0)))"
    )
