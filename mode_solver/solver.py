#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 10/2022
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>


import numpy as np
from scipy.optimize import minimize

from typing import List, Optional
from .typing import Position, NCoords, Bounds
from .potential import Potential
from .coulomb import coulomb_potential, coulomb_gradient, coulomb_hessian, kappa
from .ions import Ion
from .results import ModeSolverResults


def mode_solver(pot: Potential, ions: List[Ion], x0: NCoords,
                bounds: Optional[Bounds] = None, minimize_options=dict()) -> ModeSolverResults:
    N, d = x0.shape
    masses_amu = np.asarray([ion.mass_amu for ion in ions])

    def fun(X):
        _X = X.reshape(N, d)
        return pot.potential(_X, masses_amu).sum() + coulomb_potential(_X)

    def jac(X):
        _X = X.reshape(N, d)
        grad = pot.gradient(_X, masses_amu) + coulomb_gradient(_X)
        grad = grad.ravel()
        return grad

    def hess(X):
        """Total mass-dependent hessian

        Returns:
            H (array, shape: (Nd, Nd)):
                In the typical case d = 3, it is a (3N, 3N) matrix where coordinates
                are sorted like (x1, y1, z1, x2, y2, z2, ..., xN, yN, zN)
                for ions 1 ... N
        """
        _X = X.reshape(N, d)
        hess = coulomb_hessian(_X)  # shape (N, N, d, d)
        pot_hess = pot.hessian(_X, masses_amu)  # shape (N, d, d)
        hess[np.diag_indices(N, ndim=2)] += pot_hess  # add it in blocks
        hess = np.swapaxes(hess, 1, 2).reshape((N * d, N * d))
        return hess

    # eta = 1e-9
    bounds = list(bounds) * N if bounds is not None else None

    options = dict(
        # maxCGit=0,
        accuracy=1e-8,
        xtol=1e-8,
        ftol=kappa,
        # gtol=kappa / 1e-5,
        # scale=1e-6 * np.ones((N * d,)),
        # maxfun=300 * N * d
    )
    options.update(minimize_options)

    res = minimize(fun, x0.ravel(), method='TNC', jac=jac, bounds=bounds, options=options)
    x_eq = res.x.reshape((N, d))
    pot_eq = pot.potential(x_eq, masses_amu)
    hess = hess(res.x)

    result = ModeSolverResults(pot=pot,
                               ions=ions, x0=x0, x_eq=x_eq,
                               fun=res.fun, jac=res.jac, hess=hess,
                               pot_eq=pot_eq,
                               minimize_results=res)

    return result


def init_crystal(r0: Position, dx: float, n_ions: int) -> NCoords:
    """initialize positions of particles in a 1D crystal
    equally spaced by dx along the x axis

    Args:
        r0 (array_like, shape (3,)): (x, y, z) position of the center of mass of the crystal
        dx (float): particle spacing
        n_ions (int): number of particles

    Returns:
        Coords (array, shape: (n_ions, 3)): particle positions in a crystal
    """
    x0, y0, z0 = r0
    X = np.zeros((n_ions, 3), dtype=float)
    X[:, 0] = np.linspace(-n_ions / 2 * dx, n_ions / 2 * dx, n_ions) + x0
    X[:, 1] = y0
    X[:, 2] = z0
    return X
