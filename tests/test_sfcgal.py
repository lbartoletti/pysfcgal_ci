import pytest

import pysfcgal.sfcgal as sfcgal
from pysfcgal.sfcgal import (Point, LineString, Polygon, MultiPoint,
    MultiLineString, MultiPolygon, GeometryCollection)
import geom_data

def test_version():
    print(sfcgal.sfcgal_version())

geometry_names, geometry_values = zip(*geom_data.data.items())

@pytest.mark.parametrize("geometry", geometry_values, ids=geometry_names)
def test_integrity(geometry):
    """Test conversion from and to GeoJSON-like data"""
    geom = sfcgal.shape(geometry)
    data = sfcgal.mapping(geom)
    assert(geometry == data)

@pytest.mark.parametrize("geometry", geometry_values, ids=geometry_names)
def test_wkt_write(geometry):
    geom = sfcgal.shape(geometry)
    wkt = geom.wkt
    assert(wkt)
    data = sfcgal.mapping(sfcgal.read_wkt(wkt))
    assert(geometry == data)

def test_point_in_polygon():
    """Tests the intersection between a point and a polygon"""
    point = Point(2, 3)
    polygon1 = Polygon([(0, 0), (5, 0), (5, 5), (0, 5), (0, 0)])
    polygon2 = Polygon([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)])
    assert(polygon1.intersects(point))
    assert(point.intersects(polygon1))
    assert(not polygon2.intersects(point))
    assert(not point.intersects(polygon2))
    result = point.intersection(polygon1)
    assert(isinstance(result, Point))
    assert(not result.is_empty)
    assert(result.x == point.x)
    assert(result.y == point.y)
    result = point.intersection(polygon2)
    assert(isinstance(result, GeometryCollection))
    assert(result.is_empty)

def test_intersection_polygon_polygon():
    """Tests the intersection between two polygons"""
    polygon1 = Polygon([(0, 0), (5, 0), (5, 5), (0, 5), (0, 0)])
    polygon2 = Polygon([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)])
    assert(polygon1.intersects(polygon2))
    assert(polygon2.intersects(polygon1))
    polygon3 = polygon1.intersection(polygon2)
    assert(polygon3.area == 1.0)
    # TODO: check coordinates

def test_point():
    point1 = Point(4,5,6)
    assert(point1.x == 4.0)
    assert(point1.y == 5.0)
    assert(point1.z == 6.0)
    assert(point1.has_z)

    point2 = Point(4,5)
    assert(point2.x == 4.0)
    assert(point2.y == 5.0)
    with pytest.raises(sfcgal.DimensionError):
        z = point2.z
    assert(not point2.has_z)

def test_line_string():
    line = LineString([(0,0), (0, 1), (1, 1.5), (1, 2)])
    assert(len(line) == 4)

    # test access to coordinates
    coords = line.coords
    assert(len(coords) == 4)
    assert(coords[0] == (0.0,0.0))
    assert(coords[-1] == (1.0,2.0))
    assert(coords[0:2] == [(0.0,0.0), (0.0, 1.0)])

def test_geometry_collection():
    geom = sfcgal.shape(geom_data.data["gc1"])
    # length
    assert(len(geom) == 3)
    # iteration
    for g in geom.geoms:
        print(geom)
    # indexing
    g = geom.geoms[1]
    assert(isinstance(g, LineString))
    g = geom.geoms[-1]
    assert(isinstance(g, Polygon))
    gs = geom.geoms[0:2]
    assert(len(gs) == 2)
    # conversion to lists
    gs = list(geom.geoms)
    assert([g.__class__ for g in gs] == [Point, LineString, Polygon])

def test_is_valid():
    p = Polygon([(0,0), (1,0), (1,1), (0,1)])
    assert(p.is_valid())
    p = Polygon([(0,0), (1,1), (1,0), (0,1)])
    assert(not p.is_valid())

    l = LineString([])
    assert(l.is_valid())
    l = LineString([(0,0)])
    assert(not l.is_valid())
    l = LineString([(0,0), (1,1), (1,0), (0,1)])
    assert(l.is_valid())

    p = Polygon([(0,0), (1,1), (1,0), (0,1)])
    r, l = p.is_valid_detail()
    assert(r == 'ring 0 self intersects')

def test_approximate_medial_axis():
    p = Polygon( [(190, 190), (10, 190), (10, 10), (190, 10), (190, 20), (160, 30), (60, 30), (60, 130), (190, 140), (190, 190)] )
    resWkt = p.approximate_medial_axis().wktDecim(2)

    g1 = sfcgal.read_wkt(resWkt)
    g2 = sfcgal.read_wkt('MULTILINESTRING((184.19 15.81,158.38 20.00),(50.00 20.00,158.38 20.00),(50.00 20.00,35.00 35.00),(35.00 35.00,35.00 153.15),(35.00 153.15,40.70 159.30),(164.04 164.04,40.70 159.30))')
    assert(g1.covers(g2))

def test_straight_skeleton():
    p = Polygon( [(190, 190), (10, 190), (10, 10), (190, 10), (190, 20), (160, 30), (60, 30), (60, 130), (190, 140), (190, 190)] )
    resWkt = p.straight_skeleton().wktDecim(2)

    g1 = sfcgal.read_wkt(resWkt)
    g2 = sfcgal.read_wkt('MULTILINESTRING((190.00 190.00,164.04 164.04),(10.00 190.00,40.70 159.30),(10.00 10.00,35.00 35.00),(190.00 10.00,184.19 15.81),(190.00 20.00,184.19 15.81),(160.00 30.00,158.38 20.00),(60.00 30.00,50.00 20.00),(60.00 130.00,35.00 153.15),(190.00 140.00,164.04 164.04),(184.19 15.81,158.38 20.00),(50.00 20.00,158.38 20.00),(50.00 20.00,35.00 35.00),(35.00 35.00,35.00 153.15),(35.00 153.15,40.70 159.30),(164.04 164.04,40.70 159.30))')
    assert(g1.covers(g2))

def test_minkowski_sum():
    p = Polygon( [(190, 190), (10, 190), (10, 10), (190, 10), (190, 20), (160, 30), (60, 30), (60, 130), (190, 140), (190, 190)] )
    p2 = Polygon( [ (185, 185), (185, 190), (190, 190), (190, 185), (185, 185) ] )
    resWkt = p.straight_skeleton().minkowski_sum(p2).wktDecim(2)

    g1 = sfcgal.read_wkt(resWkt)
    g2 = sfcgal.read_wkt('MULTIPOLYGON(((375.00 210.00,370.11 206.47,349.17 209.87,350.00 215.00,350.00 220.00,345.00 220.00,343.38 210.00,245.00 210.00,250.00 215.00,250.00 220.00,245.00 220.00,237.50 212.50,225.00 225.00,225.00 333.52,245.00 315.00,250.00 315.00,250.00 320.00,227.49 340.84,230.70 344.30,349.24 348.86,375.00 325.00,380.00 325.00,380.00 330.00,356.64 351.64,380.00 375.00,380.00 380.00,375.00 380.00,349.04 354.04,230.51 349.49,200.00 380.00,195.00 380.00,195.00 375.00,223.29 346.71,220.00 343.15,220.00 225.00,195.00 200.00,195.00 195.00,200.00 195.00,222.50 217.50,235.00 205.00,240.00 205.00,343.38 205.00,369.19 200.81,375.00 195.00,380.00 195.00,380.00 200.00,377.09 202.91,380.00 205.00,380.00 210.00,375.00 210.00)))')
    assert(g1.covers(g2))
