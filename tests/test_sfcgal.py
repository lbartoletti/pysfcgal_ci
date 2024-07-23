import pathlib

import pytest

import pysfcgal.sfcgal as sfcgal
from pysfcgal.sfcgal import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    PolyhedralSurface,
    Solid,
    Tin,
    Triangle,
)
from filecmp import cmp
import geom_data


def test_version():
    print(sfcgal.sfcgal_version())


geometry_names, geometry_values = zip(*geom_data.data.items())


@pytest.mark.parametrize("geometry", geometry_values, ids=geometry_names)
def test_integrity(geometry):
    """Test conversion from and to GeoJSON-like data"""
    geom = sfcgal.shape(geometry)
    data = sfcgal.mapping(geom)
    assert geometry == data


@pytest.mark.parametrize("geometry", geometry_values, ids=geometry_names)
def test_wkt_write(geometry):
    geom = sfcgal.shape(geometry)
    wkt = geom.wkt
    assert wkt
    data = sfcgal.mapping(sfcgal.read_wkt(wkt))
    assert geometry == data


def test_wkt_read():
    good_wkt = "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))"
    geom = sfcgal.read_wkt(good_wkt)
    assert geom.__class__ == Polygon

    good_wkt = "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0),)"
    geom = sfcgal.read_wkt(good_wkt)
    assert geom.__class__ == GeometryCollection


def test_wkt_str():
    good_wkt = "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))"
    geom = sfcgal.read_wkt(good_wkt)
    assert str(geom) == "POLYGON((0.00000000 0.00000000,0.00000000 1.00000000,1.00000000 1.00000000,1.00000000 0.00000000,0.00000000 0.00000000))"  # noqa: E501


def test_wkb_write():
    point = Point(0, 1)
    wkb = point.hexwkb
    expected_wkb = "01010000000000000000000000000000000000f03f"
    assert wkb == expected_wkb

    mp = sfcgal.Polygon([(0, 0), (0, 5), (5, 5), (5, 0), (0, 0)])
    wkb = mp.hexwkb
    expected_wkb = '010300000001000000050000000000000000000000000000000000000000000000000000000000000000001440000000000000144000000000000014400000000000001440000000000000000000000000000000000000000000000000'  # noqa: E501
    assert wkb == expected_wkb

    expected_wkb = '\x01\x03\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa: E501
    wkb = mp.wkb.decode("utf-8")
    assert wkb == expected_wkb


def test_wkb_read():
    wkb_expected = "01020000000300000000000000000000000000000000000000000000000000f03f000000000000f03f00000000000000400000000000000040"  # noqa: E501
    wkt_expected = "LINESTRING(0.0 0.0,1.0 1.0,2.0 2.0)"

    ls = sfcgal.read_wkt(wkt_expected)
    ls.hexwkb == wkb_expected

    # Special case for EWKB
    # TODO: get srid from PreparedGeometry
    ewkb_ls = "01020000206a0f00000300000000000000000000000000000000000000000000000000f03f000000000000f03f00000000000000400000000000000040"  # noqa: E501
    ls = sfcgal.read_wkb(ewkb_ls)
    ls.hexwkb == wkb_expected


def test_point_in_polygon():
    """Tests the intersection between a point and a polygon"""
    point = Point(2, 3)
    polygon1 = Polygon([(0, 0), (5, 0), (5, 5), (0, 5), (0, 0)])
    polygon2 = Polygon([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)])
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


def test_intersection_polygon_polygon():
    """Tests the intersection between two polygons"""
    polygon1 = Polygon([(0, 0), (5, 0), (5, 5), (0, 5), (0, 0)])
    polygon2 = Polygon([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)])
    assert polygon1.intersects(polygon2)
    assert polygon2.intersects(polygon1)
    polygon3 = polygon1.intersection(polygon2)
    assert polygon3.area == 1.0
    # TODO: check coordinates


def test_point():
    point1 = Point(4, 5, 6)
    assert point1.x == 4.0
    assert point1.y == 5.0
    assert point1.z == 6.0
    assert point1.has_z
    assert not point1.has_m

    point2 = Point(4, 5)
    assert point2.x == 4.0
    assert point2.y == 5.0
    assert not point2.has_z
    assert not point2.has_m
    assert not point2 == point1

    point3 = Point(4, 5, 6, 7)
    assert point3.x == 4.0
    assert point3.y == 5.0
    assert point3.z == 6.0
    assert point3.m == 7.0
    assert point3.has_z
    assert point3.has_m
    assert not point3 == point1
    assert not point3 == point2

    pointm = Point(4, 5, m=7)
    assert pointm.x == 4.0
    assert pointm.y == 5.0
    assert pointm.m == 7.0
    assert not pointm.has_z
    assert pointm.has_m
    assert not pointm == point1
    assert not pointm == point2
    assert not pointm == point3

    pointz = Point(4, 5, z=6)
    assert pointz.x == 4.0
    assert pointz.y == 5.0
    assert pointz.z == 6.0
    assert pointz.has_z
    assert not pointz.has_m
    assert point1 == pointz


def test_line_string():
    line = LineString([(0, 0), (0, 1), (1, 1.5), (1, 2)])
    assert len(line) == 4

    # test access to coordinates
    coords = line.coords
    assert len(coords) == 4
    assert coords[0] == (0.0, 0.0)
    assert coords[-1] == (1.0, 2.0)
    assert coords[0:2] == [(0.0, 0.0), (0.0, 1.0)]


def test_linestring_eq():
    line1 = LineString([(0, 0), (0, 1), (1, 1.5), (1, 2)])
    line2 = LineString([(0, 0), (0, 1), (1, 1.5), (1, 3)])
    assert line1 != line2
    assert line1 != line2[:-1]
    assert line1[:-1] == line2[:-1]


def test_linestring_getter():
    line = LineString([(0, 0), (0, 1), (1, 1.5), (1, 2)])
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


def test_polygon():
    c0 = [(0, 0), (10, 0), (0, 10), (10, 10), (0, 0)]
    c1 = [(2, 2), (3, 2), (3, 3), (2, 2)]
    c2 = [(5, 5), (5, 6), (6, 6), (5, 5)]
    polygon = Polygon(exterior=c0, interiors=[c1, c2])
    # exterior ring
    l0 = LineString(c0)
    assert polygon.exterior == l0
    # interior rings
    l1 = LineString(c1)
    l2 = LineString(c2)
    assert polygon.n_interiors == 2
    assert polygon.interiors == [l1, l2]
    assert polygon.rings == [l0, l1, l2]
    # iteration
    for line, ring in zip([l0, l1, l2], polygon):
        assert line == ring
    # indexing
    assert polygon[0] == l0
    assert polygon[1] == l1
    assert polygon[-1] == l2
    assert polygon[:] == [l0, l1, l2]
    assert polygon[-1:-3:-1] == [l2, l1]
    # closed rings / polygon equality
    polygon_with_unclosed_lists = Polygon(
        exterior=c0[:-1], interiors=[c1[:-1], c2[:-1]]
    )
    assert polygon == polygon_with_unclosed_lists
    polygon_without_hole = Polygon(c0)
    assert polygon != polygon_without_hole


def test_multipoint():
    mp1 = MultiPoint(((0, 0), (1, 1), (0, 1)))
    pts = [Point(0, 0), Point(1, 1), Point(0, 1)]
    # iteration
    for point, expected_point in zip(mp1, pts):
        assert point == expected_point
    # indexing
    for idx in range(len(mp1)):
        assert mp1[idx] == pts[idx]
    assert mp1[-1] == pts[-1]
    assert mp1[1:3] == pts[1:3]
    # equality
    mp2 = MultiPoint(((1, 1), (0, 1), (1, 0)))
    assert mp1 != mp2
    assert mp1[1:] == mp2[:2]
    mp3 = MultiPoint(((1, 1), (0, 1), (0, 0)))
    # the point order is important (be compliant with other GIS softwares)
    assert mp1 != mp3


def test_multilinestring():
    c0 = [(0, 0), (1, 1)]
    c1 = [(2, 2), (3, 3)]
    c2 = [(-2, -2), (-1, -1)]
    ml1 = MultiLineString([c0, c1, c2])
    linestrings = [LineString(c0), LineString(c1), LineString(c2)]
    # iteration
    for linestring, expected_linestring in zip(ml1, linestrings):
        assert linestring == expected_linestring
    # indexing
    for idx in range(len(ml1)):
        assert ml1[idx] == linestrings[idx]
    assert ml1[-1] == linestrings[-1]
    assert ml1[1:3] == linestrings[1:3]
    # equality
    ml2 = MultiLineString([c2, c0])
    assert ml1 != ml2
    ml3 = MultiLineString([c2, c0, c1])
    assert ml1 != ml3  # the order is important


def test_multipolygon():
    c0 = [(0, 0), (10, 0), (0, 10), (10, 10), (0, 0)]
    c1 = [(2, 2), (3, 2), (3, 3), (2, 2)]
    c2 = [(5, 5), (5, 6), (6, 6), (5, 5)]
    mp1 = MultiPolygon([[c0], [c1], [c2]])
    polygons = [Polygon(c0), Polygon(c1), Polygon(c2)]
    # iteration
    for polygon, expected_polygon in zip(mp1, polygons):
        assert polygon == expected_polygon
    # indexing
    for idx in range(len(mp1)):
        assert mp1[idx] == polygons[idx]
    assert mp1[-1] == polygons[-1]
    assert mp1[1:3] == polygons[1:3]
    # equality
    mp2 = MultiPolygon([[c1], [c2]])
    assert mp1 != mp2
    mp3 = MultiPolygon([[c2], [c0], [c1]])
    assert mp1 != mp3  # the order is important


def test_polyhedralsurface():
    p0 = (0, 0, 0)
    p1 = (1, 0, 0)
    p2 = (0, 1, 0)
    p3 = (0, 0, 1)
    polys = [
        Polygon([p0, p1, p2]),
        Polygon([p0, p1, p3]),
        Polygon([p0, p2, p3]),
        Polygon([p1, p2, p3]),
    ]
    phs = PolyhedralSurface(
        [[[p0, p1, p2]], [[p0, p1, p3]], [[p0, p2, p3]], [[p1, p2, p3]]]
    )
    assert len(phs) == 4
    # iteration
    for polygon, expected_polygon in zip(phs, polys):
        assert polygon == expected_polygon
    # indexing
    for idx in range(len(phs)):
        assert phs[idx] == polys[idx]
    assert phs[-1] == polys[-1]
    assert phs[1:3] == polys[1:3]
    # equality
    phs2 = PolyhedralSurface([[[p0, p1, p2]], [[p0, p1, p3]], [[p0, p2, p3]]])
    assert not phs2.is_valid()
    assert phs != phs2
    phs3 = PolyhedralSurface(
        [[[p1, p2, p3]], [[p0, p1, p2]], [[p0, p1, p3]], [[p0, p2, p3]]]
    )
    assert phs != phs3


def from_point_list_to_polyhedral_surface_coordinates(points):
    return [
        [
            [points[0], points[1], points[6], points[2]]
        ],
        [
            [points[0], points[3], points[5], points[1]]
        ],
        [
            [points[6], points[2], points[4], points[7]]
        ],
        [
            [points[3], points[5], points[7], points[4]]
        ],
        [
            [points[0], points[2], points[4], points[3]]
        ],
        [
            [points[1], points[6], points[7], points[5]]
        ],
    ]


def test_solid():
    points_ext = [
        (0, 0, 0),
        (10, 0, 0),
        (0, 10, 0),
        (0, 0, 10),
        (0, 10, 10),
        (10, 0, 10),
        (10, 10, 0),
        (10, 10, 10),
    ]
    points_int_1 = [
        (2, 2, 2),
        (3, 2, 2),
        (2, 3, 2),
        (2, 2, 3),
        (2, 3, 3),
        (3, 2, 3),
        (3, 3, 2),
        (3, 3, 3),
    ]
    points_int_2 = [
        (6, 6, 6),
        (8, 6, 6),
        (6, 8, 6),
        (6, 6, 8),
        (6, 8, 8),
        (8, 6, 8),
        (8, 8, 6),
        (8, 8, 8),
    ]
    polyhedrals = [
        PolyhedralSurface(
            from_point_list_to_polyhedral_surface_coordinates(points_ext)
        ),
        PolyhedralSurface(
            from_point_list_to_polyhedral_surface_coordinates(points_int_1)
        ),
        PolyhedralSurface(
            from_point_list_to_polyhedral_surface_coordinates(points_int_2)
        ),
    ]
    solid = Solid(
        [
            from_point_list_to_polyhedral_surface_coordinates(points_ext),
            from_point_list_to_polyhedral_surface_coordinates(points_int_1),
            from_point_list_to_polyhedral_surface_coordinates(points_int_2),
        ]
    )
    assert solid.n_shells == 3
    # iteration
    for shell, expected_polyhedral in zip(solid, polyhedrals):
        assert shell == expected_polyhedral
    # indexing
    for idx in range(solid.n_shells):
        solid[idx] == polyhedrals[idx]
    solid[-1] == polyhedrals[-1]
    solid[1:3] == polyhedrals[1:3]
    # equality
    solid2 = Solid([from_point_list_to_polyhedral_surface_coordinates(points_ext)])
    assert solid != solid2
    solid3 = Solid(
        [
            from_point_list_to_polyhedral_surface_coordinates(points_ext),
            from_point_list_to_polyhedral_surface_coordinates(points_int_2),
            from_point_list_to_polyhedral_surface_coordinates(points_int_1),
        ]
    )
    assert solid != solid3


def test_triangle():
    p0 = (0, 0, 0)
    p1 = (1, 0, 0)
    p2 = (0, 1, 0)
    p3 = (0, 0, 1)
    t1 = Triangle([p0, p1, p2])
    points = [Point(*p0), Point(*p1), Point(*p2)]
    # iteration
    for point, expected_point in zip(t1, points):
        assert point == expected_point
    # indexing
    for idx in range(3):
        assert t1[idx] == points[idx]
    assert t1[-1] == points[-1]
    assert t1[1:3] == points[1:3]
    # equality
    t2 = Triangle([p0, p1, p3])
    t3 = Triangle([p1, p2, p0])
    assert t1 != t2
    assert t1 != t3


def test_tin_wkt():
    coordinates = [
                [(0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0)],
                [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)]
            ]
    geom = sfcgal.Tin(coordinates)

    assert geom.wktDecim(0) == "TIN Z(((0 0 0,0 0 1,0 1 0,0 0 0)),((0 0 0,0 1 0,1 1 0,0 0 0)))"  # noqa: E501
    assert sfcgal.tin_to_coordinates(geom._geom) == coordinates


def test_tin():
    p0 = (0, 0, 0)
    p1 = (1, 0, 0)
    p2 = (0, 1, 0)
    p3 = (0, 0, 1)
    triangles = [
        Triangle([p0, p1, p2]),
        Triangle([p0, p1, p3]),
        Triangle([p0, p2, p3]),
        Triangle([p1, p2, p3]),
    ]
    tin = Tin([[p0, p1, p2], [p0, p1, p3], [p0, p2, p3], [p1, p2, p3]])
    assert len(tin) == 4
    # iteration
    for triangle, expected_triangle in zip(tin, triangles):
        assert triangle == expected_triangle
    # indexing
    for idx in range(len(tin)):
        assert tin[idx] == triangles[idx]
    assert tin[-1] == triangles[-1]
    assert tin[1:3] == triangles[1:3]
    # equality
    tin2 = Tin([[p0, p1, p2], [p0, p1, p3], [p0, p2, p3]])
    assert not tin2.is_valid()
    assert tin != tin2
    tin3 = Tin([[p1, p2, p3], [p0, p1, p2], [p0, p1, p3], [p0, p2, p3]])
    assert tin != tin3


def test_geometry_collection():
    collection = sfcgal.shape(geom_data.data["gc1"])
    point = sfcgal.shape(geom_data.data["point1"])
    linestring = sfcgal.shape(geom_data.data["line1"])
    polygon = sfcgal.shape(geom_data.data["polygon1"])
    expected_geometries = [point, linestring, polygon]
    # length
    assert len(collection) == 3
    # iteration
    for geometry, expected_geometry in zip(collection, expected_geometries):
        assert geometry == expected_geometry
    # indexing
    g = collection.geoms[1]
    assert isinstance(g, LineString)
    g = collection.geoms[-1]
    assert isinstance(g, Polygon)
    gs = collection.geoms[0:2]
    assert len(gs) == 2
    for idx in range(len(collection)):
        assert collection[idx] == expected_geometries[idx]
    assert collection[-1] == expected_geometries[-1]
    assert collection[1:3] == expected_geometries[1:3]
    # conversion to lists
    gs = list(collection.geoms)
    assert [g.__class__ for g in gs] == [Point, LineString, Polygon]
    # equality
    collection2 = GeometryCollection()
    for _ in range(len(collection)):
        collection2.addGeometry(point)
    assert collection != collection2
    collection3 = GeometryCollection()
    assert collection != collection2
    collection3.addGeometry(point)
    collection3.addGeometry(linestring)
    collection3.addGeometry(polygon)
    assert collection == collection3


def test_is_valid():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert poly.is_valid()
    poly = Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])
    assert not poly.is_valid()

    line = LineString([])
    assert line.is_valid()
    line = LineString([(0, 0)])
    assert not line.is_valid()
    line = LineString([(0, 0), (1, 1), (1, 0), (0, 1)])
    assert line.is_valid()

    poly = Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])
    ring, _ = poly.is_valid_detail()
    assert ring == "ring 0 self intersects"


def test_approximate_medial_axis():
    poly = Polygon(
        [
            (190, 190),
            (10, 190),
            (10, 10),
            (190, 10),
            (190, 20),
            (160, 30),
            (60, 30),
            (60, 130),
            (190, 140),
            (190, 190),
        ]
    )
    res_wkt = poly.approximate_medial_axis().wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt(
        """MULTILINESTRING((184.19 15.81,158.38 20.00),
        (50.00 20.00,158.38 20.00),(50.00 20.00,35.00 35.00),(35.00 35.00,35.00
        153.15),(35.00 153.15,40.70 159.30),(164.04 164.04,40.70 159.30))"""
    )
    assert geom1.covers(geom2)


def test_straight_skeleton():
    poly = Polygon(
        [
            (190, 190),
            (10, 190),
            (10, 10),
            (190, 10),
            (190, 20),
            (160, 30),
            (60, 30),
            (60, 130),
            (190, 140),
            (190, 190),
        ]
    )
    res_wkt = poly.straight_skeleton().wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt(
        """MULTILINESTRING((190.00 190.00,164.04 164.04),(10.00
    190.00,40.70 159.30),(10.00 10.00,35.00 35.00),(190.00 10.00,184.19
    15.81),(190.00 20.00,184.19 15.81),(160.00 30.00,158.38 20.00),(60.00
    30.00,50.00 20.00),(60.00 130.00,35.00 153.15),(190.00 140.00,164.04
    164.04),(184.19 15.81,158.38 20.00),(50.00 20.00,158.38 20.00),(50.00
    20.00,35.00 35.00),(35.00 35.00,35.00 153.15),(35.00 153.15,40.70
    159.30),(164.04 164.04,40.70 159.30))"""
    )
    assert geom1.covers(geom2)


def test_extrude_straight_skeleton_polygon():
    """Inspired from testExtrudeStraightSkeleton SFCGAL unit test
    """
    geom = sfcgal.read_wkt("POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ))")
    expected_wkt = (
          "POLYHEDRALSURFACE Z(((4.00 5.00 0.00,5.00 5.00 0.00,4.00 4.00 0.00,4.00 "
          "5.00 0.00)),((0.00 4.00 0.00,4.00 4.00 0.00,0.00 0.00 0.00,0.00 4.00 "
          "0.00)),((4.00 4.00 0.00,5.00 0.00 0.00,0.00 0.00 0.00,4.00 4.00 "
          "0.00)),((5.00 5.00 0.00,5.00 0.00 0.00,4.00 4.00 0.00,5.00 5.00 "
          "0.00)),((0.00 4.00 0.00,0.00 0.00 0.00,2.00 2.00 2.00,0.00 4.00 "
          "0.00)),((0.00 0.00 0.00,5.00 0.00 0.00,3.00 2.00 2.00,0.00 0.00 "
          "0.00)),((2.00 2.00 2.00,0.00 0.00 0.00,3.00 2.00 2.00,2.00 2.00 "
          "2.00)),((4.50 3.50 0.50,5.00 5.00 0.00,4.50 4.50 0.50,4.50 3.50 "
          "0.50)),((3.00 2.00 2.00,5.00 0.00 0.00,4.50 3.50 0.50,3.00 2.00 "
          "2.00)),((4.50 3.50 0.50,5.00 0.00 0.00,5.00 5.00 0.00,4.50 3.50 "
          "0.50)),((5.00 5.00 0.00,4.00 5.00 0.00,4.50 4.50 0.50,5.00 5.00 "
          "0.00)),((4.50 4.50 0.50,4.00 4.00 0.00,4.50 3.50 0.50,4.50 4.50 "
          "0.50)),((4.50 4.50 0.50,4.00 5.00 0.00,4.00 4.00 0.00,4.50 4.50 "
          "0.50)),((4.00 4.00 0.00,0.00 4.00 0.00,2.00 2.00 2.00,4.00 4.00 "
          "0.00)),((4.50 3.50 0.50,4.00 4.00 0.00,3.00 2.00 2.00,4.50 3.50 "
          "0.50)),((3.00 2.00 2.00,4.00 4.00 0.00,2.00 2.00 2.00,3.00 2.00 "
          "2.00)))"
    )
    result = geom.extrude_straight_skeleton(2.0)
    assert expected_wkt == result.wktDecim(2)


def test_extrude_straight_skeleton_polygon_with_hole():
    """Inspired from testExtrudeStraightSkeletonPolygonWithHole SFCGAL unit test
    """
    geom = sfcgal.read_wkt(
        "POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ), (1 1, 1 2, 2 2, 2 1, 1 1))"
    )
    expected_wkt = (
        "POLYHEDRALSURFACE Z(((4.00 5.00 0.00,5.00 5.00 0.00,4.00 4.00 0.00,4.00 "
        "5.00 0.00)),((2.00 1.00 0.00,5.00 0.00 0.00,0.00 0.00 0.00,2.00 1.00 "
        "0.00)),((5.00 5.00 0.00,5.00 0.00 0.00,4.00 4.00 0.00,5.00 5.00 "
        "0.00)),((2.00 1.00 0.00,0.00 0.00 0.00,1.00 1.00 0.00,2.00 1.00 "
        "0.00)),((1.00 2.00 0.00,1.00 1.00 0.00,0.00 0.00 0.00,1.00 2.00 "
        "0.00)),((0.00 4.00 0.00,2.00 2.00 0.00,1.00 2.00 0.00,0.00 4.00 "
        "0.00)),((0.00 4.00 0.00,1.00 2.00 0.00,0.00 0.00 0.00,0.00 4.00 "
        "0.00)),((4.00 4.00 0.00,5.00 0.00 0.00,2.00 2.00 0.00,4.00 4.00 "
        "0.00)),((4.00 4.00 0.00,2.00 2.00 0.00,0.00 4.00 0.00,4.00 4.00 "
        "0.00)),((2.00 2.00 0.00,5.00 0.00 0.00,2.00 1.00 0.00,2.00 2.00 "
        "0.00)),((0.50 2.50 0.50,0.00 0.00 0.00,0.50 0.50 0.50,0.50 2.50 "
        "0.50)),((1.00 3.00 1.00,0.00 4.00 0.00,0.50 2.50 0.50,1.00 3.00 "
        "1.00)),((0.50 2.50 0.50,0.00 4.00 0.00,0.00 0.00 0.00,0.50 2.50 "
        "0.50)),((2.50 0.50 0.50,5.00 0.00 0.00,3.50 1.50 1.50,2.50 0.50 "
        "0.50)),((0.00 0.00 0.00,5.00 0.00 0.00,2.50 0.50 0.50,0.00 0.00 "
        "0.00)),((0.50 0.50 0.50,0.00 0.00 0.00,2.50 0.50 0.50,0.50 0.50 "
        "0.50)),((4.50 3.50 0.50,5.00 5.00 0.00,4.50 4.50 0.50,4.50 3.50 "
        "0.50)),((3.50 2.50 1.50,3.50 1.50 1.50,4.50 3.50 0.50,3.50 2.50 "
        "1.50)),((4.50 3.50 0.50,5.00 0.00 0.00,5.00 5.00 0.00,4.50 3.50 "
        "0.50)),((3.50 1.50 1.50,5.00 0.00 0.00,4.50 3.50 0.50,3.50 1.50 "
        "1.50)),((5.00 5.00 0.00,4.00 5.00 0.00,4.50 4.50 0.50,5.00 5.00 "
        "0.00)),((4.50 4.50 0.50,4.00 4.00 0.00,4.50 3.50 0.50,4.50 4.50 "
        "0.50)),((4.50 4.50 0.50,4.00 5.00 0.00,4.00 4.00 0.00,4.50 4.50 "
        "0.50)),((3.00 3.00 1.00,0.00 4.00 0.00,1.00 3.00 1.00,3.00 3.00 "
        "1.00)),((3.50 2.50 1.50,4.50 3.50 0.50,3.00 3.00 1.00,3.50 2.50 "
        "1.50)),((3.00 3.00 1.00,4.00 4.00 0.00,0.00 4.00 0.00,3.00 3.00 "
        "1.00)),((4.50 3.50 0.50,4.00 4.00 0.00,3.00 3.00 1.00,4.50 3.50 "
        "0.50)),((2.00 1.00 0.00,1.00 1.00 0.00,0.50 0.50 0.50,2.00 1.00 "
        "0.00)),((2.50 0.50 0.50,2.00 1.00 0.00,0.50 0.50 0.50,2.50 0.50 "
        "0.50)),((1.00 1.00 0.00,1.00 2.00 0.00,0.50 2.50 0.50,1.00 1.00 "
        "0.00)),((0.50 0.50 0.50,1.00 1.00 0.00,0.50 2.50 0.50,0.50 0.50 "
        "0.50)),((1.00 3.00 1.00,2.00 2.00 0.00,3.00 3.00 1.00,1.00 3.00 "
        "1.00)),((0.50 2.50 0.50,1.00 2.00 0.00,1.00 3.00 1.00,0.50 2.50 "
        "0.50)),((1.00 3.00 1.00,1.00 2.00 0.00,2.00 2.00 0.00,1.00 3.00 "
        "1.00)),((2.00 2.00 0.00,2.00 1.00 0.00,2.50 0.50 0.50,2.00 2.00 "
        "0.00)),((3.50 2.50 1.50,3.00 3.00 1.00,3.50 1.50 1.50,3.50 2.50 "
        "1.50)),((3.50 1.50 1.50,2.00 2.00 0.00,2.50 0.50 0.50,3.50 1.50 "
        "1.50)),((3.00 3.00 1.00,2.00 2.00 0.00,3.50 1.50 1.50,3.00 3.00 "
        "1.00)))"
    )
    result = geom.extrude_straight_skeleton(2.0)
    assert expected_wkt == result.wktDecim(2)


def test_extrude_straight_skeleton_building():
    """Inspired from testExtrudeStraightSkeletonGenerateBuilding SFCGAL unit test
    """
    geom = sfcgal.read_wkt(
        "POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ), (1 1, 1 2, 2 2, 2 1, 1 1))"
    )
    expected_wkt = (
        "POLYHEDRALSURFACE Z(((0.00 0.00 0.00,0.00 4.00 0.00,4.00 4.00 0.00,4.00 "
        "5.00 0.00,5.00 5.00 0.00,5.00 0.00 0.00,0.00 0.00 0.00),(1.00 1.00 "
        "0.00,2.00 1.00 0.00,2.00 2.00 0.00,1.00 2.00 0.00,1.00 1.00 "
        "0.00)),((0.00 0.00 0.00,0.00 0.00 9.00,0.00 4.00 9.00,0.00 4.00 "
        "0.00,0.00 0.00 0.00)),((0.00 4.00 0.00,0.00 4.00 9.00,4.00 4.00 "
        "9.00,4.00 4.00 0.00,0.00 4.00 0.00)),((4.00 4.00 0.00,4.00 4.00 "
        "9.00,4.00 5.00 9.00,4.00 5.00 0.00,4.00 4.00 0.00)),((4.00 5.00 "
        "0.00,4.00 5.00 9.00,5.00 5.00 9.00,5.00 5.00 0.00,4.00 5.00 "
        "0.00)),((5.00 5.00 0.00,5.00 5.00 9.00,5.00 0.00 9.00,5.00 0.00 "
        "0.00,5.00 5.00 0.00)),((5.00 0.00 0.00,5.00 0.00 9.00,0.00 0.00 "
        "9.00,0.00 0.00 0.00,5.00 0.00 0.00)),((1.00 1.00 0.00,1.00 1.00 "
        "9.00,2.00 1.00 9.00,2.00 1.00 0.00,1.00 1.00 0.00)),((2.00 1.00 "
        "0.00,2.00 1.00 9.00,2.00 2.00 9.00,2.00 2.00 0.00,2.00 1.00 "
        "0.00)),((2.00 2.00 0.00,2.00 2.00 9.00,1.00 2.00 9.00,1.00 2.00 "
        "0.00,2.00 2.00 0.00)),((1.00 2.00 0.00,1.00 2.00 9.00,1.00 1.00 "
        "9.00,1.00 1.00 0.00,1.00 2.00 0.00)),((4.00 5.00 9.00,5.00 5.00 "
        "9.00,4.00 4.00 9.00,4.00 5.00 9.00)),((2.00 1.00 9.00,5.00 0.00 "
        "9.00,0.00 0.00 9.00,2.00 1.00 9.00)),((5.00 5.00 9.00,5.00 0.00 "
        "9.00,4.00 4.00 9.00,5.00 5.00 9.00)),((2.00 1.00 9.00,0.00 0.00 "
        "9.00,1.00 1.00 9.00,2.00 1.00 9.00)),((1.00 2.00 9.00,1.00 1.00 "
        "9.00,0.00 0.00 9.00,1.00 2.00 9.00)),((0.00 4.00 9.00,2.00 2.00 "
        "9.00,1.00 2.00 9.00,0.00 4.00 9.00)),((0.00 4.00 9.00,1.00 2.00 "
        "9.00,0.00 0.00 9.00,0.00 4.00 9.00)),((4.00 4.00 9.00,5.00 0.00 "
        "9.00,2.00 2.00 9.00,4.00 4.00 9.00)),((4.00 4.00 9.00,2.00 2.00 "
        "9.00,0.00 4.00 9.00,4.00 4.00 9.00)),((2.00 2.00 9.00,5.00 0.00 "
        "9.00,2.00 1.00 9.00,2.00 2.00 9.00)),((0.50 2.50 9.50,0.00 0.00 "
        "9.00,0.50 0.50 9.50,0.50 2.50 9.50)),((1.00 3.00 10.00,0.00 4.00 "
        "9.00,0.50 2.50 9.50,1.00 3.00 10.00)),((0.50 2.50 9.50,0.00 4.00 "
        "9.00,0.00 0.00 9.00,0.50 2.50 9.50)),((2.50 0.50 9.50,5.00 0.00 "
        "9.00,3.50 1.50 10.50,2.50 0.50 9.50)),((0.00 0.00 9.00,5.00 0.00 "
        "9.00,2.50 0.50 9.50,0.00 0.00 9.00)),((0.50 0.50 9.50,0.00 0.00 "
        "9.00,2.50 0.50 9.50,0.50 0.50 9.50)),((4.50 3.50 9.50,5.00 5.00 "
        "9.00,4.50 4.50 9.50,4.50 3.50 9.50)),((3.50 2.50 10.50,3.50 1.50 "
        "10.50,4.50 3.50 9.50,3.50 2.50 10.50)),((4.50 3.50 9.50,5.00 0.00 "
        "9.00,5.00 5.00 9.00,4.50 3.50 9.50)),((3.50 1.50 10.50,5.00 0.00 "
        "9.00,4.50 3.50 9.50,3.50 1.50 10.50)),((5.00 5.00 9.00,4.00 5.00 "
        "9.00,4.50 4.50 9.50,5.00 5.00 9.00)),((4.50 4.50 9.50,4.00 4.00 "
        "9.00,4.50 3.50 9.50,4.50 4.50 9.50)),((4.50 4.50 9.50,4.00 5.00 "
        "9.00,4.00 4.00 9.00,4.50 4.50 9.50)),((3.00 3.00 10.00,0.00 4.00 "
        "9.00,1.00 3.00 10.00,3.00 3.00 10.00)),((3.50 2.50 10.50,4.50 3.50 "
        "9.50,3.00 3.00 10.00,3.50 2.50 10.50)),((3.00 3.00 10.00,4.00 4.00 "
        "9.00,0.00 4.00 9.00,3.00 3.00 10.00)),((4.50 3.50 9.50,4.00 4.00 "
        "9.00,3.00 3.00 10.00,4.50 3.50 9.50)),((2.00 1.00 9.00,1.00 1.00 "
        "9.00,0.50 0.50 9.50,2.00 1.00 9.00)),((2.50 0.50 9.50,2.00 1.00 "
        "9.00,0.50 0.50 9.50,2.50 0.50 9.50)),((1.00 1.00 9.00,1.00 2.00 "
        "9.00,0.50 2.50 9.50,1.00 1.00 9.00)),((0.50 0.50 9.50,1.00 1.00 "
        "9.00,0.50 2.50 9.50,0.50 0.50 9.50)),((1.00 3.00 10.00,2.00 2.00 "
        "9.00,3.00 3.00 10.00,1.00 3.00 10.00)),((0.50 2.50 9.50,1.00 2.00 "
        "9.00,1.00 3.00 10.00,0.50 2.50 9.50)),((1.00 3.00 10.00,1.00 2.00 "
        "9.00,2.00 2.00 9.00,1.00 3.00 10.00)),((2.00 2.00 9.00,2.00 1.00 "
        "9.00,2.50 0.50 9.50,2.00 2.00 9.00)),((3.50 2.50 10.50,3.00 3.00 "
        "10.00,3.50 1.50 10.50,3.50 2.50 10.50)),((3.50 1.50 10.50,2.00 2.00 "
        "9.00,2.50 0.50 9.50,3.50 1.50 10.50)),((3.00 3.00 10.00,2.00 2.00 "
        "9.00,3.50 1.50 10.50,3.00 3.00 10.00)))"
    )
    result = geom.extrude_polygon_straight_skeleton(9.0, 2.0)
    assert expected_wkt == result.wktDecim(2)


def test_minkowski_sum():
    poly = Polygon(
        [
            (190, 190),
            (10, 190),
            (10, 10),
            (190, 10),
            (190, 20),
            (160, 30),
            (60, 30),
            (60, 130),
            (190, 140),
            (190, 190),
        ]
    )
    poly2 = Polygon([(185, 185), (185, 190), (190, 190), (190, 185), (185, 185)])
    res_wkt = poly.straight_skeleton().minkowski_sum(poly2).wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt(
        """MULTIPOLYGON(((375.00 210.00,370.11 206.47,349.17
    209.87,350.00 215.00,350.00 220.00,345.00 220.00,343.38 210.00,245.00
    210.00,250.00 215.00,250.00 220.00,245.00 220.00,237.50 212.50,225.00
    225.00,225.00 333.52,245.00 315.00,250.00 315.00,250.00 320.00,227.49
    340.84,230.70 344.30,349.24 348.86,375.00 325.00,380.00 325.00,380.00
    330.00,356.64 351.64,380.00 375.00,380.00 380.00,375.00 380.00,349.04
    354.04,230.51 349.49,200.00 380.00,195.00 380.00,195.00 375.00,223.29
    346.71,220.00 343.15,220.00 225.00,195.00 200.00,195.00 195.00,200.00
    195.00,222.50 217.50,235.00 205.00,240.00 205.00,343.38 205.00,369.19
    200.81,375.00 195.00,380.00 195.00,380.00 200.00,377.09 202.91,380.00
    205.00,380.00 210.00,375.00 210.00)))"""
    )
    assert geom1.covers(geom2)


def test_union():
    poly = Polygon([(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)])
    poly2 = Polygon([(-1, -1, 10), (-1, 1, 10), (1, 1, 10), (1, -1, 10), (-1, -1, 10)])

    res_wkt = poly.union(poly2).wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt(
        """POLYGON((0.00 1.00,-1.00 1.00,-1.00 -1.00,1.00 -1.00,1.00 0.00,1.00
        1.00,0.00 1.00))"""
    )

    assert geom1.covers(geom2)


def test_union_3d():
    poly = Polygon([(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)])
    poly2 = Polygon([(-1, -1, 10), (-1, 1, 10), (1, 1, 10), (1, -1, 10), (-1, -1, 10)])

    res_wkt = poly.union(poly2).wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt(
        """GEOMETRYCOLLECTION(TIN(((-0.00 0.00 1.00,-0.00 1.00 1.00,1.00 1.00
        1.00,-0.00 0.00 1.00)),((1.00 -0.00 1.00,-0.00 0.00 1.00,1.00 1.00
        1.00,1.00 -0.00 1.00))),TIN(((-1.00 -1.00 10.00,-1.00 1.00 10.00,1.00
        1.00 10.00,-1.00 -1.00 10.00)),((1.00 -1.00 10.00,-1.00 -1.00 10.00,
        1.00 1.00 10.00,1.00 -1.00 10.00))))"""
    )

    assert geom1.covers(geom2)


def test_instersects():
    line = LineString([(0, 0), (4, 4)])
    line2 = LineString([(0, 4), (4, 0)])

    assert line.intersects(line2)


def test_intersection_3d():
    line = LineString([(0, 0), (4, 4)])
    line2 = LineString([(0, 4), (4, 0)])

    res_wkt = line.intersection_3d(line2).wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt("POINT(2 2)")

    assert geom1.covers(geom2)

    line = LineString([(0, 0, 1), (4, 4, 3)])
    line2 = LineString([(0, 4, 5), (4, 0, 2)])

    assert line.intersection_3d(line2).is_empty == 1

    line = LineString([(0, 0, 2), (4, 4, 4)])
    line2 = LineString([(0, 4, 4), (4, 0, 2)])

    res_wkt = line.intersection_3d(line2).wktDecim(0)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt("POINT(2 2 3)")

    assert geom1.covers(geom2)


def test_convexhull():
    mp = MultiPoint([(0, 0, 5), (5, 0, 3), (2, 2, 4), (5, 5, 6), (0, 5, 2), (0, 0, 8)])

    # convexhull
    geom = mp.convexhull()
    res_wkt = "POLYGON((0.0 0.0,5.0 0.0,5.0 5.0,0.0 5.0,0.0 0.0))"
    geom_res = sfcgal.read_wkt(res_wkt)
    assert geom.covers(geom_res)

    # convexhull_3d
    geom = mp.convexhull_3d()
    geom_res = sfcgal.read_wkt(
        """
        POLYHEDRALSURFACE(((5.0 0.0 3.0,0.0 0.0 8.0,0.0 0.0 5.0,5.0 0.0 3.0)),
        ((0.0 0.0 8.0,0.0 5.0 2.0,0.0 0.0 5.0,0.0 0.0 8.0)),
        ((0.0 0.0 8.0,5.0 0.0 3.0,5.0 5.0 6.0,0.0 0.0 8.0)),
        ((5.0 5.0 6.0,0.0 5.0 2.0,0.0 0.0 8.0,5.0 5.0 6.0)),
        ((5.0 0.0 3.0,0.0 5.0 2.0,5.0 5.0 6.0,5.0 0.0 3.0)),
        ((0.0 0.0 5.0,0.0 5.0 2.0,5.0 0.0 3.0,0.0 0.0 5.0)))"""
    )
    assert geom.wktDecim(1) == geom_res.wktDecim(1)


def test_alphaShapes():
    wkt = """MultiPoint ((6.3 8.4),(7.6 8.8),(6.8 7.3),(5.3 1.8),(9.1 5),(8.1 7),
    (8.8 2.9),(2.4 8.2),(3.2 5.1),(3.7 2.3),(2.7 5.4),(8.4 1.9),(7.5 8.7),(4.4 4.2),
    (7.7 6.7),(9 3),(3.6 6.1),(3.2 6.5),(8.1 4.7),(8.8 5.8),(6.8 7.3),(4.9 9.5),(8.1 6),
    (8.7 5),(7.8 1.6),(7.9 2.1),(3 2.2),(7.8 4.3),(2.6 8.5),(4.8 3.4),(3.5 3.5),(3.6 4),
    (3.1 7.9),(8.3 2.9),(2.7 8.4),(5.2 9.8),(7.2 9.5),(8.5 7.1),(7.5 8.4),(7.5 7.7),
    (8.1 2.9),(7.7 7.3),(4.1 4.2),(8.3 7.2),(2.3 3.6),(8.9 5.3),(2.7 5.7),(5.7 9.7),
    (2.7 7.7),(3.9 8.8),(6 8.1),(8 7.2),(5.4 3.2),(5.5 2.6),(6.2 2.2),(7 2),(7.6 2.7),
    (8.4 3.5),(8.7 4.2),(8.2 5.4),(8.3 6.4),(6.9 8.6),(6 9),(5 8.6),(4.3 8),(3.6 7.3),
    (3.6 6.8),(4 7.5),(2.4 6.7),(2.3 6),(2.6 4.4),(2.8 3.3),(4 3.2),(4.3 1.9),(6.5 1.6),
    (7.3 1.6),(3.8 4.6),(3.1 5.9),(3.4 8.6),(4.5 9),(6.4 9.7))"""
    mp = sfcgal.read_wkt(wkt)

    # alpha_shapes with no arguments
    result = mp.alpha_shapes().wktDecim(1)

    expected = """POLYGON((8.9 5.3,9.1 5.0,8.7 4.2,9.0 3.0,8.4 1.9,7.8 1.6,7.3 1.6,6.5 1.6,5.3 1.8,4.3 1.9,3.7 2.3,3.0 2.2,2.8 3.3,2.3 3.6,2.6 4.4,2.7 5.4,2.3 6.0,2.4 6.7,2.7 7.7,2.4 8.2,2.6 8.5,3.4 8.6,3.9 8.8,4.5 9.0,4.9 9.5,5.2 9.8,5.7 9.7,6.4 9.7,7.2 9.5,7.6 8.8,7.5 8.4,8.3 7.2,8.5 7.1,8.8 5.8,8.9 5.3))"""  # noqa: E501

    assert result == expected

    # alpha_shapes allows holes
    result = mp.alpha_shapes(allow_holes=True).wktDecim(1)

    expected = """POLYGON((8.9 5.3,9.1 5.0,8.7 4.2,9.0 3.0,8.4 1.9,7.8 1.6,7.3 1.6,6.5 1.6,5.3 1.8,4.3 1.9,3.7 2.3,3.0 2.2,2.8 3.3,2.3 3.6,2.6 4.4,2.7 5.4,2.3 6.0,2.4 6.7,2.7 7.7,2.4 8.2,2.6 8.5,3.4 8.6,3.9 8.8,4.5 9.0,4.9 9.5,5.2 9.8,5.7 9.7,6.4 9.7,7.2 9.5,7.6 8.8,7.5 8.4,8.3 7.2,8.5 7.1,8.8 5.8,8.9 5.3),(3.6 6.1,3.6 6.8,4.0 7.5,4.3 8.0,6.0 8.1,6.8 7.3,7.7 6.7,8.1 6.0,8.2 5.4,8.1 4.7,7.8 4.3,7.6 2.7,6.2 2.2,5.4 3.2,4.4 4.2,3.8 4.6,3.6 6.1))"""  # noqa: E501

    assert result == expected

    # using optimal alpha
    result = mp.optimal_alpha_shapes().wktDecim(1)

    expected = """POLYGON((8.9 5.3,9.1 5.0,8.7 4.2,9.0 3.0,8.8 2.9,8.4 1.9,7.8 1.6,7.3 1.6,6.5 1.6,5.3 1.8,4.3 1.9,3.7 2.3,3.0 2.2,2.8 3.3,2.3 3.6,2.6 4.4,2.7 5.4,2.3 6.0,2.4 6.7,2.7 7.7,2.4 8.2,2.6 8.5,3.4 8.6,3.9 8.8,4.5 9.0,4.9 9.5,5.2 9.8,5.7 9.7,6.4 9.7,7.2 9.5,7.6 8.8,7.5 8.4,7.5 7.7,8.3 7.2,8.5 7.1,8.3 6.4,8.8 5.8,8.9 5.3))"""  # noqa: E501

    assert result == expected

    # using optimal alpha with allow_holes
    result = mp.optimal_alpha_shapes(True).wktDecim(1)

    expected = """POLYGON((8.9 5.3,9.1 5.0,8.7 4.2,9.0 3.0,8.8 2.9,8.4 1.9,7.8 1.6,7.3 1.6,6.5 1.6,5.3 1.8,4.3 1.9,3.7 2.3,3.0 2.2,2.8 3.3,2.3 3.6,2.6 4.4,2.7 5.4,2.3 6.0,2.4 6.7,2.7 7.7,2.4 8.2,2.6 8.5,3.4 8.6,3.9 8.8,4.5 9.0,4.9 9.5,5.2 9.8,5.7 9.7,6.4 9.7,7.2 9.5,7.6 8.8,7.5 8.4,7.5 7.7,8.3 7.2,8.5 7.1,8.3 6.4,8.8 5.8,8.9 5.3),(3.6 6.1,3.6 6.8,4.0 7.5,4.3 8.0,5.0 8.6,6.0 8.1,6.8 7.3,7.7 6.7,8.1 6.0,8.2 5.4,8.1 4.7,7.8 4.3,8.1 2.9,7.6 2.7,7.0 2.0,6.2 2.2,5.5 2.6,5.4 3.2,4.8 3.4,4.4 4.2,3.8 4.6,3.6 6.1))"""  # noqa: E501

    assert result == expected


def test_area_3d():
    triangle = Triangle([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    assert triangle.area_3d() == 0.5


def test_difference_3d():
    geom1 = sfcgal.read_wkt(
        "SOLID((((0 0 0, 0 1 0, 1 1 0, 1 0 0, 0 0 0)),"
        "((0 0 0, 0 0 1, 0 1 1, 0 1 0, 0 0 0)),"
        "((0 0 0, 1 0 0, 1 0 1, 0 0 1, 0 0 0)),"
        "((1 1 1, 0 1 1, 0 0 1, 1 0 1, 1 1 1)),"
        "((1 1 1, 1 0 1, 1 0 0, 1 1 0, 1 1 1)),"
        "((1 1 1, 1 1 0, 0 1 0, 0 1 1, 1 1 1))))")
    geom2 = sfcgal.read_wkt(
        "SOLID((((0 0 0.5, 0 1 0.5, 1 1 0.5, 1 0 0.5, 0 0 0.5)),"
        "((0 0 0.5, 0 0 1, 0 1 1, 0 1 0.5, 0 0 0.5)),"
        "((0 0 0.5, 1 0 0.5, 1 0 1, 0 0 1, 0 0 0.5)),"
        "((1 1 1, 0 1 1, 0 0 1, 1 0 1, 1 1 1)),"
        "((1 1 1, 1 0 1, 1 0 0.5, 1 1 0.5, 1 1 1)),"
        "((1 1 1, 1 1 0.5, 0 1 0.5, 0 1 1, 1 1 1))))")
    diff = geom1.difference_3d(geom2)
    assert diff.volume() == 0.5


def test_covers_3d():
    geom1 = sfcgal.read_wkt(
        "SOLID(( ((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)), "
        "((1 0 0,1 1 0,1 1 1,1 0 1,1 0 0)), ((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)), "
        "((0 0 1,0 1 1,0 1 0,0 0 0,0 0 1)), ((1 0 1,1 1 1,0 1 1,0 0 1,1 0 1)), "
        "((1 0 0,1 0 1,0 0 1,0 0 0,1 0 0)) ))"
    )
    geom2 = sfcgal.read_wkt(
        "SOLID(( ((0 0 0,0 0.1 0,0.1 0.1 0,0.1 0 0,0 0 0)), "
        "((0.1 0 0,0.1 0.1 0,0.1 0.1 0.1,0.1 0 0.1,0.1 0 0)), "
        "((0 0.1 0,0 0.1 0.1,0.1 0.1 0.1,0.1 0.1 0,0 0.1 0)), "
        "((0 0 0.1,0 0.1 0.1,0 0.1 0,0 0 0,0 0 0.1)), "
        "((0.1 0 0.1,0.1 0.1 0.1,0 0.1 0.1,0 0 0.1,0.1 0 0.1)), "
        "((0.1 0 0,0.1 0 0.1,0 0 0.1,0 0 0,0.1 0 0)) ))"
    )
    assert geom1.covers_3d(geom2)

    geom1 = sfcgal.read_wkt(
        "SOLID(( ((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)), "
        "((1 0 0,1 1 0,1 1 1,1 0 1,1 0 0)), ((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)), "
        "((0 0 1,0 1 1,0 1 0,0 0 0,0 0 1)), ((1 0 1,1 1 1,0 1 1,0 0 1,1 0 1)), "
        "((1 0 0,1 0 1,0 0 1,0 0 0,1 0 0)) ))"
    )
    geom2 = sfcgal.read_wkt(
        "SOLID(( ((0.1 0.1 0.1,0.1 1.1 0.1,1.1 1.1 0.1,1.1 0.1 0.1,0.1 0.1 0.1)), "
        "((1.1 0.1 0.1,1.1 1.1 0.1,1.1 1.1 1.1,1.1 0.1 1.1,1.1 0.1 0.1)), "
        "((0.1 1.1 0.1,0.1 1.1 1.1,1.1 1.1 1.1,1.1 1.1 0.1,0.1 1.1 0.1)), "
        "((0.1 0.1 1.1,0.1 1.1 1.1,0.1 1.1 0.1,0.1 0.1 0.1,0.1 0.1 1.1)), "
        "((1.1 0.1 1.1,1.1 1.1 1.1,0.1 1.1 1.1,0.1 0.1 1.1,1.1 0.1 1.1)), "
        "((1.1 0.1 0.1,1.1 0.1 1.1,0.1 0.1 1.1,0.1 0.1 0.1,1.1 0.1 0.1)) ))"
    )

    assert not geom1.covers_3d(geom2)


def test_is_planar():
    geom_planar = sfcgal.read_wkt(
        "Polygon((0.0 0.0 1.0, 0.0 1.0 1.0, 1.0 1.0 1.0, 1.0 0.0 1.0, 0.0 0.0 1.0))")
    assert geom_planar.is_planar()

    geom_non_planar = sfcgal.read_wkt(
        "Polygon((0.0 0.0 1.0, 0.0 1.0 1.0, 1.0 1.0 1.0, 1.0 0.0 2.0, 0.0 0.0 1.0))")
    assert not geom_non_planar.is_planar()


def test_orientation():
    geom = sfcgal.read_wkt(
        "Polygon((0.0 0.0 1.0, 1.0 0.0 1.0, 1.0 1.0 1.0, 0.0 1.0 1.0, 0.0 0.0 1.0))")

    assert geom.orientation() == -1

    geom = sfcgal.read_wkt(
        "Polygon((0.0 0.0 1.0, 0.0 1.0 1.0, 1.0 1.0 1.0, 1.0 0.0 1.0, 0.0 0.0 1.0))")

    assert geom.orientation() == 1


def test_line_sub_string():
    geom = sfcgal.read_wkt('LineString Z(0 0 0, 10 10 10)')

    result = geom.line_sub_string(0.1, 0.5).wktDecim(0)

    assert result == 'LINESTRING Z(1 1 1,5 5 5)'


def test_partition_2():
    geom = sfcgal.read_wkt(
        'POLYGON((391 374,240 431,252 340,374 320,289 214,134 390,68 186,154 259,'
        '161 107,435 108,208 148,295 160,421 212,441 303,391 374))')

    result = geom.y_monotone_partition_2().wktDecim(0)

    assert result == (
        "GEOMETRYCOLLECTION("
        "POLYGON((134 390,68 186,154 259,134 390)),"
        "POLYGON((289 214,134 390,154 259,161 107,435 108,208 148,295 160,421 212,289 214)),"  # noqa: E501
        "POLYGON((391 374,240 431,252 340,374 320,289 214,421 212,441 303,391 374)))")

    result = geom.approx_convex_partition_2().wktDecim(0)
    assert result == (
        "GEOMETRYCOLLECTION("
        "POLYGON((391 374,240 431,252 340,374 320,391 374)),"
        "POLYGON((134 390,68 186,154 259,134 390)),"
        "POLYGON((289 214,134 390,154 259,289 214)),"
        "POLYGON((161 107,435 108,208 148,161 107)),"
        "POLYGON((154 259,161 107,208 148,154 259)),"
        "POLYGON((289 214,154 259,208 148,295 160,289 214)),"
        "POLYGON((374 320,289 214,295 160,421 212,374 320)),"
        "POLYGON((391 374,374 320,421 212,441 303,391 374)))")

    result = geom.greene_approx_convex_partition_2().wktDecim(0)
    assert result == (
        "GEOMETRYCOLLECTION("
        "POLYGON((134 390,68 186,154 259,134 390)),"
        "POLYGON((161 107,435 108,208 148,161 107)),"
        "POLYGON((208 148,295 160,421 212,289 214,208 148)),"
        "POLYGON((154 259,161 107,208 148,154 259)),"
        "POLYGON((289 214,134 390,154 259,208 148,289 214)),"
        "POLYGON((374 320,289 214,421 212,374 320)),"
        "POLYGON((374 320,421 212,441 303,391 374,374 320)),"
        "POLYGON((391 374,240 431,252 340,374 320,391 374)))")

    result = geom.optimal_convex_partition_2().wktDecim(0)
    assert result == (
        "GEOMETRYCOLLECTION("
        "POLYGON((391 374,240 431,252 340,374 320,391 374)),"
        "POLYGON((134 390,68 186,154 259,134 390)),"
        "POLYGON((161 107,435 108,208 148,161 107)),"
        "POLYGON((154 259,161 107,208 148,154 259)),"
        "POLYGON((289 214,134 390,154 259,208 148,295 160,289 214)),"
        "POLYGON((374 320,289 214,295 160,421 212,441 303,374 320)),"
        "POLYGON((391 374,374 320,441 303,391 374)))")


def test_visibility_point():
    """Inspired from testVisibility_PointInPolygon SFCGAL unit test"""
    geom = sfcgal.read_wkt("POLYGON (( 0 4, 0 0, 3 2, 4 0, 4 4, 1 2, 0 4 ))")
    point = sfcgal.read_wkt("POINT(0.5 2.0)")
    result = geom.point_visibility(point)
    expected_geom = sfcgal.read_wkt("POLYGON((3 2, 1 2, 0 4, 0 0, 3 2))")
    assert result.covers(expected_geom)


def test_visibility_point_with_hole():
    """Inspired from testVisibility_PointInPolygonHole SFCGAL unit test"""
    geom = sfcgal.read_wkt(
        "POLYGON (( 0 4, 0 0, 3 2, 4 0, 4 4, 1 2, 0 4 ), "
        "(0.2 1.75, 0.9 1.8, 0.7 1.2, 0.2 1.75))")
    point = sfcgal.read_wkt("POINT(0.5 2.0)")
    result = geom.point_visibility(point)
    expected_geom = sfcgal.read_wkt(
        "POLYGON((0.0 1.6,0.2 1.8,0.9 1.8,1.9 1.3,3.0 2.0,1.0 2.0,0.0 4.0,0.0 1.6))")
    assert result.covers(expected_geom)


def test_visibility_segment():
    """Inspired from testVisibility_SegmentInPolygon SFCGAL unit test"""
    geom = sfcgal.read_wkt("POLYGON (( 0 4, 0 0, 3 2, 4 0, 4 4, 1 2, 0 4 ))")
    start_point = sfcgal.read_wkt("POINT(1 2)")
    end_point = sfcgal.read_wkt("POINT(4 4)")
    expected_wkt = "POLYGON((4.0 0.0,4.0 4.0,1.0 2.0,0.0 1.3,0.0 0.0,3.0 2.0,4.0 0.0))"
    result = geom.segment_visibility(start_point, end_point)
    assert expected_wkt == result.wktDecim(1)


def test_visibility_segment_with_hole():
    """Inspired from testVisibility_SegmentInPolygonHole SFCGAL unit test"""
    geom = sfcgal.read_wkt(
        "POLYGON ("
        "(1 2, 12 3, 19 -2, 12 6, 14 14, 9 5, 1 2), "
        "(8 3, 8 4, 10 3, 8 3), "
        "(10 6, 11 7, 11 6, 10 6)"
        ")"
    )
    start_point = sfcgal.read_wkt("POINT(19 -2)")
    end_point = sfcgal.read_wkt("POINT(12 6)")
    expected_wkt = (
        "POLYGON((19.0 -2.0,12.0 6.0,14.0 14.0,10.4 7.6,11.0 7.0,11.0 6.0,10.0 "
        "6.0,9.6 6.0,9.0 5.0,1.0 2.0,4.7 2.3,8.0 4.0,10.0 3.0,9.9 2.8,12.0 "
        "3.0,19.0 -2.0))"
    )
    result = geom.segment_visibility(start_point, end_point)
    assert expected_wkt == result.wktDecim(1)


def test_extrude():
    mp = Polygon([(0, 0), (0, 5), (5, 5), (5, 0)])
    result = mp.extrude(0, 0, 5)
    expected_wkt = (
        "POLYHEDRALSURFACE Z("
        "((0.0 0.0 0.0,0.0 5.0 0.0,5.0 5.0 0.0,5.0 0.0 0.0,0.0 0.0 0.0)),"
        "((0.0 0.0 5.0,5.0 0.0 5.0,5.0 5.0 5.0,0.0 5.0 5.0,0.0 0.0 5.0)),"
        "((0.0 0.0 0.0,0.0 0.0 5.0,0.0 5.0 5.0,0.0 5.0 0.0,0.0 0.0 0.0)),"
        "((0.0 5.0 0.0,0.0 5.0 5.0,5.0 5.0 5.0,5.0 5.0 0.0,0.0 5.0 0.0)),"
        "((5.0 5.0 0.0,5.0 5.0 5.0,5.0 0.0 5.0,5.0 0.0 0.0,5.0 5.0 0.0)),"
        "((5.0 0.0 0.0,5.0 0.0 5.0,0.0 0.0 5.0,0.0 0.0 0.0,5.0 0.0 0.0)))")
    assert result.wktDecim(1) == expected_wkt


def test_vtk():
    """Test vtk output"""
    geom = sfcgal.read_wkt(
        "POLYHEDRALSURFACE Z ("
        "((0.0 0.0 0.0, 0.0 5.0 0.0, 5.0 5.0 0.0, 5.0 0.0 0.0, 0.0 0.0 0.0)), "
        "((0.0 0.0 5.0, 5.0 0.0 5.0, 5.0 5.0 5.0, 0.0 5.0 5.0, 0.0 0.0 5.0)), "
        "((0.0 0.0 0.0, 0.0 0.0 5.0, 0.0 5.0 5.0, 0.0 5.0 0.0, 0.0 0.0 0.0)), "
        "((0.0 5.0 0.0, 0.0 5.0 5.0, 5.0 5.0 5.0, 5.0 5.0 0.0, 0.0 5.0 0.0)), "
        "((5.0 5.0 0.0, 5.0 5.0 5.0, 5.0 0.0 5.0, 5.0 0.0 0.0, 5.0 5.0 0.0)), "
        "((5.0 0.0 0.0, 5.0 0.0 5.0, 0.0 0.0 5.0, 0.0 0.0 0.0, 5.0 0.0 0.0)))")
    geom.vtk('/tmp/out.vtk')
    expected_vtk = pathlib.Path(__file__).parent.resolve() / "expected.vtk"
    assert cmp('/tmp/out.vtk', expected_vtk)


def test_rhr_lhr():
    """Test Force_LHR and Force_RHR"""
    extCW_intCCW = "POLYGON((0 5,5 5,5 0,0 0,0 5),(2 1,2 2,1 2,1 1,2 1),(4 3,4 4,3 4,3 3,4 3))"  # noqa: E501
    extCCW_intCW = "POLYGON((0 5,0 0,5 0,5 5,0 5),(2 1,1 1,1 2,2 2,2 1),(4 3,3 3,3 4,4 4,4 3))"  # noqa: E501
    allCW = "POLYGON((0 5,5 5,5 0,0 0,0 5),(2 1,1 1,1 2,2 2,2 1),(4 3,3 3,3 4,4 4,4 3))"  # noqa: E501
    allCCW = "POLYGON((0 5,0 0,5 0,5 5,0 5),(2 1,2 2,1 2,1 1,2 1),(4 3,4 4,3 4,3 3,4 3))"  # noqa: E501

    # Force_RHR
    geom = sfcgal.read_wkt(extCW_intCCW)
    rhr = geom.force_rhr().wktDecim(0)
    assert rhr == extCW_intCCW

    geom = sfcgal.read_wkt(extCCW_intCW)
    rhr = geom.force_rhr().wktDecim(0)
    assert rhr == extCW_intCCW

    geom = sfcgal.read_wkt(allCW)
    rhr = geom.force_rhr().wktDecim(0)
    assert rhr == extCW_intCCW

    geom = sfcgal.read_wkt(allCCW)
    rhr = geom.force_rhr().wktDecim(0)
    assert rhr == extCW_intCCW

    # Force_LHR
    geom = sfcgal.read_wkt(extCW_intCCW)
    lhr = geom.force_lhr().wktDecim(0)
    assert lhr == extCCW_intCW

    geom = sfcgal.read_wkt(extCCW_intCW)
    lhr = geom.force_lhr().wktDecim(0)
    assert lhr == extCCW_intCW

    geom = sfcgal.read_wkt(allCW)
    lhr = geom.force_lhr().wktDecim(0)
    assert lhr == extCCW_intCW

    geom = sfcgal.read_wkt(allCCW)
    lhr = geom.force_lhr().wktDecim(0)
    assert lhr == extCCW_intCW
