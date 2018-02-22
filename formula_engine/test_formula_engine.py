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
            self.assertEqual(ParseTree(input_str).evaluate_tree().val, val)

    def test_nesting(self):
        answers = {
            'Add(Add(2,1), Add(3,1))' : 7.0,
            'Subtract( Multiply(   2.5, 3.5), Add(3,     1))' : 4.75,
        }
        for input_str, val in answers.iteritems():
            self.assertEqual(ParseTree(input_str).evaluate_tree().val, val)

    def test_varargs(self):
        answers = {
            'Add(1, 2.0, 3,  5, 7.5)' : 18.5,
            'Subtract( Add(2, 3), Add (3,4), Add(  4,5))' : -11,
        }
        for input_str, val in answers.iteritems():
            self.assertEqual(ParseTree(input_str).evaluate_tree().val, val)

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
        }
        for input_str, val in answers.iteritems():
            self.assertEqual(
                ParseTree(input_str, self.traverser).evaluate_tree().val, val)

    def test_list_response(self):
        answers = {
            'get_dates()' : ['Account Name', 'JAN 17', 'FEB 17'],
            'get_cells_by_title( Discount/Promotion)' : [0.0, 0.0, 0.0]
        }
        for input_str, val in answers.iteritems():
            res = ParseTree(input_str, self.traverser).evaluate_tree(is_list=True)
            self.assertGreaterEqual(len(res), 3)
            self.assertEqual([i.val for i in res][:3], val)
        answers = {
            'get_cells_by_date(SEP 17)' : [4634.00, 4600.0, 9234.0]
        }
        for input_str, val in answers.iteritems():
            res = ParseTree(input_str, self.traverser).evaluate_tree(is_list=True)
            self.assertGreaterEqual(len(res), 3)
            self.assertEqual([i.val for i in res][-3:], val)

    def test_title_annotations(self):
        answers = {
            'get_cells_by_date( JAN 17)' : [
                'Rent-Tempe',
                'Discount/Promotion',
                'Credit Card Fee paid by tenant'
            ],
            'get_cells_by_title( Discount/Promotion)' : [
                'Discount/Promotion',
                'Discount/Promotion',
                'Discount/Promotion'
            ]
        }
        for input_str, val in answers.iteritems():
            res = ParseTree(input_str, self.traverser).evaluate_tree(is_list=True)
            self.assertGreaterEqual(len(res), 3)
            self.assertEqual([i.title.val for i in res][:3], val)

    def test_date_annotations(self):
        answers = {
            'get_cells_by_date( JAN 17)' : ['JAN 17', 'JAN 17', 'JAN 17'],
            'get_cells_by_title( Discount/Promotion)' : ['JAN 17', 'FEB 17', 'MAR 17']
        }
        for input_str, val in answers.iteritems():
            res = ParseTree(input_str, self.traverser).evaluate_tree(is_list=True)
            self.assertGreaterEqual(len(res), 3)
            self.assertEqual([i.date.val for i in res][:3], val)

    def test_nested_annotations(self):
        q = 'Add(get_cell_by_index(2, 10), get_cell_by_index(3, 10))'
        res = ParseTree(q, self.traverser).evaluate_tree()
        self.assertEqual(res.val, 10309)
        self.assertEqual(res.date.val, 'OCT 17')
        # TODO(aditya): Establish and test well-defined behavior for differing
        # annotations in the case of singleton response (as above). Currently,
        # we merely use the annotation of the args[0] element.

if __name__ == '__main__':
    unittest.main()
