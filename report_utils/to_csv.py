#!/usr/bin/env python

'''
Converts report files to CSV format.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import csv
import os
import xlrd

def xlsx_to_csv(path_name, file_name, ext, folder=''):
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

def could_not_convert(path_name, file_name, ext, folder=''):
    raise Exception('Cannot convert file with extension {ext} to CSV'
        .format(ext=ext))

def to_csv(path, folder):
    name, ext = os.path.splitext(os.path.basename(path))
    if not os.path.exists(folder):
        os.makedirs(folder)
    switcher = {
        '.xlsx' : xlsx_to_csv
    }
    converter = switcher.get(ext, could_not_convert)
    return converter(path, name, ext, folder)
