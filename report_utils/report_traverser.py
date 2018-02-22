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

class Cell(object):
    def __init__(self, val, title, date):
        self.val = val
        self.title = title
        self.date = date

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

    @staticmethod
    def denoise_cell(cell):
        noise = ['$', ',']
        denoised = cell
        for frag in noise:
            denoised = denoised.replace(frag, '')
        return denoised

    def cell_to_float(self, cell):
        try:
            return Cell(float(ReportTraverser.denoise_cell(cell.val).strip()),
                        cell.title,
                        cell.date)
        except ValueError:
            raise Exception('Cannot convert ' + cell.val + ' to numeric')

    def cells_to_floats(self, cells, skips=False):
        floats = []
        for cell in cells:
            try:
                floats.append(self.cell_to_float(cell))
            except Exception:
                if skips:
                    continue
        return floats

    def get_dates(self):
        '''
        Returns a list of strings corresponding to the dates in the axis
        containing them.
        '''
        vals = []
        with open(self.file_name) as csv_file:
            if self.date_axis is Axis.ROW:
                for i, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if i == self.date_axis_index:
                        for col_index, col in enumerate(row):
                            if col_index < self.title_axis_index:
                                continue
                            vals.append(Cell(col, "", col))
                        break
            if self.date_axis is Axis.COL:
                for i, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if i < self.title_axis_index:
                        continue
                    for col_index, col in enumerate(row):
                        if col_index == self.date_axis_index:
                            vals.append(Cell(col, "", col))
                            break
        return vals

    def get_titles(self):
        '''
        Returns a list of strings corresponding to the titles in the axis
        containing them.
        '''
        vals = []
        with open(self.file_name) as csv_file:
            if self.title_axis is Axis.ROW:
                for i, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if i == self.title_axis_index:
                        for col_index, col in enumerate(row):
                            if col_index < self.date_axis_index:
                                continue
                            vals.append(Cell(col, col, ""))
                        break
            if self.title_axis is Axis.COL:
                for i, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if i < self.date_axis_index:
                        continue
                    for col_index, col in enumerate(row):
                        if col_index == self.title_axis_index:
                            vals.append(Cell(col, col, ""))
                            break
        return vals

    def get_cell_by_index(self, title_index, date_index):
        '''
        Returns a string corresponding to the cell addressed by @title_index and
        @date_index.
        '''
        # Cast args to int if not already typed correctly.
        try:
            int(title_index)
        except ValueError:
            raise Exception('Unable to cast supplied title_index ' + \
                title_index + ' to int.')
        try:
            int(date_index)
        except ValueError:
            raise Exception('Unable to cast supplied date_index ' + \
                date_index + ' to int.')
        title_index_int = int(title_index)
        date_index_int = int(date_index)
        if title_index_int < 0 or date_index_int < 0:
            return Cell(None, "", "")
        row_axis_index = (self.date_axis_index if self.date_axis is Axis.ROW
                          else self.title_axis_index)
        col_axis_index = (self.date_axis_index if self.date_axis is Axis.COL
                          else self.title_axis_index)
        row_to_find = row_axis_index + (date_index_in
                                        if self.date_axis is Axis.COL
                                        else title_index_int)
        col_to_find = col_axis_index + (date_index_int
                                        if self.date_axis is Axis.ROW
                                        else title_index_int)
        with open(self.file_name) as csv_file:
            for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                if row_index == row_to_find:
                    for col_index, col in enumerate(row):
                        if col_index == col_to_find:
                            return Cell(col,
                                        self.get_titles()[title_index_int],
                                        self.get_dates()[date_index_int])
        return Cell(None, "", "")

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

    def get_cells_by_date(self, date_text):
        vals = []
        with open(self.file_name) as csv_file:
            if self.date_axis is Axis.ROW:
                found_col_index = -1
                for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if row_index == self.date_axis_index:
                        for col_index, col in enumerate(row):
                            if col_index < self.title_axis_index:
                                continue
                            if col == date_text:
                                found_col_index = col_index
                                break
                    elif found_col_index >= 0:
                        for col_index, col in enumerate(row):
                            if col_index == found_col_index:
                                vals.append(Cell(col,
                                                 self.get_titles()[row_index - self.date_axis_index],
                                                 self.get_dates()[col_index - self.title_axis_index]))
            if self.date_axis is Axis.COL:
                found_row_index = False
                for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if found_row_index:
                        break
                    if row_index < self.title_axis_index:
                        continue
                    for col_index, col in enumerate(row):
                        if found_row_index:
                            vals.append(Cell(col,
                                             self.get_titles()[col_index - self.date_axis_index],
                                             self.get_dates()[row_index - self.title_axis_index]))
                        if col_index == self.date_axis_index and col == date_text:
                            found_row_index = True
        return vals

    def get_cells_by_title(self, title_text):
        vals = []
        with open(self.file_name) as csv_file:
            if self.title_axis is Axis.ROW:
                found_col_index = -1
                for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if row_index == self.title_axis_index:
                        for col_index, col in enumerate(row):
                            if col_index < self.date_axis_index:
                                continue
                            if col == title_text:
                                found_col_index = col_index
                                break
                    elif found_col_index >= 0:
                        for col_index, col in enumerate(row):
                            if col_index == found_col_index:
                                vals.append(Cell(col,
                                                 self.get_titles()[col_index - self.date_axis_index],
                                                 self.get_dates()[row_index - self.title_axis_index]))
            if self.title_axis is Axis.COL:
                found_row_index = False
                for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                    if found_row_index:
                        break
                    if row_index < self.date_axis_index:
                        continue
                    for col_index, col in enumerate(row):
                        if found_row_index:
                            vals.append(Cell(col,
                                             self.get_titles()[row_index - self.date_axis_index],
                                             self.get_dates()[col_index - self.title_axis_index]))
                        if col_index == self.title_axis_index and col == title_text:
                            found_row_index = True
        return vals
