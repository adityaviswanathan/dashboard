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

def file_exists(file_name, errmsg):
    try:
        f = open(file_name)
        f.close()
        return True
    except IOError:
        print errmsg
        return False

def t2l(tup):
    return [str(i) for i in tup]

def get_goldens_path(test_type):
    return (os.path.dirname(os.path.abspath(__file__)) + '/' +
        test_type + '_' + GOLDENS_NAME_SUFFIX + '.txt')

def write_test_results(goldens_path, goldens_folder, GoldensTestClass):
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
            'minichksum')

    @staticmethod
    def write_goldens(file_name):
        axis_decision = AxisDecision(file_name)
        axis_decision.decide()
        traverser = ReportTraverser(file_name,
                                    axis_decision.date_axis,
                                    axis_decision.date_index,
                                    axis_decision.title_axis,
                                    axis_decision.title_index)
        minichksum = (traverser.get_cell_by_index(0, 0) +
                      traverser.get_cell_by_index(1, 0) +
                      traverser.get_cell_by_index(0, 1) +
                      traverser.get_cell_by_index(1, 1))
        return (file_name, minichksum)

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
                # self.assertEqual(golden_test, found)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--goldens', help='path from which goldens file will be generated')
    args = parser.parse_args()
    if args.goldens:
        write_goldens(args.goldens)
    else:
        unittest.main()
