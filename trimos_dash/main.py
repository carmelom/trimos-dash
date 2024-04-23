#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 04/2023
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>

"""
Module docstring
"""
import os
import argparse
import slapdash
from slapdash import Saver, trigger_update

from trimos import potential as mpot
from trimos.solver import init_crystal
from trimos import mode_solver
from .ions import Ions, parse_ion_string
from .plotter import PlotDashboard


class HarmonicTrapParameters:
    fx: float = 1.0
    fy: float = 1.1
    fz: float = 3.0
    target_ion: Ions = Ions.CA40

    _metadata = {f"f{j}": {"units": "MHz"} for j in "xyz"}

    def _freqs(self):
        return [getattr(self, f"f{j}") * 1e6 for j in "xyz"]


class FieldParameters:
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


class QuarticParameters:
    add_quartic: bool = False
    quartic_x: float = 0.0

    _metadata = {"quartic_x": {"units": "1e18 V/m^4"}}


class ModeSolverDashboard:
    _mode_report: str = ""

    _metadata = {
        "mode_report": {"renderAs": "textarea"},
    }

    def __init__(self):
        self.trap_parameters = HarmonicTrapParameters()
        self.field_parameters = FieldParameters()
        self.cubic_parameters = CubicParameters()
        self.quartic_parameters = QuarticParameters()
        self.ion_string: str = "Ca40 * 2"
        self.plots = PlotDashboard()

    @trigger_update("mode_report")
    def solve(self):
        ion = self.trap_parameters.target_ion._get_ion()
        pot = mpot.HarmonicPaulTrapPotential(*self.trap_parameters._freqs(), ion=ion)

        if self.field_parameters.add_field:
            pot = pot + mpot.LinearPotential(self.field_parameters._fields())

        if self.cubic_parameters.add_cubic:
            pot = pot + mpot.CubicPotential(self.cubic_parameters.cubic_x * 1e12)

        if self.quartic_parameters.add_quartic:
            pot = pot + mpot.QuarticPotential(self.quartic_parameters.quartic_x * 1e18)

        ions = parse_ion_string(self.ion_string)
        # roi = (400e-6, 30e-6, 30e-6)
        n_ions = len(ions)
        x0 = init_crystal((0, 0, 0), dx=5e-6, n_ions=n_ions)
        self._results = mode_solver(pot, ions, x0)
        self.plots._update(self._results)
        self._mode_report = repr(self._results)
        print("solve done")

    @property
    def mode_report(self) -> str:
        return self._mode_report

    def __repr__(self):
        return "Mode Solver"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("PORT", help="Port number", type=int)
    args = parser.parse_args()
    saver = Saver("settings/mode_solver_settings.json")
    dashboard = saver(ModeSolverDashboard)()
    slapdash.run(
        dashboard,
        host="0.0.0.0",
        port=args.PORT,
        css=os.path.join(os.getcwd(), "custom.css"),
    )


if __name__ == "__main__":
    main()
