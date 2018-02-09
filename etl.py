#!/usr/bin/env python

'''
Handles ETL (extraction, transformation, and load) on a rolling rent collection
financial report.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import argparse
import csv
import os
import xlrd

import report_utils

OUT_FOLDER = 'out'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='run ETL on a supplied file')
    args = parser.parse_args()
    data_file = report_utils.to_csv(args.file, OUT_FOLDER)

    # Algo:
    # A rolling rent collection report, at a high level, is a 2D matrix with
    # time on one axis and row titles on the other. Well-formed extraction of
    # data necessitates the following:
    #
    # a) Mapping each axis to either time or row title.
    # b) Computing the start index of both time and row title.

    axis_decision = report_utils.AxisDecision(data_file)
    axis_decision.decide()
    traverser = report_utils.ReportTraverser(
        data_file,
        axis_decision.date_axis,
        axis_decision.date_index,
        axis_decision.title_axis,
        axis_decision.title_index)

if __name__ == '__main__':
    main()
