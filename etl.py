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

from utils import DateAxisDecider, ReportTraverser, Axis

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
        print('Converting {name}.{ext} to CSV via temp file {csv}.'
               .format(name=file_name, ext=ext, csv=csv_file_name))
        for row_index in range(sheet.nrows):
            csv_writer.writerow(sheet.row_values(row_index))
        csv_file.close()
        return csv_file.name
    else:
        raise Exception('Cannot convert file with extension {ext} to CSV'
                         .format(ext=ext))

def axis_detection(file_name):
    # Underlying data indexed by either row or col.
    row_values = []
    col_values = []
    with open(file_name) as csv_file:
        for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
            row_values.append([])
            for col_index, col in enumerate(row):
                row_values[row_index].append(col)
                if len(col_values)-1 < col_index:
                    col_values.append([])
                col_values[col_index].append(col)
    row_date_decider = DateAxisDecider(row_values)
    col_date_decider = DateAxisDecider(col_values)
    if row_date_decider.is_date_axis() and col_date_decider.is_date_axis():
        row_index = row_date_decider.top_indexes[0]
        col_index = col_date_decider.top_indexes[0]
        if (row_date_decider.entries_scores[row_index] >
            col_date_decider.entries_scores[col_index]):
            return (Axis.ROW, row_date_decider)
    elif row_date_decider.is_date_axis():
        return (Axis.ROW, row_date_decider)
    elif col_date_decider.is_date_axis():
        return (Axis.COL, col_date_decider)
    return (Axis.NONE, None)

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

    date_axis, date_axis_metadata = axis_detection(data_file)
    if date_axis is Axis.NONE:
        raise Exception('Unable to identify date axis of report file {csv}'
                         .format(csv=data_file))

    # Below is a HACK that sets the title axis as the opposite axis to whatever
    # is decided to be the date axis.
    title_axis = Axis.COL if date_axis is Axis.ROW else Axis.ROW

    traverser = ReportTraverser(
        data_file,
        date_axis,
        date_axis_metadata.top_indexes[0],
        title_axis,
        0)

    # TODO(aditya): test traverser on variety of reports.

if __name__ == '__main__':
    main()
