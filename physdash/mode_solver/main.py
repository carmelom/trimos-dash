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

from mode_solver import ions as mions
from mode_solver import potential as mpot
from mode_solver.solver import init_crystal
from mode_solver import mode_solver
from .plotter import Plotter


class HarmonicTrapParameters:

    fx: float = 1.0
    fy: float = 1.0
    fz: float = 1.0

    _metadata = {f"f{j}": {"units": 'MHz'} for j in 'xyz'}

    def _freqs(self):
        return [getattr(self, f"f{j}") * 1e6 for j in 'xyz']


class FieldXParameters:

    add_field: bool = False
    field_x: float = 0.0
    field_y: float = 0.0
    field_z: float = 0.0

    _metadata = {f"field_{j}": {"units": "V/m"} for j in "xyz"}

    def _fields(self):
        return [-getattr(self, f"field_{j}") for j in "xyz"]


class CubicParameters:

    add_cubic: bool = False
    cubic_x: float = 0.0

    _metadata = {"cubic_x": {"units": "1e12 V/m^3"}}


class ModeSolverDashboard:

    n_ions: int = 2
    _mode_report: str = ""

    _metadata = {
        'mode_report': {"renderAs": 'textarea'},
    }

    def __init__(self):
        self.trap_parameters = HarmonicTrapParameters()
        self.field_parameters = FieldXParameters()
        self.cubic_parameters = CubicParameters()
        self.plots = Plotter()

    @trigger_update("mode_report")
    def solve(self):
        ion = mions.Ca40
        pot = mpot.HarmonicPaulTrapPotential(*self.trap_parameters._freqs(), ion=ion)

        if self.field_parameters.add_field:
            pot = pot + mpot.LinearPotential(self.field_parameters._fields())

        if self.cubic_parameters.add_cubic:
            pot = pot + mpot.CubicPotential(self.cubic_parameters.cubic_x * 1e12)

        n_ions = self.n_ions
        ions = [ion] * n_ions
        r0 = (0, 0, 0)
        # roi = (400e-6, 30e-6, 30e-6)
        x0 = init_crystal(r0, dx=10e-6, n_ions=n_ions)
        self._results = mode_solver(pot, ions, x0)
        self.plots._update(self._results)
        self._mode_report = repr(self._results)
        print('solve done')

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
