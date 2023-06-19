#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 05/2023
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>

import re
from enum import Enum
from trimos import ions as mions


class Ions(Enum):
    CA40 = 'Ca40'
    BE9 = 'Be9'
    MG24 = 'Mg24'
    BA137 = 'Ba137'
    YB171 = 'Yb171'

    def _get_ion(self):
        return getattr(mions, self.value)


def parse_ion_string(ion_string):
    ions_expr = "|".join([i.value for i in Ions])
    expr1 = f"({ions_expr})\s*\*\s*([0-9]+)"  # noqa
    expr2 = f"([0-9]+)\s*\*\s*({ions_expr})"  # noqa
    ions = []
    for name in ion_string.split(","):
        name = name.strip()
        m = re.fullmatch(ions_expr, name)
        if m:
            ions += [getattr(mions, name)]
            continue
        m = re.fullmatch(expr1, name)
        if m:
            name, n = m.groups()
            ions += int(n) * [getattr(mions, name)]
            continue
        m = re.fullmatch(expr2, name)
        if m:
            n, name = m.groups()
            ions += int(n) * [getattr(mions, name)]
            continue
    return ions
