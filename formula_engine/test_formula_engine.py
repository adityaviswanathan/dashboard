#!/usr/bin/env python

'''
Tests ParseTree and downstream ParseTreeNode.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import os
import sys
import unittest
from parse_tree import ParseTree
# Append parent dir to $PYTHONPATH to import ReportTraverser, whose public
# methods have bindings into the ParseTreeNode.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
import report_utils

class ParseTreeBasic(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

    def test_basic(self):
        answers = {
            'Add(2,1)' : 3.0,
            'Subtract(2,1)' : 1.0,
            'Multiply(2,1)' : 2.0,
            'Divide(2,1)' : 2.0,
            'Multiply(2.5,    2.5)' : 6.25,
            'Count(2.5,    2.5, 4)' : 3.0,
            'Average(1, 2, 3)' : 2.0,
            'Average(2, 2.5, 3)' : 2.5,
        }
        for input_str, val in answers.iteritems():
            self.assertEqual(ParseTree(input_str).evaluate_tree(), val)

    def test_nesting(self):
        answers = {
            'Add(Add(2,1), Add(3,1))' : 7.0,
            'Subtract( Multiply(   2.5, 3.5), Add(3,     1))' : 4.75,
        }
        for input_str, val in answers.iteritems():
            self.assertEqual(ParseTree(input_str).evaluate_tree(), val)

    def test_varargs(self):
        answers = {
            'Add(1, 2.0, 3,  5, 7.5)' : 18.5,
            'Subtract( Add(2, 3), Add (3,4), Add(  4,5))' : -11,
        }
        for input_str, val in answers.iteritems():
            self.assertEqual(ParseTree(input_str).evaluate_tree(), val)

class ParseTreeTraverser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        data_file = open('testdata/cashflow_test.csv').name
        axis_decision = report_utils.AxisDecision(data_file)
        axis_decision.decide()
        self.traverser = report_utils.ReportTraverser(
            data_file,
            axis_decision.date_axis,
            axis_decision.date_index,
            axis_decision.title_axis,
            axis_decision.title_index)

    def test_traverser_bindings(self):
        answers = {
            'Count(get_dates())' : 14,
            'Count( get_titles (  )  )' : 51,
            'get_cell_by_text ( Late Fee, JAN 17  )' : 0,
            'Add(get_cell_by_text ( Late Fee, OCT 17  ), get_cell_by_index(5, 11))' : 510,
            'Ceiling(Average(get_cells_by_date(SEP 17)))' : 1122,
            'get_dates()' : 'Account Name' # Tests bogus case of call to
                                           # evaluate_tree without specifying
                                           # is_list flag. Ok to disable.
        }
        for input_str, val in answers.iteritems():
            self.assertEqual(
                ParseTree(input_str, self.traverser).evaluate_tree(), val)

    def test_list_response(self):
        answers = {
            'get_dates()' : ['Account Name', 'JAN 17', 'FEB 17', 'MAR 17',
                'APR 17', 'MAY 17', 'JUN 17', 'JUL 17', 'AUG 17', 'SEP 17',
                'OCT 17', 'NOV 17', 'DEC 17', 'Total']
        }
        for input_str, val in answers.iteritems():
            self.assertEqual(
                ParseTree(input_str, self.traverser).evaluate_tree(is_list=True), val)

if __name__ == '__main__':
    unittest.main()
