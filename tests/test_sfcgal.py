import pytest

import pysfcgal.sfcgal as sfcgal
from pysfcgal.sfcgal import (Point, LineString, Polygon, GeometryCollection,
                             MultiPoint)
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

    point2 = Point(4, 5)
    assert point2.x == 4.0
    assert point2.y == 5.0
    assert not point2.has_z


def test_line_string():
    line = LineString([(0, 0), (0, 1), (1, 1.5), (1, 2)])
    assert len(line) == 4

    # test access to coordinates
    coords = line.coords
    assert len(coords) == 4
    assert coords[0] == (0.0, 0.0)
    assert coords[-1] == (1.0, 2.0)
    assert coords[0:2] == [(0.0, 0.0), (0.0, 1.0)]


def test_geometry_collection():
    geom = sfcgal.shape(geom_data.data["gc1"])
    # length
    assert len(geom) == 3
    # iteration
    for g in geom.geoms:
        print(geom)
    # indexing
    g = geom.geoms[1]
    assert isinstance(g, LineString)
    g = geom.geoms[-1]
    assert isinstance(g, Polygon)
    gs = geom.geoms[0:2]
    assert len(gs) == 2
    # conversion to lists
    gs = list(geom.geoms)
    assert [g.__class__ for g in gs] == [Point, LineString, Polygon]


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
    assert ring == 'ring 0 self intersects'


def test_approximate_medial_axis():
    poly = Polygon([(190, 190), (10, 190), (10, 10), (190, 10), (190, 20),
                    (160, 30), (60, 30), (60, 130), (190, 140), (190, 190)])
    res_wkt = poly.approximate_medial_axis().wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt(
        """MULTILINESTRING((184.19 15.81,158.38 20.00),
        (50.00 20.00,158.38 20.00),(50.00 20.00,35.00 35.00),(35.00 35.00,35.00
        153.15),(35.00 153.15,40.70 159.30),(164.04 164.04,40.70 159.30))""")
    assert geom1.covers(geom2)


def test_straight_skeleton():
    poly = Polygon([(190, 190), (10, 190), (10, 10), (190, 10), (190, 20),
                    (160, 30), (60, 30), (60, 130), (190, 140), (190, 190)])
    res_wkt = poly.straight_skeleton().wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt("""MULTILINESTRING((190.00 190.00,164.04 164.04),(10.00
    190.00,40.70 159.30),(10.00 10.00,35.00 35.00),(190.00 10.00,184.19
    15.81),(190.00 20.00,184.19 15.81),(160.00 30.00,158.38 20.00),(60.00
    30.00,50.00 20.00),(60.00 130.00,35.00 153.15),(190.00 140.00,164.04
    164.04),(184.19 15.81,158.38 20.00),(50.00 20.00,158.38 20.00),(50.00
    20.00,35.00 35.00),(35.00 35.00,35.00 153.15),(35.00 153.15,40.70
    159.30),(164.04 164.04,40.70 159.30))""")
    assert geom1.covers(geom2)


def test_minkowski_sum():
    poly = Polygon([(190, 190), (10, 190), (10, 10), (190, 10), (190, 20),
                    (160, 30), (60, 30), (60, 130), (190, 140), (190, 190)])
    poly2 = Polygon(
        [(185, 185), (185, 190), (190, 190), (190, 185), (185, 185)])
    res_wkt = poly.straight_skeleton().minkowski_sum(poly2).wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt("""MULTIPOLYGON(((375.00 210.00,370.11 206.47,349.17
    209.87,350.00 215.00,350.00 220.00,345.00 220.00,343.38 210.00,245.00
    210.00,250.00 215.00,250.00 220.00,245.00 220.00,237.50 212.50,225.00
    225.00,225.00 333.52,245.00 315.00,250.00 315.00,250.00 320.00,227.49
    340.84,230.70 344.30,349.24 348.86,375.00 325.00,380.00 325.00,380.00
    330.00,356.64 351.64,380.00 375.00,380.00 380.00,375.00 380.00,349.04
    354.04,230.51 349.49,200.00 380.00,195.00 380.00,195.00 375.00,223.29
    346.71,220.00 343.15,220.00 225.00,195.00 200.00,195.00 195.00,200.00
    195.00,222.50 217.50,235.00 205.00,240.00 205.00,343.38 205.00,369.19
    200.81,375.00 195.00,380.00 195.00,380.00 200.00,377.09 202.91,380.00
    205.00,380.00 210.00,375.00 210.00)))""")
    assert geom1.covers(geom2)


def test_union():
    poly = Polygon([(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)])
    poly2 = Polygon([(-1, -1, 10), (-1, 1, 10),
                     (1, 1, 10), (1, -1, 10), (-1, -1, 10)])

    res_wkt = poly.union(poly2).wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt(
        """POLYGON((0.00 1.00,-1.00 1.00,-1.00 -1.00,1.00 -1.00,1.00 0.00,1.00
        1.00,0.00 1.00))""")

    assert geom1.covers(geom2)


def test_union_3d():
    poly = Polygon([(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)])
    poly2 = Polygon([(-1, -1, 10), (-1, 1, 10),
                     (1, 1, 10), (1, -1, 10), (-1, -1, 10)])

    res_wkt = poly.union(poly2).wktDecim(2)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt(
        """GEOMETRYCOLLECTION(TIN(((-0.00 0.00 1.00,-0.00 1.00 1.00,1.00 1.00
        1.00,-0.00 0.00 1.00)),((1.00 -0.00 1.00,-0.00 0.00 1.00,1.00 1.00
        1.00,1.00 -0.00 1.00))),TIN(((-1.00 -1.00 10.00,-1.00 1.00 10.00,1.00
        1.00 10.00,-1.00 -1.00 10.00)),((1.00 -1.00 10.00,-1.00 -1.00 10.00,
        1.00 1.00 10.00,1.00 -1.00 10.00))))""")

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
    geom2 = sfcgal.read_wkt('POINT(2 2)')

    assert geom1.covers(geom2)

    line = LineString([(0, 0, 1), (4, 4, 3)])
    line2 = LineString([(0, 4, 5), (4, 0, 2)])

    assert line.intersection_3d(line2).is_empty == 1

    line = LineString([(0, 0, 2), (4, 4, 4)])
    line2 = LineString([(0, 4, 4), (4, 0, 2)])

    res_wkt = line.intersection_3d(line2).wktDecim(0)

    geom1 = sfcgal.read_wkt(res_wkt)
    geom2 = sfcgal.read_wkt('POINT(2 2 3)')

    assert geom1.covers(geom2)

def test_convexhull():
    mp = MultiPoint([(0, 0, 5), (5, 0, 3), (2, 2, 4), (5, 5, 6),
                     (0, 5, 2), (0, 0, 8)])

    # convexhull
    geom = mp.convexhull()
    res_wkt = "POLYGON((0.0 0.0,5.0 0.0,5.0 5.0,0.0 5.0,0.0 0.0))"
    geom_res = sfcgal.read_wkt(res_wkt)
    assert geom.covers(geom_res)

    # convexhull_3d
    geom = mp.convexhull_3d()
    geom_res = sfcgal.read_wkt("""
        POLYHEDRALSURFACE(((5.0 0.0 3.0,0.0 0.0 8.0,0.0 0.0 5.0,5.0 0.0 3.0)),
        ((0.0 0.0 8.0,0.0 5.0 2.0,0.0 0.0 5.0,0.0 0.0 8.0)),
        ((0.0 0.0 8.0,5.0 0.0 3.0,5.0 5.0 6.0,0.0 0.0 8.0)),
        ((5.0 5.0 6.0,0.0 5.0 2.0,0.0 0.0 8.0,5.0 5.0 6.0)),
        ((5.0 0.0 3.0,0.0 5.0 2.0,5.0 5.0 6.0,5.0 0.0 3.0)),
        ((0.0 0.0 5.0,0.0 5.0 2.0,5.0 0.0 3.0,0.0 0.0 5.0)))""")
    assert geom.wktDecim(1) == geom_res.wktDecim(1)
