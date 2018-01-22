#!/usr/bin/env python

'''
Enum representation of report axis.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import enum

class Axis(enum.Enum):
    NONE = 0
    ROW = 1
    COL = 2
