import pytest

from pysfcgal.sfcgal import Point, Polygon, Triangle


@pytest.fixture
def triangle(c0, c1, c2):
    yield Triangle([c0, c1, c2])


@pytest.fixture
def triangle_2(c0, c1, c3):
    yield Triangle([c0, c1, c3])


@pytest.fixture
def triangle_unordered(c0, c1, c2):
    yield Triangle([c1, c2, c0])


@pytest.fixture
def expected_points(c0, c1, c2):
    yield [Point(*c0), Point(*c1), Point(*c2)]


@pytest.fixture
def expected_polygon(c0, c1, c2):
    yield Polygon([c0, c1, c2])


def test_triangle(triangle, expected_points, triangle_2, triangle_unordered):
    # iteration
    for point, expected_point in zip(triangle, expected_points):
        assert point == expected_point
    # indexing
    for idx in range(3):
        assert triangle[idx] == expected_points[idx]
    assert triangle[-1] == expected_points[-1]
    assert triangle[1:3] == expected_points[1:3]
    # equality
    assert triangle != triangle_2
    assert triangle != triangle_unordered
