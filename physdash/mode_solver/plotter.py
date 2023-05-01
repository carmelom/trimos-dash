#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 04/2023
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>

import numpy as np
import matplotlib.pyplot as plt
from mode_solver.results import ModeSolverResults

import base64
from io import BytesIO


def _fig_to_str(fig):
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    return base64.b64encode(tmpfile.getvalue()).decode('utf-8')


class PlotROI:
    x: float = 30
    y: float = 8
    z: float = 8
    _num: int = 60

    _metadata = {f"{j}": {"units": "um"} for j in "xyz"}

    def _xyz(self):
        return (
            np.linspace(-self.x, self.x, self._num) * 1e-6,
            np.linspace(-self.y, self.y, self._num) * 1e-6,
            np.linspace(-self.z, self.z, self._num) * 1e-6,
        )


class Plotter:
    _plot_x_eq: str = ""
    _plot_potential: str = ""
    _plot_yz: str = ""

    _metadata = {
        'x_eq': {"renderAs": 'image'},
        'potential': {"renderAs": 'image'},
        'ax_yz': {"renderAs": 'image'},
    }

    def __init__(self):
        self.roi = PlotROI()
        self._fig_x_eq, ax_x = plt.subplots(figsize=(5, 2), dpi=100)
        self._fig_potential, ax_pot = plt.subplots(figsize=(5, 2), dpi=100)
        self._fig_yz, ax_yz = plt.subplots(figsize=(3, 3), dpi=100)

        line_x, = ax_x.plot([], [], 'o')
        ax_x.set(
            ylim=(-1.05, 1.05),
            xlabel="x [um]",
            ylabel="y [um]"
        )

        line_pot, = ax_pot.plot([], [], marker='none', ls='-')
        ax_pot.set(
            xlabel="x [um]",
            ylabel="$\\phi$ [V]"
        )

        ax_yz.set(
            xlabel="y [um]",
            ylabel="z [um]",
        )

        self._artists = [line_x, line_pot, ax_yz]

    def _update(self, results: ModeSolverResults):
        line_x, line_pot, ax_yz = self._artists
        x, y = results.x_eq[:, 0:2].T * 1e6
        line_x.set_data(x, y)
        line_x.axes.relim()
        line_x.axes.autoscale_view(scaley=False)
        self._plot_x_eq = _fig_to_str(self._fig_x_eq)

        X = self.roi._xyz()
        X = np.stack(X, axis=1)
        x, y, z = X.T.copy()

        X[:, 1:3] = 0
        pot = results.pot.potential(X, 1)
        line_pot.set_data(x * 1e6, pot)
        line_pot.axes.relim()
        line_pot.axes.autoscale_view()
        self._plot_potential = _fig_to_str(self._fig_potential)

        y, z = np.meshgrid(y, z)
        shape = y.shape
        y1, z1 = y.ravel(), z.ravel()
        X = np.stack([np.zeros_like(y1), y1, z1], axis=1)
        pot = results.pot.potential(X, 1).reshape(shape)
        ax_yz.clear()
        ax_yz.contour(y, z, pot, 50)
        self._plot_yz = _fig_to_str(self._fig_yz)

    @property
    def x_eq(self) -> str:
        return self._plot_x_eq

    @property
    def potential(self) -> str:
        return self._plot_potential

    @property
    def ax_yz(self) -> str:
        return self._plot_yz
