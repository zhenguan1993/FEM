from numpy.testing._private.nosetester import get_package_name
from FEM.Torsion2D import Torsion2D
from FEM.Mesh.Delaunay import Delaunay
from FEM.Utils.polygonal import roundCorner, giveCoordsCircle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath

r = 1.0
hueco = 0.4
N = 100
phi = 1.0
G = 80000.0

vert, seg = giveCoordsCircle([0, 0], r, n=N)
vertextra = [[-hueco, -hueco], [hueco, -hueco],
             [hueco, hueco], [-hueco, hueco]]
segextra = [[0, 1], [1, 2], [2, 3], [3, 0]]

holes = []
hole = {'center': [-2*r, 2*r], 'segments': segextra, 'vertices': vertextra}
holes += [hole]


params = Delaunay._strdelaunay(constrained=True, delaunay=True, a='0.003', o=2)

geometria = Delaunay(vert, params, nvn=1, holes_dict=holes)
geometria.show()
plt.show()
GG = []
su = 0
for centroide in geometria.centroids:
    path = mpltPath.Path(vertextra)
    inside2 = path.contains_points([centroide])
    GG += [G]
    if inside2[0]:
        GG[-1] = 1
geometria.segments = seg
geometria.mask = None
O = Torsion2D(geometria, GG, phi)
O.geometry.holes = None
O.solve()
plt.show()
