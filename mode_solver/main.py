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

from pytrans import ions as ptions
from pytrans.analysis.mode_solver import HarmonicTrap
from pytrans.analysis import analyse_potential
from pytrans.plotting.plotting import plot3d_make_layout, plot3d_potential

from enum import Enum

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
        trap = HarmonicTrap(**self.trap_parameters._freqs(), ion=ion)

        ions = [ion] * 4
        r0 = (0, 0, 0)
        roi = (400e-6, 30e-6, 30e-6)
        self._results = analyse_potential(trap, None, ions, r0, roi=roi, verbose=False, plot=False)

        self._fig, self._axes = plot3d_make_layout(n=1)

        plot3d_potential(trap, None, ion, self._results.x_eq, roi,
                         axes=self._axes, analyse_results=self._results)
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
