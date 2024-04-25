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
from .ions import ion_colors

import base64
from io import BytesIO


def _fig_to_str(fig):
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format="png")
    return base64.b64encode(tmpfile.getvalue()).decode("utf-8")


def _update_ions_scatter(scatter, x, y, ions):
    ax = scatter.axes
    col = [ion_colors[str(c)] for c in ions]
    scatter.set(offsets=np.c_[x, y], color=col, zorder=99)
    ax.ignore_existing_data_limits = True
    ax.update_datalim(scatter.get_datalim(ax.transData))
    ax.autoscale_view()


def _average_mass(ions):
    return np.asarray([ion.mass_amu for ion in ions]).mean()


def _ravel_coords(*args):
    args = np.broadcast_arrays(*args)
    shape = args[0].shape
    args = list(map(np.ravel, args))
    X = np.stack(args, axis=1).astype(float)
    return shape, X


def _project_on_single_ion_modes(
    mode_vectors, single_ion_modes=np.eye(3), keys=["x", "y", "z"]
):
    # projections of normal modes on single-ion eigenmodes
    proj = abs(np.einsum("Mai,mi", mode_vectors, single_ion_modes)).sum(1)
    mode1_index = np.argmax(proj, axis=1)

    mode_vectors_projected = np.asarray(
        [
            mode_vectors[j] @ single_ion_modes[mode1_index[j]]
            for j in range(len(mode_vectors))
        ]
    )
    mode_labels = {}
    keys = "xyz" if keys is None else keys
    for j, key in enumerate(keys):
        mode_labels[key] = np.where(mode1_index == j)[0]

    return mode_vectors_projected, mode_labels


class PlotROI:
    x: float = 30.0
    y: float = 8.0
    z: float = 8.0
    x_slice: float = 0.0

    _num: int = 60

    _metadata = {
        "x": {"units": "um"},
        "y": {"units": "um"},
        "z": {"units": "um"},
        "x_slice": {
            "min": -100,
            "max": 100,
            "step": 0.1,
            "units": "um",
            "renderAs": "slider",
        },
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
        "plot": {"renderAs": "image"},
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
        ax_x.set(xlabel="x [um]", ylabel="y [um]")
        self._fig.tight_layout()
        self._artists = [sc_x]

    def _update(self, results: ModeSolverResults):
        (sc_x,) = self._artists
        x, y = results.x_eq[:, 0:2].T * 1e6
        _update_ions_scatter(sc_x, x, y, results.ions)


class AxialPotentialPlotter(Plotter):
    def __init__(self, roi):
        super().__init__(roi)
        self._fig, ax_pot = plt.subplots(figsize=(5, 2), dpi=100)
        (line_pot,) = ax_pot.plot([], [], color="k", marker="none", ls="-")
        sc_ions = ax_pot.scatter([], [])
        ax_pot.set(xlabel="x [um]", ylabel="$\\phi$ [V]")
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
        self._fig, self._ax = plt.subplots(
            figsize=(3.5, 3.5), dpi=100, layout="constrained"
        )

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


class ThreeDPotentialPlotter(Plotter):
    def __init__(self, roi):
        super().__init__(roi)
        self._fig = plt.figure(
            figsize=(3.8, 3.8),
            dpi=100,
            layout="constrained",
        )
        self._ax = self._fig.add_subplot(
            111,
            projection="3d",
            computed_zorder=False,
        )

    def _update(self, results):
        self._ax.clear()

        m = _average_mass(results.ions)

        def _fun(x, y, z):
            shape, X = _ravel_coords(x, y, z)
            return results.pot.potential(X, m).reshape(shape)

        _kwargs = dict(levels=30, cmap="coolwarm", alpha=0.65, zorder=-1)

        x, y, z = self._roi._xyz()
        x0, y0, z0 = results.x_eq.mean(axis=0)

        X, Y = np.meshgrid(x, y)
        xy_slice = _fun(X, Y, z0)
        self._ax.contour(
            x * 1e6, y * 1e6, xy_slice, zdir="z", offset=z.min() * 1e6, **_kwargs
        )

        Y, Z = np.meshgrid(y, z)
        yz_slice = _fun(x0, Y, Z)
        self._ax.contour(
            yz_slice, y * 1e6, z * 1e6, zdir="x", offset=x.min() * 1e6, **_kwargs
        )

        Z, X = np.meshgrid(z, x)
        xz_slice = _fun(X, y0, Z)
        self._ax.contour(
            x * 1e6, xz_slice, z * 1e6, zdir="y", offset=y.max() * 1e6, **_kwargs
        )

        x1, y1, z1 = results.x_eq.T
        col = [ion_colors[str(c)] for c in results.ions]
        self._ax.scatter(x1 * 1e6, y1 * 1e6, z1 * 1e6, color=col, zorder=99)

        self._ax.set(
            xlabel="x [um]",
            ylabel="y [um]",
            zlabel="z [um]",
            xlim=(x.min() * 1e6, x.max() * 1e6),
            ylim=(y.min() * 1e6, y.max() * 1e6),
            zlim=(z.min() * 1e6, z.max() * 1e6),
            aspect="equal",
        )


class ModeFreqsPlotter(Plotter):
    def __init__(self, roi):
        super().__init__(roi)
        self._fig, self._ax = plt.subplots(
            figsize=(7, 2.3), dpi=100, layout="constrained"
        )

    def _update(self, results):
        self._ax.clear()
        mode_freqs = results.mode_freqs
        mode_vectors = results.mode_vectors

        _, mode_labels = _project_on_single_ion_modes(mode_vectors)

        for j, (key, ix) in enumerate(mode_labels.items()):
            f = mode_freqs[ix]
            self._ax.vlines(f * 1e-6, 0, 1, label=key, color=f"C{j}", lw=2)
        self._ax.legend()

        self._ax.set(xlabel="Mode frequencies [MHz]", yticks=[])


class ModePartecipationsPlotter(Plotter):
    def __init__(self, roi):
        super().__init__(roi)
        self._figsize = (7, 2.3)
        self._fig, self._ax = plt.subplots(
            figsize=self._figsize, dpi=100, layout="constrained"
        )

    def _update(self, results):
        mode_freqs = results.mode_freqs
        mode_vectors = results.mode_vectors
        mode_vectors_proj, mode_labels = _project_on_single_ion_modes(
            mode_vectors, keys=["x", "y", "z"]
        )

        # --- plot

        cols = [ion_colors[str(c)] for c in results.ions]
        nn = len(results.ions)

        plot_modes = ["x", "y"]
        mosaic = [[f"{mode}_{j}" for j in range(nn)] for mode in plot_modes]
        self._fig, axes = plt.subplot_mosaic(
            mosaic,
            figsize=self._figsize,
            dpi=100,
            sharey=True,
            sharex=True,
            layout="constrained",
        )

        for mode in plot_modes:
            mode_freqs_1 = mode_freqs[mode_labels[mode]]
            mode_vectors_1 = mode_vectors_proj[mode_labels[mode]]
            axes[f"{mode}_0"].set(ylabel=f"{mode} modes")
            for j in range(nn):
                f = mode_freqs_1[j]
                m = mode_vectors_1[j]
                ax = axes[f"{mode}_{j}"]
                ax.bar(np.arange(1, len(m) + 1), m, color=cols)
                ax.text(
                    0.2,
                    0.8,
                    f"{f*1e-6:.2f}",
                    transform=ax.transAxes,
                    ha="center",
                    size=7,
                )
                ax.axhline(0, color="k", lw=0.75, zorder=-1)
                ax.set(xticks=[1, len(m)], xticklabels=[])


class PlotDashboard:
    _results: ModeSolverResults = None

    def __init__(self):
        self.roi = PlotROI()
        self.equilibrium_position = EquilibriumPositionPlotter(self.roi)
        self.axial_potential = AxialPotentialPlotter(self.roi)
        self.radial_potential = RadialPotentialPlotter(self.roi)
        self.plot_3d = ThreeDPotentialPlotter(self.roi)
        self.mode_frequencies = ModeFreqsPlotter(self.roi)
        self.mode_partecipations = ModePartecipationsPlotter(self.roi)

        self._plotters = []
        for _, plotter in inspect.getmembers(
            self, lambda obj: isinstance(obj, Plotter)
        ):
            self._plotters.append(plotter)

    def _update(self, results: ModeSolverResults):
        self._results = results
        for plotter in self._plotters:
            plotter._update(results)
            plotter._show()
