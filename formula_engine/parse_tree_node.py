#!/usr/bin/env python

'''
Defines the node for the parse tree. More importantly, implements recursive
evaluation of a node and defines all legal functions.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import enum
import math
import operator
import os
import sys

# TODO(aditya): Handle None return values from ReportTraverser (in most cases
# will need to cast to 0.0.
# TODO(aditya): Handle argc validation to function names. For ex. 'Floor' and
# 'Ceiling' functions both expect strictly one argument and we should throw an
# error or warning if such a contract is disobeyed during execution.

class ParseTreeNodeType(enum.Enum):
    CONSTANT = 0
    FUNCTION = 1

class ParseTreeNode(object):
    LIST_BINDINGS = set(['get_dates', 'get_titles', 'get_cells_by_date', 'get_cells_by_title'])
    SINGLETON_BINDINGS = set(['get_cell_by_index', 'get_cell_by_text'])
    BINDING_IS_NUMERIC = {
        'get_dates' : False,
        'get_titles' : False,
        'get_cells_by_date' : True,
        'get_cells_by_title' : True,
        'get_cell_by_index' : True,
        'get_cell_by_text' : True
    }
    BINDINGS = LIST_BINDINGS | SINGLETON_BINDINGS
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

    def traverser_func(self, n):
        '''
        Private helper that maps @n to its corresponding API in
        ReportTraverser. In the case of singleton responses, we return a
        singleton list. The ReportTraverser API returns cells in string form,
        but these strings need to be converted to numeric during evaluation,
        which is handled here. In the case we cannot safely convert a
        particular cell to numeric, we skip over it.
        '''
        # TODO(aditya): Handle typecast skips more gracefully. As of now, this
        # will cause integrity bugs for composition functions like 'Average'.
        # For ex. if we computed Average over a list of k string values where
        # we were only able to successfully convert j < k values to numeric,
        # we would in reality be computing the Sum of those j values divided by
        # k, when in reality the Sum of j values should be divided by j.
        if n in ParseTreeNode.SINGLETON_BINDINGS:
            # If return type of ReportTraverser method is a singleton, we need to
            # convert the returned string into its equivalent float value before
            # continuing evaluation, which is handled via
            # ReportTraverser.cell_to_float().
            return lambda a : [self.traverser.cell_to_float(
                getattr(self.traverser, n)(*[i.val for i in a]))]
        if n in ParseTreeNode.LIST_BINDINGS:
            if ParseTreeNode.BINDING_IS_NUMERIC[n]:
                return lambda a : self.traverser.cells_to_floats(
                    getattr(self.traverser, n)(*[i.val for i in a]), True)
            else:
                return lambda a : getattr(self.traverser, n)(*[i.val for i in a])

    def __init__(self, val, node_type, traverser, parent):
        self.val = val
        self.type = node_type
        self.traverser = traverser
        self.parent = parent
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
            'Floor' : lambda a : [math.floor(a[0])],
            'Ceiling' : lambda a : [math.ceil(a[0])],
            'get_dates' : self.traverser_func('get_dates'),
            'get_titles' : self.traverser_func('get_titles'),
            'get_cell_by_index' : self.traverser_func('get_cell_by_index'),
            'get_cell_by_text' : self.traverser_func('get_cell_by_text'),
            'get_cells_by_date' : self.traverser_func('get_cells_by_date'),
            'get_cells_by_title' : self.traverser_func('get_cells_by_title')
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
