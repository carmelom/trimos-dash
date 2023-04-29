#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created: 03/2023
# Author: Carmelo Mordini <cmordini@phys.ethz.ch>
""" Define common types
"""
from typing import List, Tuple
from nptyping import NDArray, Shape, Float

Position = NDArray[Shape["3"], Float]
NCoords = NDArray[Shape["N, 3"], Float]
NData = NDArray[Shape["N"], Float]
Roi = NDArray[Shape["3"], Float]
Bounds = List[Tuple[float, float]]
