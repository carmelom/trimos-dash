#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 04/2023
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>

import inspect
import numpy as np
import matplotlib.pyplot as plt
from trimos.results import ModeSolverResults
from slapdash import trigger_update

import base64
from io import BytesIO


def _fig_to_str(fig):
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    return base64.b64encode(tmpfile.getvalue()).decode('utf-8')


ion_colors = {
    'Ca40': 'C3',
    'Be9': 'C0',
    'Mg24': 'cyan',
    'Ba137': 'purple',
    'Yb171': 'black'
}


def _update_ions_scatter(scatter, x, y, ions):
    ax = scatter.axes
    col = [ion_colors[str(c)] for c in ions]
    scatter.set(offsets=np.c_[x, y], color=col, zorder=99)
    ax.ignore_existing_data_limits = True
    ax.update_datalim(scatter.get_datalim(ax.transData))
    ax.autoscale_view()
    
def _average_mass(ions):
    return np.asarray([ion.mass_amu for ion in ions]).mean()


class PlotROI:
    x: float = 30.0
    y: float = 8.0
    z: float = 8.0
    x_slice: float = 0.0

    _num: int = 60

    _metadata = {
        'x': {"units": "um"}, 'y': {"units": "um"}, 'z': {"units": "um"},
        'x_slice': {'min': -100, 'max': 100, 'step': 0.1, 'units': 'um', 'renderAs': 'slider'},
    }

    def _xyz(self):
        return (
            np.linspace(-self.x, self.x, self._num) * 1e-6,
            np.linspace(-self.y, self.y, self._num) * 1e-6,
            np.linspace(-self.z, self.z, self._num) * 1e-6,
        )


class Plotter:
    _plot: str = ""
    _fig: plt.Figure = None
    _artists: list = []

    _metadata = {
        'plot': {"renderAs": 'image'},
    }

    def __init__(self, roi: PlotROI):
        self._roi = roi

    @trigger_update("plot")
    def _show(self):
        self._plot = _fig_to_str(self._fig)

    def _update(self, results: ModeSolverResults):
        raise NotImplementedError()

    @property
    def plot(self) -> str:
        return self._plot


class EquilibriumPositionPlotter(Plotter):

    def __init__(self, roi):
        super().__init__(roi)
        self._fig, ax_x = plt.subplots(figsize=(5, 2), dpi=100)

        sc_x = ax_x.scatter([], [])
        ax_x.set(
            xlabel="x [um]",
            ylabel="y [um]"
        )
        self._fig.tight_layout()
        self._artists = [sc_x]

    def _update(self, results: ModeSolverResults):
        sc_x, = self._artists
        x, y = results.x_eq[:, 0:2].T * 1e6
        _update_ions_scatter(sc_x, x, y, results.ions)


class AxialPotentialPlotter(Plotter):

    def __init__(self, roi):
        super().__init__(roi)
        self._fig, ax_pot = plt.subplots(figsize=(5, 2), dpi=100)
        line_pot, = ax_pot.plot([], [], color='k', marker='none', ls='-')
        sc_ions = ax_pot.scatter([], [])
        ax_pot.set(
            xlabel="x [um]",
            ylabel="$\\phi$ [V]"
        )
        self._fig.tight_layout()
        self._artists = [line_pot, sc_ions]

    def _update(self, results):
        line_pot, sc_ions = self._artists
        ax = line_pot.axes
        X = self._roi._xyz()
        X = np.stack(X, axis=1)
        x, y, z = X.T.copy()

        X[:, 1:3] = 0
        m = _average_mass(results.ions)
        pot = results.pot.potential(X, m)
        x_eq = results.x_eq[:, 0]
        pot_eq = results.pot_eq
        line_pot.set_data(x * 1e6, pot)
        _update_ions_scatter(sc_ions, x_eq * 1e6, pot_eq, results.ions)
        ax.relim()
        ax.autoscale_view()


class RadialPotentialPlotter(Plotter):

    def __init__(self, roi):
        super().__init__(roi)
        self._fig, self._ax = plt.subplots(figsize=(3.5, 3.5), dpi=100)
        self._fig.tight_layout()

    def _update(self, results):
        x, y, z = self._roi._xyz()
        y, z = np.meshgrid(y, z)
        shape = y.shape
        y1, z1 = y.ravel(), z.ravel()
        x1 = np.ones_like(y1) * self._roi.x_slice
        X = np.stack([x1, y1, z1], axis=1)
        y_eq, z_eq = results.x_eq[:, 1:3].T
        m = _average_mass(results.ions)
        pot = results.pot.potential(X, m).reshape(shape)
        self._ax.clear()
        sc = self._ax.scatter([], [])
        _update_ions_scatter(sc, y_eq * 1e6, z_eq * 1e6, results.ions)
        self._ax.contour(y * 1e6, z * 1e6, pot, 50)
        self._ax.set(
            xlabel="y [um]",
            ylabel="z [um]",
            aspect=1,
        )


class PlotDashboard:
    _results: ModeSolverResults = None

    def __init__(self):
        self.roi = PlotROI()
        self.equilibrium_position = EquilibriumPositionPlotter(self.roi)
        self.axial_potential = AxialPotentialPlotter(self.roi)
        self.radial_potential = RadialPotentialPlotter(self.roi)

        self._plotters = []
        for _, plotter in inspect.getmembers(self, lambda obj: isinstance(obj, Plotter)):
            self._plotters.append(plotter)

    def _update(self, results: ModeSolverResults):
        self._results = results
        for plotter in self._plotters:
            plotter._update(results)
            plotter._show()
