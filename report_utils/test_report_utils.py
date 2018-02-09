#!/usr/bin/env python

'''
Tests AxisDecision and ReportTraverser.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import argparse
import csv
import os
import unittest
from axis import Axis
from axis_decision import AxisDecision
from report_traverser import ReportTraverser

GOLDENS_NAME_SUFFIX = 'goldens'
DEBUG = False
HASH_DIGITS = 10
DATA_REACH_THRESH = 10
DATE_SEARCH = "January"
TITLE_SEARCH = "Cost"

def file_exists(file_name, errmsg):
    try:
        f = open(file_name)
        f.close()
        return True
    except IOError:
        if DEBUG:
            print errmsg
        return False

def t2l(tup):
    return [str(i) for i in tup]

def get_goldens_path(test_type):
    return (os.path.dirname(os.path.abspath(__file__)) + '/' +
        test_type + '_' + GOLDENS_NAME_SUFFIX + '.txt')

def write_test_results(goldens_path, goldens_folder, GoldensTestClass):
    print 'Emitting goldens for ' + str(GoldensTestClass.__name__) + '...'
    if not (hasattr(GoldensTestClass, 'goldens_headers') or
            hasattr(GoldensTestClass, 'write_goldens')):
        print ('Attempting to write goldens for undefined GoldensTestClass: ' +
                GoldensTestClass)
    with open(goldens_path, 'w') as goldens:
        csv_goldens = csv.writer(goldens)
        csv_goldens.writerow(GoldensTestClass.goldens_headers())
        for f in os.listdir(goldens_folder):
            if f.endswith('.csv'):
                try:
                    csv_goldens.writerow(GoldensTestClass.write_goldens(
                        goldens_folder + '/' + f))
                except:
                    print ('Unable to identify date axis for ' +
                            goldens_folder + '/' + f)
                    continue
    print 'Done emitting goldens for ' + str(GoldensTestClass.__name__) + '...'

def write_goldens(goldens_folder):
    write_test_results(get_goldens_path('axis_decision'),
                       goldens_folder,
                       AxisDecisionGoldens)
    write_test_results(get_goldens_path('report_traverser'),
                       goldens_folder,
                       ReportTraverserGoldens)

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
    def write_goldens(file_name):
        axis_decision = AxisDecision(file_name)
        axis_decision.decide()
        return (
            file_name,
            axis_decision.date_axis,
            axis_decision.date_index,
            axis_decision.title_axis,
            axis_decision.title_index)

    def test_goldens(self):
        with open(self.goldens_path, 'r') as goldens:
            csv_goldens = csv.reader(goldens, delimiter=',')
            for golden_test in csv_goldens:
                # TEST: ensure goldens file is well-formed.
                self.assertEqual(len(golden_test),
                                 len(AxisDecisionGoldens.goldens_headers()))
                file_name = golden_test[0]
                err = 'Cannot open file "' + file_name + '", skipping.'
                if not file_exists(file_name, err):
                    continue
                found = t2l(AxisDecisionGoldens.write_goldens(file_name))
                # TEST: run goldens test.
                self.assertEqual(golden_test, found)

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
            'get_cell_by_index hashcode',
            'get_cell_by_text hashcode',
            'get_cells_by_date hashcode',
            'get_cells_by_title hashcode',
            'get_dates hashcode',
            'get_titles hashcode')

    @staticmethod
    def write_goldens(file_name):
        axis_decision = AxisDecision(file_name)
        axis_decision.decide()
        traverser = ReportTraverser(file_name,
                                    axis_decision.date_axis,
                                    axis_decision.date_index,
                                    axis_decision.title_axis,
                                    axis_decision.title_index)
        # Generate representative hashes for ReportTraverser's public methods:
        # 1) get_cell_by_index
        # 2) get_cell_by_text
        # 3) get_cells_by_date
        # 4) get_cells_by_title
        # 5) get_dates
        # 6) get_titles
        # This is done by computing these methods on @file_name on some fixed
        # parameters currently specified as globals in this file. Note that
        # these fixed parameters do not necessarily exhaustively test a
        # particular method and that goldens-based tests are really sanity
        # checks for these methods.
        get_cell_by_index_str = ''
        get_cell_by_text_str = ''
        for i in range(0, DATA_REACH_THRESH):
            for j in range(0, DATA_REACH_THRESH):
                get_cell_by_index_str += str(traverser.get_cell_by_index(i, j))
                get_cell_by_text_str += str(
                    traverser.get_cell_by_text(TITLE_SEARCH, DATE_SEARCH))
        dates = traverser.get_dates()
        titles = traverser.get_titles()
        # Lets search for cells based on a known legal date/title value. We
        # will not throw an out-of-bounds error below because dates is
        # guaranteed to be non-empty at this point (if ReportTraverser was
        # successfully constructed).
        get_cells_by_date_str = str(traverser.get_cells_by_date(dates[0]))
        get_cells_by_title_str = str(traverser.get_cells_by_title(titles[0]))
        str_codes = [
            get_cell_by_index_str,
            get_cell_by_text_str,
            get_cells_by_date_str,
            get_cells_by_title_str,
            str(dates),
            str(titles)]
        file_codes = [abs(hash(i)) % (10 ** HASH_DIGITS) for i in str_codes]
        return tuple([file_name] + file_codes)

    def test_goldens(self):
        with open(self.goldens_path, 'r') as goldens:
            csv_goldens = csv.reader(goldens, delimiter=',')
            for golden_test in csv_goldens:
                # TEST: ensure goldens file is well-formed.
                self.assertEqual(len(golden_test),
                                 len(ReportTraverserGoldens.goldens_headers()))
                file_name = golden_test[0]
                err = 'Cannot open file "' + file_name + '", skipping.'
                if not file_exists(file_name, err):
                    continue
                found = t2l(ReportTraverserGoldens.write_goldens(file_name))
                # TEST: run goldens test.
                self.assertEqual(golden_test, found)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--goldens', help='path from which goldens file will be generated')
    args = parser.parse_args()
    if args.goldens:
        write_goldens(args.goldens)
    else:
        unittest.main()
