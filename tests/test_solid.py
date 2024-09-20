import itertools

import pytest

from pysfcgal.sfcgal import (PolyhedralSurface, Solid,
                             solid_to_polyhedralsurface)


def from_point_list_to_cube_coordinates(points):
    return [
        [
            [points[0], points[2], points[6], points[4], points[0]]
        ],  # bottom face
        [
            [points[1], points[5], points[7], points[3], points[1]]
        ],  # up face
        [
            [points[0], points[1], points[3], points[2], points[0]]
        ],  # left face
        [
            [points[2], points[3], points[7], points[6], points[2]]
        ],  # front face
        [
            [points[6], points[7], points[5], points[4], points[6]]
        ],  # right face
        [
            [points[4], points[5], points[1], points[0], points[4]]
        ],  # back face
    ]


def create_cube_coordinates(min_val=0, max_val=1):
    return from_point_list_to_cube_coordinates(
        [
            point_coord
            for point_coord
            in itertools.product((min_val, max_val), repeat=3)
        ]
    )


@pytest.fixture
def points_ext():
    yield create_cube_coordinates(0., 10.)


@pytest.fixture
def points_int_1():
    yield create_cube_coordinates(2., 3.)


@pytest.fixture
def points_int_2():
    yield create_cube_coordinates(6., 8.)


@pytest.fixture
def expected_polyhedralsurfaces(points_ext, points_int_1, points_int_2):
    yield [
        PolyhedralSurface(points_ext),
        PolyhedralSurface(points_int_1),
        PolyhedralSurface(points_int_2),
    ]


@pytest.fixture
def composed_polyhedralsurface(points_ext, points_int_1, points_int_2):
    yield PolyhedralSurface(points_ext + points_int_1 + points_int_2)


@pytest.fixture
def solid(points_ext, points_int_1, points_int_2):
    yield Solid([points_ext, points_int_1, points_int_2])


@pytest.fixture
def solid_without_holes(points_ext):
    yield Solid([points_ext])


@pytest.fixture
def solid_unordered(points_ext, points_int_1, points_int_2):
    yield Solid([points_ext, points_int_2, points_int_1])


def test_solid(
    solid, expected_polyhedralsurfaces, solid_without_holes, solid_unordered
):
    assert solid.n_shells == 3
    # iteration
    for shell, expected_polyhedral in zip(solid, expected_polyhedralsurfaces):
        assert shell == expected_polyhedral
    # indexing
    for idx in range(solid.n_shells):
        solid[idx] == expected_polyhedralsurfaces[idx]
    solid[-1] == expected_polyhedralsurfaces[-1]
    solid[1:3] == expected_polyhedralsurfaces[1:3]
    # equality
    assert solid != solid_without_holes
    assert solid != solid_unordered


def test_solid_to_polyhedralsurface_deprecated(solid, composed_polyhedralsurface):
    with pytest.warns(DeprecationWarning):
        phs = solid_to_polyhedralsurface(solid._geom, wrapped=True)
    assert not phs.is_valid()  # PolyhedralSurface with interior shells
    assert phs.geom_type == "PolyhedralSurface"
    assert phs == composed_polyhedralsurface


def test_solid_to_polyhedralsurface(solid, composed_polyhedralsurface):
    phs = solid.to_polyhedralsurface(wrapped=True)
    assert not phs.is_valid()  # PolyhedralSurface with interior shells
    assert phs.geom_type == "PolyhedralSurface"
    assert phs == composed_polyhedralsurface
