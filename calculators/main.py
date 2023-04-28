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


@Saver('settings.json')
class Calculators:

    voltage: float = 0.0
    power: bool = False

    def reset(self):
        self.voltage = 0.0

    def __repr__(self):
        return "calculators"


def main():
    plugin = Calculators()
    slapdash.run(plugin,
                 host='0.0.0.0',
                 port=PORT,
                 css=os.path.join(os.getcwd(), 'custom.css')
                 )


if __name__ == "__main__":
    main()
