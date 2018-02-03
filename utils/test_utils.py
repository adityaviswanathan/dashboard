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

def get_goldens_path(test_type):
    return (os.path.dirname(os.path.abspath(__file__)) + '/' +
        test_type + '_' + GOLDENS_NAME_SUFFIX + '.txt')

def write_goldens(goldens_folder):
    goldens_path = get_goldens_path('axis_decider')
    with open(goldens_path, 'w') as goldens:
        csv_goldens = csv.writer(goldens)
        csv_goldens.writerow((
            'file',
            'date_axis',
            'date_index',
            'title_axis',
            'title_index'))
        for f in os.listdir(goldens_folder):
            if f.endswith('.csv'):
                try:
                    axis_decider = AxisDecider(goldens_folder + '/' + f)
                    axis_decider.decide()
                    csv_goldens.writerow((
                        goldens_folder + '/' + f,
                        axis_decider.date_axis,
                        axis_decider.date_index,
                        axis_decider.title_axis,
                        axis_decider.title_index))
                except:
                    print ('Unable to identify date axis for ' +
                            goldens_folder + '/' + f)
                    continue

class AxisDeciderGoldens(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.goldens_path = get_goldens_path('axis_decision')
        err = 'Goldens file ' + self.goldens_path + ' does not exist.'
        if not file_exists(self.goldens_path, err):
            raise unittest.SkipTest(err)

    def test_goldens(self):
        with open(self.goldens_path, 'r') as goldens:
            csv_goldens = csv.reader(goldens, delimiter=',')
            for golden_test in csv_goldens:
                # TEST: ensure goldens file is well-formed.
                self.assertEqual(len(golden_test), 5)
                file_name = golden_test[0]
                err = 'Cannot open file "' + file_name + '", skipping.'
                if not file_exists(file_name, err):
                    continue
                axis_decision = AxisDecision(file_name)
                axis_decision.decide()
                found = [str(i) for i in (
                    axis_decision.date_axis,
                    axis_decision.date_index,
                    axis_decision.title_axis,
                    axis_decision.title_index)]
                # TEST: run goldens test.
                self.assertEqual(golden_test[1:], found)

class ReportTraverserGoldens(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.goldens_path = get_goldens_path('report_traverser')
        err = 'Goldens file ' + self.goldens_path + ' does not exist.'
        if not file_exists(self.goldens_path, err):
            raise unittest.SkipTest(err)

    def test_goldens(self):
        with open(self.goldens_path, 'r') as goldens:
            csv_goldens = csv.reader(goldens, delimiter=',')
            for golden_test in csv_goldens:
                # TEST: ensure goldens file is well-formed.
                self.assertEqual(len(golden_test), 5)
                file_name = golden_test[0]
                try:
                    f = open(file_name)
                    f.close()
                except IOError:
                    print 'Cannot open file "' + file_name + '", skipping.'
                    continue
                axis_decision = AxisDecision(file_name)
                axis_decision.decide()
                found = [str(i) for i in (
                    axis_decision.date_axis,
                    axis_decision.date_index,
                    axis_decision.title_axis,
                    axis_decision.title_index)]
                # TEST: run goldens test.
                self.assertEqual(golden_test[1:], found)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--goldens', help='path from which goldens file will be generated')
    args = parser.parse_args()
    if args.goldens:
        write_goldens(args.goldens)
    else:
        unittest.main()
