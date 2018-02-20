#!/usr/bin/env python

'''
Defines the node for the parse tree. More importantly, implements recursive
evaluation of a node and defines all legal functions.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import enum
import operator
import os
import sys
# Append parent dir to $PYTHONPATH to import ReportTraverser, whose public
# methods have bindings into the ParseTreeNode.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
import report_utils

# TODO(aditya): Handle None return values from ReportTraverser (in most cases
# will need to cast to 0.0.

class ParseTreeNodeType(enum.Enum):
    CONSTANT = 0
    FUNCTION = 1

class ParseTreeNode(object):
    BINDINGS = set(['get_dates', 'get_cell_by_text'])
    def operator_func(self, n):
        '''
        Private helper that applies a well-defined Python built-in operator
        as a function to an argument list.
        '''
        return lambda a : [reduce(getattr(operator, n), [float(i) for i in a])]

    def average_func(self, args):
        divide_args = [self.function_defs['Add'](args)[0],
            self.function_defs['Count'](args)[0]]
        return self.function_defs['Divide'](divide_args)

    def cells_to_nodes(self, cells):
        return [ParseTreeNode(cell,
                              ParseTreeNodeType.CONSTANT,
                              self.traverser,
                              None) for cell in cells]

    def get_dates(self, args):
        return self.cells_to_nodes(self.traverser.get_dates())

    def get_cell_by_text(self, args):
        return self.cells_to_nodes(
            [self.traverser.get_cell_by_text(*[a.val for a in args])])

    def __init__(self, val, node_type, traverser, parent):
        self.val = val
        self.type = node_type
        self.parent = parent
        self.traverser = traverser
        self.children = []
        # Defines a mapping of function names to lambdas that execute during
        # parse tree unfolding. The type contract for lambda I/O behavior is
        # that both inputs and outputs are lists. Analytical functions cast
        # inputs to numeric values during execution.
        self.function_defs = {
            'Add' : self.operator_func('add'), # varargs.
            'Subtract' : self.operator_func('sub'), # varargs.
            'Multiply' : self.operator_func('mul'), # varargs.
            'Divide' : self.operator_func('truediv'), # varargs.
            'FloorDivide' : self.operator_func('floordiv'), # varargs.
            'Count' : lambda a : [len(a)], # varargs.
            'Average' : self.average_func, # varargs.
            'get_dates' : self.get_dates,
            'get_cell_by_text' : self.get_cell_by_text
        }

    def evaluate_with_args(self, args):
        if self.type == ParseTreeNodeType.CONSTANT:
            return [self.val]
        if self.val not in self.function_defs:
            raise Exception(
                'Cannot find definition for function "' + self.val  + '".')
        return self.function_defs[self.val](args)

    def evaluate(self):
        if self.val not in ParseTreeNode.BINDINGS and len(self.children) > 0:
            args = []
            for c in self.children:
                args += c.evaluate()
            return self.evaluate_with_args(args)
        return self.evaluate_with_args(self.children)
