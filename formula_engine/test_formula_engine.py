#!/usr/bin/env python

'''
Tests ParseTree and downstream ParseTreeNode.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import unittest
from parse_tree import ParseTree

class ParseTreeTest(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
