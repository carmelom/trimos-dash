#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 04/2023
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>


import numpy as np
from scipy.constants import pi, elementary_charge, epsilon_0
from .typing import NCoords

kappa = elementary_charge / 4 / pi / epsilon_0


def distances(X: NCoords):
    """distances between particles

    Args:
        X (array, shape (N, d)): particle positions

    Returns:
        r_ab (array, shape (N, N, d)): particle distances, where
          r_ab[a, b, j] = (X[a] - X[b])[j]
    """
    N, d = X.shape
    r = np.empty((N, N, d))
    for j, w in enumerate(X.T):
        r[:, :, j] = w[:, None] - w
    return r


def coulomb_potential(X: NCoords):
    """coulomb_potential

    Args:
        X (array, shape (N, d)): particle positions

    Returns:
        U (float): total Coulomb potential
          U = sum_ab kappa / abs(X[a] - X[b])s
    """
    if X.shape[0] == 1:
        return 0
    r = distances(X)
    r = np.sqrt(np.sum(r**2, axis=-1))
    pot = kappa * np.sum(1 / r[np.triu_indices(len(r), k=1)])
    return pot


def coulomb_gradient(X: NCoords):
    """coulomb_gradient

    Args:
        X (array, shape (N, d)): particle positions

    Returns:
        f (array, shape (N, d)): gradient of U = coulomb_potential(X)
          f[a, j] = d U / d X[a, j]
          or, -f[a] is the total coulomb force on particle a
    """
    r_ab = distances(X)  # shape (N, N, d)
    r = np.sqrt(np.sum(r_ab**2, axis=-1))  # shape (N, N), diag == 0
    np.fill_diagonal(r, np.inf)
    return - kappa * np.sum(r_ab / r[..., None]**3, axis=1)


def coulomb_hessian(X: NCoords):
    """coulomb_hessian

    Args:
        X (array, shape (N, d)): particle positions

    Returns:
        H (array, shape (N, N, d, d)): gradient of U = coulomb_potential(X)
          H[a, b, i, j] = d^2 U / d X[a, i] d X[b, j]
          or, -H[a, b] is the gradient in the coulomb force on particle a
          due to displacing particle b
    """
    N, d = X.shape
    r_ab = distances(X)  # shape (N, N, d)
    r = np.sqrt(np.sum(r_ab**2, axis=-1))  # shape (N, N), diag == 0
    np.fill_diagonal(r, np.inf)
    r = r[:, :, None, None]
    d_ij = np.eye(d)[None, None, :, :]
    H = kappa * (d_ij / r**3 - 3 * r_ab[:, :, :, None] * r_ab[:, :, None, :] / r**5)
    H[np.diag_indices(N)] = - H.sum(axis=1)
    return H
