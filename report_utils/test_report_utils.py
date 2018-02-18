#!/usr/bin/env python

'''
Tests AxisDecision and ReportTraverser.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import argparse
import csv
import os
import sys
import unittest
from axis import Axis
from axis_decision import AxisDecision
from report_traverser import ReportTraverser

GOLDENS_NAME_SUFFIX = 'goldens'
LIST_START = '['
LIST_END = ']'
LIST_DELIMITER = ','
COL_DELIMITER = '|'
DEBUG = False
DATA_REACH_THRESH = 10

def file_exists(file_name, errmsg):
    try:
        f = open(file_name)
        f.close()
        return True
    except IOError:
        if DEBUG:
            print errmsg
        return False

def get_goldens_path(test_type):
    return (os.path.dirname(os.path.abspath(__file__)) + '/' +
        test_type + '_' + GOLDENS_NAME_SUFFIX + '.txt')

def write_test_results(goldens_path, goldens_folder, GoldensTestClass):
    print 'Emitting goldens for ' + str(GoldensTestClass.__name__) + '...'
    if not (hasattr(GoldensTestClass, 'goldens_headers') or
            hasattr(GoldensTestClass, 'run_goldens_test')):
        print ('Attempting to write goldens for undefined GoldensTestClass: ' +
                GoldensTestClass)
    with open(goldens_path, 'w') as goldens:
        csv_goldens = csv.writer(goldens, delimiter=COL_DELIMITER)
        csv_goldens.writerow(GoldensTestClass.goldens_headers())
        for f in os.listdir(goldens_folder):
            if f.endswith('.csv'):
                try:
                    csv_goldens.writerow(GoldensTestClass.run_goldens_test(
                        goldens_folder + '/' + f))
                except:
                    print ('Unable to identify date axis for ' +
                            goldens_folder + '/' + f)
                    continue
    print 'Done emitting goldens for ' + str(GoldensTestClass.__name__) + '.'

def run_goldens_test(goldens_folder):
    write_test_results(get_goldens_path('axis_decision'),
                       goldens_folder,
                       AxisDecisionGoldens)
    write_test_results(get_goldens_path('report_traverser'),
                       goldens_folder,
                       ReportTraverserGoldens)

def goldens_stub(name, args, value):
    l = LIST_DELIMITER.join([str(a) for a in args]) if len(args) > 0 else ''
    return name + '(' + l + ') = ' + str(value)

def goldens_append(curr_str, append_str):
    out_str = curr_str
    if out_str is not LIST_START:
        out_str += LIST_DELIMITER
    return out_str + append_str

class AxisDecisionGoldens(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.goldens_path = get_goldens_path('axis_decision')
        err = 'Goldens file ' + self.goldens_path + ' does not exist.'
        if not file_exists(self.goldens_path, err):
            raise unittest.SkipTest(err)

    def __str__(self):
        return "AxisDecisionGoldens"

    @staticmethod
    def goldens_headers():
        return (
            'filename',
            'date axis',
            'date index',
            'title axis',
            'title index')

    @staticmethod
    def run_goldens_test(file_name):
        axis_decision = AxisDecision(file_name)
        axis_decision.decide()
        return [
            file_name,
            str(axis_decision.date_axis),
            str(axis_decision.date_index),
            str(axis_decision.title_axis),
            str(axis_decision.title_index)]

    def test_goldens(self):
        with open(self.goldens_path, 'r') as goldens:
            csv_goldens = csv.reader(goldens, delimiter=COL_DELIMITER)
            for golden_test in csv_goldens:
                # TEST: ensure goldens file is well-formed.
                self.assertEqual(len(golden_test),
                                 len(AxisDecisionGoldens.goldens_headers()))
                file_name = golden_test[0]
                err = 'Cannot open file "' + file_name + '", skipping.'
                if not file_exists(file_name, err):
                    continue
                # TEST: run goldens test.
                self.assertEqual(golden_test, AxisDecisionGoldens.run_goldens_test(file_name))

class ReportTraverserGoldens(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.goldens_path = get_goldens_path('report_traverser')
        err = 'Goldens file ' + self.goldens_path + ' does not exist.'
        if not file_exists(self.goldens_path, err):
            raise unittest.SkipTest(err)

    def __str__(self):
        return "ReportTraverserGoldens"

    @staticmethod
    def goldens_headers():
        return (
            'filename',
            'get_cell_by_index values',
            'get_cell_by_text values',
            'get_cells_by_date values',
            'get_cells_by_title values',
            'get_dates values',
            'get_titles values')

    @staticmethod
    def run_goldens_test(file_name):
        axis_decision = AxisDecision(file_name)
        axis_decision.decide()
        traverser = ReportTraverser(file_name,
                                    axis_decision.date_axis,
                                    axis_decision.date_index,
                                    axis_decision.title_axis,
                                    axis_decision.title_index)
        # Generate representative strings for ReportTraverser's public methods:
        # 1) get_cell_by_index
        # 2) get_cell_by_text
        # 3) get_cells_by_date
        # 4) get_cells_by_title
        # 5) get_dates
        # 6) get_titles
        # This is done by computing these methods on @file_name.
        dates = traverser.get_dates()
        titles = traverser.get_titles()
        # Generate get_cell_by_index string code.
        get_cell_by_index_str = LIST_START
        for i in range(0, DATA_REACH_THRESH):
            for j in range(0, DATA_REACH_THRESH):
                val = traverser.get_cell_by_index(i, j)
                c = goldens_stub('get_cell_by_index', [i, j], val)
                get_cell_by_index_str = goldens_append(get_cell_by_index_str, c)
        get_cell_by_index_str += LIST_END
        # Generate get_cell_by_text string code.
        get_cell_by_text_str = LIST_START
        for date in dates:
            for title in titles:
                val = traverser.get_cell_by_text(title, date)
                c = goldens_stub('get_cell_by_text', [title, date], val)
                get_cell_by_text_str = goldens_append(get_cell_by_text_str, c)
        get_cell_by_text_str += LIST_END
        # Generate get_cells_by_date string code.
        get_cells_by_date_str = LIST_START
        for date in dates:
            val = traverser.get_cells_by_date(date)
            c = goldens_stub('get_cells_by_date', [date], val)
            get_cells_by_date_str = goldens_append(get_cells_by_date_str, c)
        get_cells_by_date_str += LIST_END
        # Generate get_cells_by_title string code.
        get_cells_by_title_str = LIST_START
        for title in titles:
            val = traverser.get_cells_by_title(title)
            c = goldens_stub('get_cells_by_title', [title], val)
            get_cells_by_title_str = goldens_append(get_cells_by_title_str, c)
        get_cells_by_title_str += LIST_END
        get_dates_str = goldens_stub(
            'get_dates', [], str(dates).replace(COL_DELIMITER, LIST_DELIMITER))
        get_titles_str = goldens_stub(
            'get_titles', [], str(titles).replace(COL_DELIMITER, LIST_DELIMITER))
        str_codes = [
            get_cell_by_index_str,
            get_cell_by_text_str,
            get_cells_by_date_str,
            get_cells_by_title_str,
            get_dates_str,
            get_titles_str]
        return [file_name] + str_codes

    def test_goldens(self):
        with open(self.goldens_path, 'r') as goldens:
            csv_goldens = csv.reader(goldens, delimiter=COL_DELIMITER)
            for golden_test in csv_goldens:
                # TEST: ensure goldens file is well-formed.
                self.assertEqual(len(golden_test),
                                 len(ReportTraverserGoldens.goldens_headers()))
                file_name = golden_test[0]
                err = 'Cannot open file "' + file_name + '", skipping.'
                if not file_exists(file_name, err):
                    continue
                # TEST: run goldens test.
                self.assertEqual(golden_test, ReportTraverserGoldens.run_goldens_test(file_name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--goldens', help='path from which goldens file will be generated')
    args = parser.parse_args()
    csv.field_size_limit(sys.maxsize)
    if args.goldens:
        run_goldens_test(args.goldens)
    else:
        unittest.main()
