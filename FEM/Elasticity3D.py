
from typing import Callable, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from tqdm import tqdm

from .Core import Core, Geometry


class Elasticity(Core):

    def __init__(self, geometry: Geometry, E: Tuple[float, list], v: Tuple[float, list], fx: Callable = lambda x: 0, fy: Callable = lambda x: 0, fz: Callable = lambda x: 0, **kargs) -> None:
        if type(E) == float or type(E) == int:
            E = [E]*len(geometry.elements)
        if type(v) == float or type(v) == int:
            v = [v]*len(geometry.elements)
        self.E = E
        self.v = v
        self.ld = []
        self.mu = []
        self.fx = fx
        self.fy = fy
        self.fz = fz
        for i in range(len(self.E)):
            ld = E[i]*v[i]/(1.0+v[i])/(1.0-2.0*v[i])
            mu = E[i]/2.0/(1.0+v[i])
            self.ld.append(ld)
            self.mu.append(mu)
        if not geometry.nvn == 3:
            print(
                'Border conditions lost, please usea a geometry with 3 variables per node (nvn=3)\nRegenerating Geoemtry...')
            geometry.nvn = 3
            geometry.cbe = []
            geometry.cbn = []
            geometry.initialize()
        Core.__init__(self, geometry, **kargs)

    def elementMatrices(self) -> None:
        """Calculate the element matrices usign Reddy's (2005) finite element model
        """

        for ee, e in enumerate(tqdm(self.elements, unit='Element')):
            m = len(e.gdl.T)

            Fu = np.zeros([m, 1])
            Fv = np.zeros([m, 1])
            Fw = np.zeros([m, 1])

            # Gauss points in global coordinates and Shape functions evaluated in gauss points
            _x, _p = e.T(e.Z.T)
            # Jacobian evaluated in gauss points and shape functions derivatives in natural coordinates
            jac, dpz = e.J(e.Z.T)
            detjac = np.linalg.det(jac)
            _j = np.linalg.inv(jac)  # Jacobian inverse
            dpx = _j @ dpz  # Shape function derivatives in global coordinates

            mu = self.mu[ee]
            ld = self.ld[ee]
            C = np.array([
                [2*mu+ld, ld, ld, 0.0, 0.0, 0.0],
                [ld, 2*mu+ld, ld, 0.0, 0.0, 0.0],
                [ld, ld, 2*mu+ld, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, mu, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, mu, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, mu]])

            o = [0.0]*m
            for k in range(len(e.Z)):  # Iterate over gauss points on domain
                B = np.array([
                    [*dpx[k, 0, :], *o, *o],
                    [*o, *dpx[k, 1, :], *o],
                    [*o, *o, *dpx[k, 2, :]],
                    [*dpx[k, 1, :], *dpx[k, 0, :], *o],
                    [*dpx[k, 2, :], *o, *dpx[k, 0, :]],
                    [*o, *dpx[k, 2, :], *dpx[k, 1, :]]])

                e.Ke += (B.T@C@B)*detjac[k]*e.W[k]

            for i in range(m):  # self part must be vectorized
                for k in range(len(e.Z)):  # Iterate over gauss points on domain

                    Fu[i][0] += _p[k, i] * self.fx(_x[k])*detjac[k]*e.W[k]
                    Fv[i][0] += _p[k, i] * self.fy(_x[k])*detjac[k]*e.W[k]
                    Fw[i][0] += _p[k, i] * self.fz(_x[k])*detjac[k]*e.W[k]

            e.Fe[0:m] += Fu
            e.Fe[m:2*m] += Fv
            e.Fe[2*m:3*m] += Fw

    def postProcess(self, mult: float = 1000, gs=None, levels=1000, **kargs) -> None:
        """Generate the stress surfaces and displacement fields for the geometry

        Args:
                mult (int, optional): Factor for displacements. Defaults to 1000.
                gs (list, optional): List of 4 gridSpec matplotlib objects. Defaults to None.
        """
        # X = []
        # Y = []
        # U1 = []
        # U2 = []
        # U3 = []
        # fig = plt.figure()
        # if not gs:
        #     gss = gridspec.GridSpec(3, 3)
        #     gs = [gss[0, 0], gss[0, 1], gss[0, 2], gss[1:, :]]
        # ax1 = fig.add_subplot(gs[0])
        # ax2 = fig.add_subplot(gs[1])
        # ax3 = fig.add_subplot(gs[2])
        # ax5 = fig.add_subplot(gs[3])
        # ee = -1
        # for e in tqdm(self.elements, unit='Element'):
        #     ee += 1
        #     _x, _u, du = e.giveSolution(True)
        #     X += _x.T[0].tolist()
        #     Y += _x.T[1].tolist()
        #     U1 += (self.C11[ee]*du[:, 0, 0]+self.C12[ee]*du[:, 1, 1]).tolist()
        #     U2 += (self.C12[ee]*du[:, 0, 0]+self.C11[ee]*du[:, 1, 1]).tolist()
        #     U3 += (self.C66[ee]*(du[:, 0, 1]+du[:, 1, 0])).tolist()
        #     coordsNuevas = e._coordsg + e._Ueg * mult
        #     ax5.plot(*e._coordsg.T, '--', color='gray', alpha=0.7)
        #     ax5.plot(*coordsNuevas.T, '-', color='black')
        # ax5.legend(['Original Shape', 'Deformed Shape (x'+format(mult)+')'])
        # ax5.set_aspect('equal')
        # ax1.set_aspect('equal')
        # ax3.set_aspect('equal')
        # ax2.set_aspect('equal')
        # cmap = 'rainbow'
        # def fmt(x): return format(x, '.3f')

        # surf = ax1.tricontourf(X, Y, U1, cmap=cmap, levels=levels, **kargs)
        # plt.colorbar(surf, ax=ax1)
        # ax1.set_title(r'$\sigma_{xx}$')

        # surf = ax2.tricontourf(X, Y, U2, cmap=cmap, levels=levels, **kargs)
        # plt.colorbar(surf, ax=ax2)
        # ax2.set_title(r'$\sigma_{yy}$')

        # surf = ax3.tricontourf(X, Y, U3, cmap=cmap, levels=levels, **kargs)
        # plt.colorbar(surf, ax=ax3)
        # ax3.set_title(r'$\sigma_{xy}$')

        # mask = self.geometry.mask
        # if self.geometry.holes:
        #     for hole in self.geometry.holes:
        #         Xs = np.array(hole['vertices'])[:, 0]
        #         Ys = np.array(hole['vertices'])[:, 1]
        #         ax1.fill(Xs, Ys, color='white', zorder=30)
        #         ax2.fill(Xs, Ys, color='white', zorder=30)
        #         ax3.fill(Xs, Ys, color='white', zorder=30)
        # if not mask == None:
        #     mask = np.array(mask)
        #     cornersnt = np.array(mask[::-1])

        #     xmin = np.min(cornersnt[:, 0])
        #     xmax = np.max(cornersnt[:, 0])

        #     ymin = np.min(cornersnt[:, 1])
        #     ymax = np.max(cornersnt[:, 1])

        #     Xs = [xmin, xmax, xmax, xmin]+cornersnt[:, 0].tolist()
        #     Ys = [ymin, ymin, ymax, ymax]+cornersnt[:, 1].tolist()
        #     ax1.fill(Xs, Ys, color='white', zorder=30)
        #     ax2.fill(Xs, Ys, color='white', zorder=30)
        #     ax3.fill(Xs, Ys, color='white', zorder=30)

    def giveStressPoint(self, X: np.ndarray) -> Tuple[tuple, None]:
        """Calculates the stress in a given set of points.

        Args:
            X (np.ndarray): Points to calculate the Stress. 2D Matrix. with 2 rows. First row is an array of 1 column with X coordinate. Second row is an array of 1 column with Y coordinate

        Returns:
            tuple or None: Tuple of stress (:math:`\sigma_x,\sigma_y,\sigma_{xy}`) if X,Y exists in domain.
        """
        # for ee, e in enumerate(self.elements):
        #     if e.isInside(X.T[0]):
        #         z = e.inverseMapping(np.array([X.T[0]]).T)
        #         _, _, du = e.giveSolutionPoint(z, True)
        #         # TODO Arreglar calculo de esfuerzos para PlaneStrain
        #         sx = (self.C11[ee]*du[:, 0, 0] +
        #               self.C12[ee]*du[:, 1, 1]).tolist()
        #         sy = (self.C12[ee]*du[:, 0, 0] +
        #               self.C11[ee]*du[:, 1, 1]).tolist()
        #         sxy = (self.C66[ee]*(du[:, 0, 1]+du[:, 1, 0])).tolist()
        # return sx, sy, sxy
        pass

    def profile(self, p0: list, p1: list, n: float = 100) -> None:
        """Generate a profile between selected points

        Args:
            p0 (list): start point of the profile [x0,y0]
            p1 (list): end point of the profile [xf,yf]
            n (int, optional): NUmber of samples for graph. Defaults to 100.

        """
        pass
        # _x = np.linspace(p0[0], p1[0], n)
        # _y = np.linspace(p0[1], p1[1], n)
        # X = np.array([_x, _y])
        # U = []
        # U1 = []
        # U2 = []
        # U3 = []
        # _X = []
        # def dist(X): return np.sqrt((p0[0]-X[0])**2+(p0[1]-X[1])**2)
        # for i in range(n):
        #     for ee, e in enumerate(self.elements):
        #         if e.isInside(X.T[i]):
        #             z = e.inverseMapping(np.array([X.T[i]]).T)
        #             _, u, du = e.giveSolutionPoint(z, True)
        #             # TODO Arreglar calculo de esfuerzos para PlaneStrain
        #             U += [u.tolist()]
        #             U1 += (self.C11[ee]*du[:, 0, 0] +
        #                    self.C12[ee]*du[:, 1, 1]).tolist()
        #             U2 += (self.C12[ee]*du[:, 0, 0] +
        #                    self.C11[ee]*du[:, 1, 1]).tolist()
        #             U3 += (self.C66[ee]*(du[:, 0, 1]+du[:, 1, 0])).tolist()
        #             _X.append(dist(X.T[i]))
        #             break
        # fig = plt.figure()
        # ax = fig.add_subplot(1, 3, 1)
        # ax.plot(_X, U1, color='black')
        # ax.grid()
        # ax.set_xlabel('d')
        # ax.set_ylabel(r'$\sigma_{xx}$')
        # ax = fig.add_subplot(1, 3, 2)
        # ax.plot(_X, U2, color='black')
        # ax.grid()
        # ax.set_xlabel('d')
        # ax.set_ylabel(r'$\sigma_{yy}$')
        # ax = fig.add_subplot(1, 3, 3)
        # ax.plot(_X, U3, color='black')
        # ax.grid()
        # ax.set_xlabel('d')
        # ax.set_ylabel(r'$\sigma_{xy}$')
        # return _X, U