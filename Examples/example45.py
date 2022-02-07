import numpy as np
import matplotlib.pyplot as plt
from FEM.Elasticity2D import PlaneStrainSparse
from FEM.Geometry.Delaunay import Delaunay

E = 21000000.0  # MPa
v = 0.2  # m
gamma = 23.54

b = 200
h = 100
l = 20

vertices = [[0.0, 0.0], [b, 0.0], [b, h], [b/2+2*l, h],
            [b/2+l, h+l], [b/2-l, h+l], [b/2-2*l, h], [0.0, h]]
params = Delaunay._strdelaunay(
    constrained=True, delaunay=True, a='2', o=2)
geometria = Delaunay(vertices, params, nvn=2, fast=True)
O = PlaneStrainSparse(geometria, E, v, fy=lambda x: -gamma, verbose=True)
cb = O.geometry.cbFromSegment(0, 0, 1)
cb += O.geometry.cbFromSegment(0, 0, 2)
cb += O.geometry.cbFromSegment(1, 0, 1)
cb += O.geometry.cbFromSegment(7, 0, 1)
O.cbe = cb
O.solve()
plt.show()
