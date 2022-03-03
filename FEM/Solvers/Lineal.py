"""Define the structure of a lineal finite element solver
"""

from scipy.sparse.linalg.eigen.arpack import eigsh as largest_eigsh
from scipy.linalg import eigh
import numpy as np
import logging
from scipy.sparse.linalg import spsolve


class Lineal():
    """Lineal Finite Element Solver.
    """

    def __init__(self, FEMObject: 'Core'):
        """Lineal Finite Element Solver

        Args:
            FEMObject (Core): [Finite Element Problem
        """
        self.system = FEMObject
        self.type = 'lineal'

    def run(self, path: str = '', **kargs):
        """Solves the equation system using numpy's solve function

        Args:
            path (str, optional): Path where the solution is stored. Defaults to ''.
        """
        logging.info('Solving equation system...')
        self.system.U = np.linalg.solve(self.system.K, self.system.S)
        if not path == '':
            np.savetxt(path, self.system.U, delimiter=',')
        for e in self.system.elements:
            e.setUe(self.system.U)
        logging.info('Done!')


class LinealSparse():
    """Lineal Finite Element Solver using sparse matrix
    """

    def __init__(self, FEMObject: 'Core'):
        """Lineal Finite Element Solver

        Args:
            FEMObject (Core): Finite Element Problem
        """
        self.system = FEMObject
        self.type = 'lineal-sparse'

    def run(self, path: str = '', **kargs):
        """Solves the equation system using scipy's spsolve function

        Args:
            path (str, optional): Path where the solution is stored. Defaults to ''.
        """
        logging.info('Converting to csr format')
        self.system.K = self.system.K.tocsr()
        logging.info('Solving...')
        self.system.U = spsolve(self.system.K, self.system.S)
        for e in self.system.elements:
            e.setUe(self.system.U)
        logging.info('Solved!')


class LinealEigen():
    """Eigen value solver

    Args:
        FEMObject (Core): FEM problem
    """

    def __init__(self, FEMObject: 'Core'):
        """Eigen value solver

        Args:
            FEMObject (Core): FEM problem
        """
        self.system = FEMObject
        self.type = 'lineal-sparse-eigen'

    def run(self, path: str = '', k=20, **kargs):
        """Solves the smallest k eigenvalues using scipy's eigen value solver

        Args:
            path (str, optional): Path where the solution is stored. Defaults to ''.
            k (int, optional): Number of eigenvalues to calculate. Defaults to 20.
        """
        logging.info('Converting to csr format')
        self.system.K = self.system.K.tocsr()
        logging.info('Solving...')
        # eigv, eigvec = largest_eigsh(
        #     self.system.K, k, self.system.M, which='SM')
        eigv, eigvec = eigh(
            self.system.K.todense(), self.system.M.todense(), eigvals=(N-k, N-1))
        idx = eigv.argsort()[::-1]
        eigv = eigv[idx]
        eigvec = eigvec[:, idx]
        self.system.eigv = eigv
        self.system.eigvec = eigvec
        if path:
            np.savetxt(path.replace('.', '_eigv.'),
                       self.system.eigv, delimiter=',', fmt='%s')
            np.savetxt(path.replace('.', '_eigvec.'),
                       self.system.eigvec, delimiter=',', fmt='%s')
        logging.info('Solved!')
