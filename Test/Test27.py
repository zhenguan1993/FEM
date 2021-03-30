from FEM.Mesh.Geometry import Geometry
from FEM.Mesh.Delaunay import Delaunay
from FEM.PlaneStress import PlaneStress
from FEM.Utils.polygonal import roundCorner, giveCoordsCircle
import matplotlib.pyplot as plt
import numpy as np

coords = [[0, 0], [4, 0], [4, 0.5], [6, 0.5],
          [6, 2.5], [4, 2.5], [4, 3], [0, 3]]
fillets = [{'start_segment': 1, 'end_segment': 2, 'r': 0.48, 'n': 5},
           {'start_segment': 4, 'end_segment': 5, 'r': 0.48, 'n': 5}]
holes = []
radi = 0.5
cent = [2, 1.5]
vert, seg = giveCoordsCircle(cent, radi, n=50)
hole = {'center': cent, 'segments': seg, 'vertices': vert}
holes += [hole]
params = Delaunay._strdelaunay(constrained=True, delaunay=True, a='0.01', o=2)
geometria = Delaunay(coords, params, nvn=2, fillets=fillets, holes_dict=holes)

geometria.cbe = geometria.cbFromSegment(7, 0, 1)
geometria.cbe += geometria.cbFromSegment(7, 0, 2)

geometria.show()
geometria.saveMesh('Mesh_tests/pieza_acero')
plt.show()

E = 29000000
v = 0.26
t = 0.5
p0 = 5000
p = p0/2
geometria.loadOnSegment(3, lambda s: p)
O = PlaneStress(geometria, E, v, t)
O.solve()
plt.show()
