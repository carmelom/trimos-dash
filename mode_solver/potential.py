#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 04/2023
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>


import numpy as np
from scipy.constants import pi, atomic_mass
from .ions import Ion
from nptyping import NDArray, Shape, Float
from .typing import NCoords, NData


class Potential:

    def __add__(self, other):
        return CombinedPotential(self, other)


class CombinedPotential(Potential):

    def __init__(self, pot_a: Potential, pot_b: Potential):
        self._pot_a = pot_a
        self._pot_b = pot_b

    def potential(self, X: NCoords, mass_amu: NData):
        return self._pot_a.potential(X, mass_amu) + self._pot_b.potential(X, mass_amu)

    def gradient(self, X: NCoords, mass_amu: NData):
        return self._pot_a.gradient(X, mass_amu) + self._pot_b.gradient(X, mass_amu)

    def hessian(self, X: NCoords, mass_amu: NData):
        return self._pot_a.hessian(X, mass_amu) + self._pot_b.hessian(X, mass_amu)


class HarmonicPaulTrapPotential(Potential):

    def __init__(self, fx, fy, fz, ion: Ion, stray_field=[0, 0, 0]):
        wx2, wy2, wz2 = (2 * pi * fx)**2, (2 * pi * fy)**2, (2 * pi * fz)**2
        c_x = ion.mass / ion.charge * wx2
        c_dc = ion.mass / ion.charge * (wy2 - wz2) / 2
        m_c_rf = ion.mass**2 / ion.charge * (wx2 + wy2 + wz2) / 2

        self._H_dc = np.asarray([
            [c_x, 0, 0],
            [0, c_dc - c_x / 2, 0],
            [0, 0, -c_dc - c_x / 2]
        ])

        self._m_H_rf = np.asarray([
            [0, 0, 0],
            [0, m_c_rf, 0],
            [0, 0, m_c_rf]
        ])

    def _H(self, mass_amu):
        mass = atomic_mass * np.atleast_1d(mass_amu).reshape(-1, 1, 1)
        return self._H_dc.reshape(1, 3, 3) + self._m_H_rf / mass

    def potential(self, X: NCoords, mass_amu: NData):
        H = self._H(mass_amu)
        pot = 0.5 * np.einsum('...i,...ij,...j', X, H, X)
        return pot

    def gradient(self, X: NCoords, mass_amu: NData):
        H = self._H(mass_amu)
        grad = np.einsum('...ij,...j', H, X)
        return grad

    def hessian(self, X: NCoords, mass_amu: NData):
        return self._H(mass_amu)


class LinearPotential(Potential):
    def __init__(self, stray_field: NDArray[Shape["3"], Float]):
        self._E = np.asarray(stray_field)

    def potential(self, X: NCoords, mass_amu: NData):
        return np.einsum('j,...j', self._E, X)

    def gradient(self, X: NCoords, mass_amu: NData):
        return self._E.reshape(1, -1)

    def hessian(self, X: NCoords, mass_amu: NData):
        return 0


class CubicPotential(Potential):
    def __init__(self, a_cubic: float):
        self._C = np.zeros((1, 3, 3, 3))
        self._C[0, 0, 0, 0] = a_cubic
        self._C[0, 0, 1, 1] = self._C[0, 1, 1, 0] = self._C[0, 1, 0, 1] = - a_cubic / 2
        self._C[0, 0, 2, 2] = self._C[0, 2, 2, 0] = self._C[0, 2, 0, 2] = - a_cubic / 2

    def potential(self, X: NCoords, mass_amu: NData):
        return (1 / 6.) * np.einsum('...abc,...a,...b,...c', self._C, X, X, X)

    def gradient(self, X: NCoords, mass_amu: NData):
        return 0.5 * np.einsum('...iab,...a,...b', self._C, X, X)

    def hessian(self, X: NCoords, mass_amu: NData):
        return np.einsum('...ija,...a', self._C, X)
