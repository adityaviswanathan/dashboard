#!/usr/bin/env python

'''
Utility to help decide which data each axis corresponds to based on a variety
of axis deciders.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

from axis import Axis
import csv
from date_axis_decider import DateAxisDecider
from title_axis_decider import TitleAxisDecider

class AxisDecision(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.row_values = []
        self.col_values = []
        self.index_values()
        self.date_axis = Axis.NONE
        self.date_index = -1
        self.title_axis = Axis.NONE
        self.title_index = -1

    def index_values(self):
        # Underlying data indexed by either row or col.
        with open(self.file_name) as csv_file:
            for row_index, row in enumerate(csv.reader(csv_file, delimiter=',')):
                self.row_values.append([])
                for col_index, col in enumerate(row):
                    self.row_values[row_index].append(col)
                    if len(self.col_values)-1 < col_index:
                        self.col_values.append([])
                    self.col_values[col_index].append(col)

    @staticmethod
    def find_axis(row_decider, col_decider):
        if row_decider.is_axis() and col_decider.is_axis():
            row_index = row_decider.top_indexes[0]
            col_index = col_decider.top_indexes[0]
            if (row_decider.entries_scores[row_index] >
                col_decider.entries_scores[col_index]):
                return (Axis.ROW, row_decider)
        elif row_decider.is_axis():
            return (Axis.ROW, row_decider)
        elif col_decider.is_axis():
            return (Axis.COL, col_decider)
        return (Axis.NONE, None)

    def find_date_axis(self):
        row_date_decider = DateAxisDecider(self.row_values)
        col_date_decider = DateAxisDecider(self.col_values)
        return AxisDecision.find_axis(row_date_decider, col_date_decider)

    def find_title_axis(self):
        row_title_decider = TitleAxisDecider(self.row_values)
        col_title_decider = TitleAxisDecider(self.col_values)
        return AxisDecision.find_axis(
            row_title_decider, col_title_decider)

    def decide(self):
        self.date_axis, date_axis_metadata = self.find_date_axis()
        self.title_axis, title_axis_metadata = self.find_title_axis()
        if self.date_axis is Axis.NONE:
            raise Exception('Unable to identify date axis of report file {csv}'
                             .format(csv=self.file_name))
        self.date_index = date_axis_metadata.top_indexes[0]
        if self.title_axis is Axis.NONE:
            # Unable to auto-assign title axis, resorting to picking
            # axis opposite to date axis.
            self.title_axis = Axis.opposite(self.date_axis)
            self.title_index = 0
        else:
            self.title_index = title_axis_metadata.top_indexes[0]
        # HACK: ensure title axis is not the same as date axis and if so,
        # prefer DateAxisDecider and pick the title axis to be the
        # opposite axis.
        if self.title_axis is self.date_axis:
            self.title_axis = Axis.opposite(self.date_axis)
