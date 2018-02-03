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

from utils import AxisDecision, DateAxisDecider, ReportTraverser, Axis

OUT_FOLDER = 'out'

def convert_to_csv(path_name, file_name, ext, folder=''):
    if (ext == '.xlsx'):
        wb = xlrd.open_workbook(path_name)
        # Below is a HACK that assumes the first sheet in the excel workbook
        # is the one that is to be processed.
        sheet = wb.sheet_by_index(0)
        csv_file = open((folder + '/' if folder else folder) +
                        file_name + '.csv', 'w')
        csv_file_name = os.path.basename(csv_file.name)
        if os.path.isfile(csv_file.name):
            print('Overwriting existing CSV file ' + csv_file_name + '.');
        csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        print('Converting {name}.{ext} to CSV via temp file {csv}'
               .format(name=file_name, ext=ext, csv=csv_file_name))
        for row_index in range(sheet.nrows):
            csv_writer.writerow(sheet.row_values(row_index))
        csv_file.close()
        return csv_file.name
    else:
        raise Exception('Cannot convert file with extension {ext} to CSV'
                         .format(ext=ext))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='run ETL on a supplied file')
    args = parser.parse_args()

    data_file = args.file
    name, ext = os.path.splitext(os.path.basename(data_file))
    if (ext != '.csv'):
        if not os.path.exists(OUT_FOLDER):
            os.makedirs(OUT_FOLDER)
        data_file = convert_to_csv(args.file, name, ext, OUT_FOLDER)

    # Algo:
    # A rolling rent collection report, at a high level, is a 2D matrix with
    # time on one axis and row titles on the other. Well-formed extraction of
    # data necessitates the following:
    #
    # a) Mapping each axis to either time or row title.
    # b) Computing the start index of both time and row title.

    axis_decision = AxisDecision(data_file)
    axis_decision.decide()
    traverser = ReportTraverser(
        data_file,
        axis_decision.date_axis,
        axis_decision.date_index,
        axis_decision.title_axis,
        axis_decision.title_index)

if __name__ == '__main__':
    main()
