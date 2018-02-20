#!/usr/bin/env python

'''
Data structure for accessing raw report data via date and/or titles. The
constructor expects information about the start indexes and axes of both
labels in order for this class to operate correctly.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import csv

from axis import Axis

class ReportTraverser(object):
    def __init__(
        self,
        file_name,
        date_axis=Axis.NONE,
        date_axis_index=-1,
        title_axis=Axis.NONE,
        title_axis_index=-1):
        if date_axis is Axis.NONE or title_axis is Axis.NONE:
            raise Exception('ReportTraverser requires both date and title axes')
        self.file_name = file_name
        self.date_axis = date_axis
        self.date_axis_index = date_axis_index
        self.title_axis = title_axis
        self.title_axis_index = title_axis_index

    def get_labels(self, axis, axis_index, other_axis_index):
        vals = []
        with open(self.file_name) as csv_file:
            if axis is Axis.ROW:
                for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if row_index == axis_index:
                        for col_index, col in enumerate(row):
                            if col_index < other_axis_index:
                                continue
                            vals.append(col)
                        break
            if axis is Axis.COL:
                for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if row_index < other_axis_index:
                        continue
                    for col_index, col in enumerate(row):
                        if col_index == axis_index:
                            vals.append(col)
                            break
        return vals

    def get_dates(self):
        '''
        Returns a list of strings corresponding to the dates in the axis
        containing them.
        '''
        return self.get_labels(self.date_axis, self.date_axis_index, self.title_axis_index)

    def get_titles(self):
        '''
        Returns a list of strings corresponding to the titles in the axis
        containing them.
        '''
        return self.get_labels(self.title_axis, self.title_axis_index, self.date_axis_index)

    def get_cell_by_index(self, title_index, date_index):
        '''
        Returns a string corresponding to the cell addressed by @title_index and
        @date_index.
        '''
        if title_index == -1 or date_index == -1:
            return None
        row_axis_index = (self.date_axis_index if self.date_axis is Axis.ROW
                          else self.title_axis_index)
        col_axis_index = (self.date_axis_index if self.date_axis is Axis.COL
                          else self.title_axis_index)
        row_to_find = row_axis_index + (date_index
                                        if self.date_axis is Axis.COL
                                        else title_index)
        col_to_find = col_axis_index + (date_index
                                        if self.date_axis is Axis.ROW
                                        else title_index)
        with open(self.file_name) as csv_file:
            for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                if row_index == row_to_find:
                    for col_index, col in enumerate(row):
                        if col_index == col_to_find:
                            return col
        return None

    def get_cell_by_text(self, title_text, date_text):
        row_axis_index = (self.date_axis_index if self.date_axis is Axis.ROW
                          else self.title_axis_index)
        col_axis_index = (self.date_axis_index if self.date_axis is Axis.COL
                          else self.title_axis_index)
        found_date_index = -1
        found_title_index = -1
        with open(self.file_name) as csv_file:
            for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                if found_date_index >= 0 and found_title_index >= 0:
                    break
                if row_index >= row_axis_index:
                    for col_index, col in enumerate(row):
                        if (col_index == col_axis_index and
                            self.date_axis is Axis.COL and
                            col == date_text):
                            found_date_index = row_index - row_axis_index
                        if (col_index == col_axis_index and
                            self.title_axis is Axis.COL and
                            col == title_text):
                            found_title_index = row_index - row_axis_index
                if row_index == row_axis_index:
                    for col_index, col in enumerate(row):
                        if self.date_axis is Axis.ROW and col == date_text:
                            found_date_index = col_index
                        if self.title_axis is Axis.ROW and col == title_text:
                            found_title_index = col_index
        return self.get_cell_by_index(found_title_index, found_date_index)

    def get_cells(self, text, axis, axis_index, other_axis_index):
        '''
        Returns a list of strings corresponding to the cells addressed by a
        @text filter for a given @axis. Also requires @axis_index and
        @other_axis_index to ensure only the values are returned.
        '''
        vals = []
        with open(self.file_name) as csv_file:
            if axis is Axis.ROW:
                found_col_index = -1
                for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if row_index == axis_index:
                        for col_index, col in enumerate(row):
                            if col_index < other_axis_index:
                                continue
                            if col == text:
                                found_col_index = col_index
                                break
                    elif found_col_index >= 0:
                        for col_index, col in enumerate(row):
                            if col_index == found_col_index:
                                vals.append(col)
            if axis is Axis.COL:
                found_row_index = False
                for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if found_row_index:
                        break
                    if row_index < other_axis_index:
                        continue
                    for col_index, col in enumerate(row):
                        if found_row_index:
                            vals.append(col)
                        if col_index == axis_index and col == text:
                            found_row_index = True
        return vals

    def get_cells_by_date(self, date_text):
       return self.get_cells(
            date_text,
            self.date_axis,
            self.date_axis_index,
            self.title_axis_index)

    def get_cells_by_title(self, title_text):
       return self.get_cells(
            title_text,
            self.title_axis,
            self.title_axis_index,
            self.date_axis_index)
