

if __name__ == '__main__':
    import scipy
    import json
    import numpy as np
    from FEM.Elasticity3D import Elasticity, NonLocalElasticityFromTensor
    from FEM.Geometry.Geometry import Geometry3D
    from FEM.Solvers.Lineal import LinealEigen

    # E = 21000000.0
    # v = 0.2
    c11 = 166.0  # MPa
    c12 = 63.9  # MPa
    c44 = 79.6  # MPa
    C = np.array([
        [c11, c12, c12, 0, 0, 0],
        [c12, c11, c12, 0, 0, 0],
        [c12, c12, c11, 0, 0, 0],
        [0, 0, 0, c44, 0, 0],
        [0, 0, 0, 0, c44, 0],
        [0, 0, 0, 0, 0, c44]])*10**9  # Pa-3

    h = 20.4356  # Armstrong
    b = 20.4356  # Armstrong
    L = 20.4356  # Armstrong

    rho = 2.329  # g/cm³

    l = 0.535
    z1 = 0.5
    Lr = 9*l

    def af(rho):
        return (1/(8*np.pi*l**3))*np.exp(-rho)  # No referencia, sacada a mano

    _a = L
    _b = h
    _c = b

    nx = 10
    ny = 10
    nz = 10

    dx = _a/nx
    dy = _b/ny
    dz = _c/nz

    coords = []

    for i in range(nx+1):
        x = i*dx
        for j in range(ny+1):
            y = j*dy
            for k in range(nz+1):
                z = k*dz
                coords += [[x, y, z]]

    dicc = []

    def node(i, j, k): return i*(ny+1)*(nz+1)+j*(nz+1)+k

    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                node1 = node(i, j, k)
                node2 = node(i+1, j, k)
                node3 = node(i+1, j+1, k)
                node4 = node(i, j+1, k)

                node5 = node(i, j, k+1)
                node6 = node(i+1, j, k+1)
                node7 = node(i+1, j+1, k+1)
                node8 = node(i, j+1, k+1)

                dicc += [[node1, node2, node3, node4,
                          node5, node6, node7, node8]]

    geometria = Geometry3D(dicc, coords, ["B1V"]*len(dicc), nvn=3, fast=True)

    O = NonLocalElasticityFromTensor(
        geometria, C, rho, l, z1, Lr, af, verbose=True, solver=LinealEigen)
    O.solve(path='SmolCube.csv')
    y = O.geometry.exportJSON()
    pjson = json.loads(y)
    pjson["disp_field"] = O.eigvec.real.T.tolist()
    y = json.dumps(pjson)
    with open("../FEM C++/docs/resources/CUBEKM101010.json", "w") as f:
        f.write(y)
