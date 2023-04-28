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
from slapdash import Saver

PORT = 8001


@Saver('settings/mode_solver_settings.json')
class ModeSolver:

    voltage: float = 0.0
    power: bool = False

    def reset(self):
        self.voltage = 0.0

    def __repr__(self):
        return "Mode Solver"


def main():
    plugin = ModeSolver()
    slapdash.run(plugin,
                 host='0.0.0.0',
                 port=PORT,
                 css=os.path.join(os.getcwd(), 'custom.css')
                 )


if __name__ == "__main__":
    main()
