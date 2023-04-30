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

    _metadata = {
        'x_eq': {"renderAs": 'image'},
        'potential': {"renderAs": 'image'},
    }

    def __init__(self):
        self.roi = PlotROI()
        self._fig_x_eq, ax_x = plt.subplots(figsize=(6, 2), dpi=100)
        self._fig_potential, ax_pot = plt.subplots(figsize=(6, 2), dpi=100)

        self._line_x, = ax_x.plot([], [], 'o')
        ax_x.set(
            ylim=(-1.05, 1.05),
            xlabel="x [um]",
            ylabel="y [um]"
        )

        self._line_pot, = ax_pot.plot([], [], marker='none', ls='-')
        ax_pot.set(
            xlabel="x [um]",
            ylabel="$\\phi$ [V]"
        )

    def _update(self, results: ModeSolverResults):
        x, y = results.x_eq[:, 0:2].T * 1e6
        self._line_x.set_data(x, y)
        self._line_x.axes.relim()
        self._line_x.axes.autoscale_view(scaley=False)
        self._plot_x_eq = _fig_to_str(self._fig_x_eq)

        x = self.roi._xyz()[0]
        X = np.stack([x, np.zeros_line(x), np.zeros_line(x)], axis=1)
        pot = results.pot.potential(X, 1)
        self._line_pot.set_data(x * 1e6, pot)
        self._line_pot.axes.relim()
        self._line_pot.axes.autoscale_view()
        self._plot_potential = _fig_to_str(self._fig_potential)

    @property
    def x_eq(self) -> str:
        return self._plot_x_eq

    @property
    def potential(self) -> str:
        return self._plot_potential
