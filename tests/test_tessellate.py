import pytest

import pysfcgal.sfcgal as sfcgal
from pysfcgal.sfcgal import (Point, LineString, Polygon, MultiPoint,
			     MultiLineString, MultiPolygon, GeometryCollection)

def test_simple_polygon():
	# t = tessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]))
	# print(t.wkt)
	print("\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]))")
	p = Polygon([(0,0), (1,0), (1,1), (0,1)])
	print(p.wktDecim(1))
	g = GeometryCollection()
	g.addGeometry(p)
	t = g.tessellate()
	print(t.wktDecim(1), "GEOMETRYCOLLECTION(TRIANGLE((1.0 0.0,1.0 1.0,0.0 1.0,1.0 0.0)),TRIANGLE((0.0 0.0,1.0 0.0,0.0 1.0,0.0 0.0)))")

def test_polygon_with_an_hole():
	# t = tessellate(Polygon([(0,0), (1,0), (1,1), (0,1)], [[(.2,.2),(.2,.8),(.8,.8),(.8,.2)]]))
	# print(t.wkt)
	print("\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)], [[(.2,.2),(.2,.8),(.8,.8),(.8,.2)]]))")
	p = Polygon([(0,0), (1,0), (1,1), (0,1)], [[(.2,.2),(.2,.8),(.8,.8),(.8,.2)]])
	g1 = GeometryCollection()
	g1.addGeometry(p)
	print(g1.tessellate().wktDecim(1), "GEOMETRYCOLLECTION(TRIANGLE((0.2 0.2,1.0 0.0,0.8 0.2,0.2 0.2)),TRIANGLE((0.0 0.0,1.0 0.0,0.2 0.2,0.0 0.0)),TRIANGLE((0.0 0.0,0.2 0.2,0.0 1.0,0.0 0.0)),TRIANGLE((0.2 0.8,1.0 1.0,0.0 1.0,0.2 0.8)),TRIANGLE((0.2 0.2,0.2 0.8,0.0 1.0,0.2 0.2)),TRIANGLE((0.8 0.8,1.0 1.0,0.2 0.8,0.8 0.8)),TRIANGLE((0.8 0.2,1.0 1.0,0.8 0.8,0.8 0.2)),TRIANGLE((1.0 0.0,1.0 1.0,0.8 0.2,1.0 0.0)))")

def test_polygon_with_breaklines():
	# t = tessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]), [LineString([(.2, .6), (.8,.6)]), LineString([(.2, .4), (.8,.4)])])
	# print(t.wkt)
	print("\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]), [LineString([(.2, .6), (.8,.6)]), LineString([(.2, .4), (.8,.4)])])")
	p = Polygon([(0,0), (1,0), (1,1), (0,1)])
	lines = [LineString([(.2, .6), (.8,.6)]), LineString([(.2, .4), (.8,.4)])]
	g = GeometryCollection()
	g.addGeometry(p)
	for l in lines:
	    print(l.wktDecim(1))
	    g.addGeometry(l)
	print(g.tessellate().wktDecim(1), "GEOMETRYCOLLECTION(TRIANGLE((0.2 0.4,1.0 0.0,0.8 0.4,0.2 0.4)),TRIANGLE((1.0 0.0,1.0 1.0,0.8 0.6,1.0 0.0)),TRIANGLE((0.8 0.4,1.0 0.0,0.8 0.6,0.8 0.4)),TRIANGLE((0.2 0.4,0.2 0.6,0.0 1.0,0.2 0.4)),TRIANGLE((0.2 0.6,1.0 1.0,0.0 1.0,0.2 0.6)),TRIANGLE((0.0 0.0,1.0 0.0,0.2 0.4,0.0 0.0)),TRIANGLE((0.0 0.0,0.2 0.4,0.0 1.0,0.0 0.0)),TRIANGLE((0.8 0.6,1.0 1.0,0.2 0.6,0.8 0.6)),TRIANGLE((0.8 0.4,0.8 0.6,0.2 0.6,0.8 0.4)),TRIANGLE((0.2 0.4,0.8 0.4,0.2 0.6,0.2 0.4)))")

def test_polygon_with_breaklines_point():
	# t = tessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]), MultiLineString([LineString([(.2, .6), (.8,.6)]), LineString([(.2, .4), (.8,.4)])]), [Point(.9, .9)])
	print("\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]), MultiLineString([LineString([(.2, .6), (.8,.6)]), LineString([(.2, .4), (.8,.4)])]), [Point(.9, .9)])")
	p = Polygon([(0,0), (1,0), (1,1), (0,1)])
	m = MultiLineString([[(.2, .6), (.8,.6)], [(.2, .4), (.8,.4)]])
	po = Point(.9, .9)
	print(p.wktDecim(1))
	print(m.wktDecim(1))
	print(po.wktDecim(1))
	g = GeometryCollection()
	g.addGeometry(p)
	g.addGeometry(m)
	g.addGeometry(po)
	print("\nTriangulation : \n")
	print(g.tessellate().wktDecim(1), "GEOMETRYCOLLECTION(TRIANGLE((0.0 0.0,1.0 0.0,0.2 0.4,0.0 0.0)),TRIANGLE((1.0 0.0,1.0 1.0,0.8 0.6,1.0 0.0)),TRIANGLE((0.8 0.4,1.0 0.0,0.8 0.6,0.8 0.4)),TRIANGLE((0.2 0.4,0.2 0.6,0.0 1.0,0.2 0.4)),TRIANGLE((0.0 0.0,0.2 0.4,0.0 1.0,0.0 0.0)),TRIANGLE((0.9 0.9,1.0 1.0,0.0 1.0,0.9 0.9)),TRIANGLE((0.2 0.6,0.9 0.9,0.0 1.0,0.2 0.6)),TRIANGLE((0.8 0.6,0.9 0.9,0.2 0.6,0.8 0.6)),TRIANGLE((0.2 0.4,0.8 0.4,0.2 0.6,0.2 0.4)),TRIANGLE((0.8 0.4,0.8 0.6,0.2 0.6,0.8 0.4)),TRIANGLE((0.2 0.4,1.0 0.0,0.8 0.4,0.2 0.4)),TRIANGLE((0.8 0.6,1.0 1.0,0.9 0.9,0.8 0.6)))")

def test_polygon_with_points():
	#t = tessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]), lines=None, points=[Point(.9, .9)])
	print("\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]), lines=None, points=[Point(.9, .9)])")
	p = Polygon([(0,0), (1,0), (1,1), (0,1)])
	po = Point(.9, .9)
	g = GeometryCollection()
	g.addGeometry(p)
	g.addGeometry(po)
	print(g.tessellate().wktDecim(1), "GEOMETRYCOLLECTION(TRIANGLE((0.9 0.9,1.0 1.0,0.0 1.0,0.9 0.9)),TRIANGLE((0.0 0.0,1.0 0.0,0.9 0.9,0.0 0.0)),TRIANGLE((0.0 0.0,0.9 0.9,0.0 1.0,0.0 0.0)),TRIANGLE((1.0 0.0,1.0 1.0,0.9 0.9,1.0 0.0)))")

def test_polygon_with_quasi_collinear_points():
  # remove small exterior triangles
	#t = tessellate(Polygon(((-4.165589, -29.100525), (8.623957000000001, -28.461553), (21.413503, -27.822581), (10.706928, -13.90117), (0.000353, 0.020242), (-2.082618, -14.540141), (-4.165589, -29.100525))))
	print("\n\ntessellate(Polygon(((-4.165589, -29.100525), (8.623957000000001, -28.461553), (21.413503, -27.822581), (10.706928, -13.90117), (0.000353, 0.020242), (-2.082618, -14.540141), (-4.165589, -29.100525))))")
	p = Polygon([(-4.165589, -29.100525), (8.623957000000001, -28.461553),
		     (21.413503, -27.822581), (10.706928, -13.90117), (0.000353,
								       0.020242),
		     (-2.082618, -14.540141), (-4.165589, -29.100525)])
	g = GeometryCollection()
	g.addGeometry(p)
	print(g.tessellate().wktDecim(4), "GEOMETRYCOLLECTION(TRIANGLE((-4.1656 -29.1005,8.6240 -28.4616,-2.0826 -14.5401,-4.1656 -29.1005)),TRIANGLE((8.6240 -28.4616,10.7069 -13.9012,-2.0826 -14.5401,8.6240 -28.4616)),TRIANGLE((-2.0826 -14.5401,10.7069 -13.9012,0.0004 0.0202,-2.0826 -14.5401)),TRIANGLE((8.6240 -28.4616,21.4135 -27.8226,10.7069 -13.9012,8.6240 -28.4616)))")

def test_polygon_with_hole_and_break_lines():
	#t = tessellate(Polygon([(0,0), (1,0), (1,1), (0,1)], [[(.2,.2), (.2,.8), (.8,.8), (.8, .2)]]), lines=[LineString([(.1, .1), (.9,.1)]), LineString([(.9, .1), (.9,.9)]), LineString([(.9, .9), (.1,.9)]), LineString([(.1, .9), (.1,.1)])])
	print("\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)], [[(.2,.2), (.2,.8), (.8,.8), (.8, .2)]]), lines=[LineString([(.1, .1), (.9,.1)]), LineString([(.9, .1), (.9,.9)]), LineString([(.9, .9), (.1,.9)]), LineString([(.1, .9), (.1,.1)])])")
	p = Polygon([(0,0), (1,0), (1,1), (0,1)], [[(.2,.2), (.2,.8), (.8,.8), (.8, .2)]])
	lines = [LineString([(.1, .1), (.9,.1)]), LineString([(.9, .1), (.9,.9)]), LineString([(.9, .9), (.1,.9)]), LineString([(.1, .9), (.1,.1)])]
	g = GeometryCollection()
	g.addGeometry(p)
	for l in lines:
	    g.addGeometry(l)
	    print(l.wktDecim(1))
	print(g.tessellate().wktDecim(1), "GEOMETRYCOLLECTION(TRIANGLE((0.0 0.0,1.0 0.0,0.1 0.1,0.0 0.0)),TRIANGLE((0.0 0.0,0.1 0.1,0.0 1.0,0.0 0.0)),TRIANGLE((0.1 0.9,1.0 1.0,0.0 1.0,0.1 0.9)),TRIANGLE((0.1 0.1,0.1 0.9,0.0 1.0,0.1 0.1)),TRIANGLE((0.1 0.1,0.9 0.1,0.2 0.2,0.1 0.1)),TRIANGLE((0.1 0.1,1.0 0.0,0.9 0.1,0.1 0.1)),TRIANGLE((0.2 0.8,0.9 0.9,0.1 0.9,0.2 0.8)),TRIANGLE((0.1 0.1,0.2 0.2,0.1 0.9,0.1 0.1)),TRIANGLE((0.2 0.2,0.2 0.8,0.1 0.9,0.2 0.2)),TRIANGLE((0.9 0.9,1.0 1.0,0.1 0.9,0.9 0.9)),TRIANGLE((0.2 0.2,0.9 0.1,0.8 0.2,0.2 0.2)),TRIANGLE((0.8 0.8,0.9 0.9,0.2 0.8,0.8 0.8)),TRIANGLE((0.9 0.1,0.9 0.9,0.8 0.2,0.9 0.1)),TRIANGLE((0.8 0.2,0.9 0.9,0.8 0.8,0.8 0.2)),TRIANGLE((0.9 0.1,1.0 1.0,0.9 0.9,0.9 0.1)),TRIANGLE((1.0 0.0,1.0 1.0,0.9 0.1,1.0 0.0)))")
