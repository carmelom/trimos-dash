#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 04/2023
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>

'''
Module docstring
'''
import os
import slapdash
from slapdash import Saver, trigger_update

from mode_solver import ions as ptions
from mode_solver.potential import HarmonicPaulTrapPotential
from mode_solver.solver import init_crystal
from mode_solver import mode_solver

import matplotlib.pyplot as plt

import base64
from io import BytesIO


def _fig_to_str(fig):
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    return base64.b64encode(tmpfile.getvalue()).decode('utf-8')


class HarmonicTrapParameters:

    fx: float = 1.0
    fy: float = 1.0
    fz: float = 1.0

    _metadata = {f"f{j}": {"units": 'MHz'} for j in 'xyz'}

    def _freqs(self):
        return {f"f{j}": getattr(self, f"f{j}") * 1e6 for j in 'xyz'}


class ModeSolverDashboard:

    _mode_plot: str = ""
    _mode_report: str = ""

    n_ions: int = 2

    _metadata = {
        'mode_plot': {"renderAs": 'image'},
        'mode_report': {"renderAs": 'textarea'},
    }

    def __init__(self):
        self.trap_parameters = HarmonicTrapParameters()

    @trigger_update("mode_plot")
    @trigger_update("mode_report")
    def solve(self):
        ion = ptions.Ca40
        pot = HarmonicPaulTrapPotential(**self.trap_parameters._freqs(), ion=ion)

        n_ions = self.n_ions
        ions = [ion] * n_ions
        r0 = (0, 0, 0)
        # roi = (400e-6, 30e-6, 30e-6)
        x0 = init_crystal(r0, dx=5e-6, n_ions=n_ions)
        self._results = mode_solver(pot, ions, x0)

        self._fig, ax = plt.subplots()

        x_eq = self._results.x_eq[:, 0]
        ax.plot(x_eq, 'o')

        self._mode_plot = _fig_to_str(self._fig)
        self._mode_report = str(self._results)

    @property
    def mode_plot(self) -> str:
        return self._mode_plot

    @property
    def mode_report(self) -> str:
        return self._mode_report

    def __repr__(self):
        return "Mode Solver"


def main():

    PORT = 8001
    saver = Saver('settings/mode_solver_settings.json')
    dashboard = saver(ModeSolverDashboard)()
    slapdash.run(dashboard,
                 host='0.0.0.0',
                 port=PORT,
                 css=os.path.join(os.getcwd(), 'custom.css')
                 )


if __name__ == "__main__":
    main()
