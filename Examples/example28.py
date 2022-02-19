from FEM.Geometry.Geometry import Geometry
from FEM.Elasticity2D import PlaneStress
import matplotlib.pyplot as plt
import numpy as np

geometria = Geometry.loadmsh('Mesh_tests/pieza_acero.msh')
geometria.show()
plt.show()
E = 29000000
v = 0.26
t = 0.5
p0 = 5000
p = p0/2
geometria.loadOnRegion(3, lambda s: p)
O = PlaneStress(geometria, E, v, t)
O.solve()
plt.show()
O.print()
