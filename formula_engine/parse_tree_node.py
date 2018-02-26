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
# Append parent dir to $PYTHONPATH to import ReportTraverser, whose public
# methods have bindings into the ParseTreeNode.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from report_utils import Cell

# TODO(aditya): Handle None return values from ReportTraverser (in most cases
# will need to cast to 0.0.
# TODO(aditya): Handle divide by zero.
# TODO(aditya): Handle float arithmetic correctly. Python will return
# approximate floating point values for float arithmetic instead of the real,
# expected value.

class ParseTreeNodeType(enum.Enum):
    CONSTANT = 0
    FUNCTION = 1

class ParseTreeNode(object):
    LIST_BINDINGS = set(['get_dates', 'get_titles', 'get_cells_by_date', 'get_cells_by_title'])
    LIST_FUNCTIONS = set(['VectorAdd', 'VectorSubtract', 'VectorMultiply', 'VectorDivide', 'VectorFloorDivide'])
    SINGLETON_BINDINGS = set(['get_cell_by_index', 'get_cell_by_text'])
    CELL_BINDINGS = set([
        'get_cells_by_date',
        'get_cells_by_title',
        'get_cell_by_index',
        'get_cell_by_text'])
    BINDINGS = LIST_BINDINGS | SINGLETON_BINDINGS
    def operator_func(self, n):
        '''
        Private helper that applies a well-defined Python built-in operator
        as a function to an argument list.
        '''
        return (lambda a : [Cell(
            reduce(getattr(operator, n), [float(i.val) for i in a]),
            a[0].title,
            a[0].date)])

    def vector_operator_func(self, n):
        def sparse(veclist):
            maxlen = max(map(len, veclist))
            sparse_veclist = []
            # Append zeros (make sparse) to any vector whose length is less
            # than maxlen.
            for vec in veclist:
                sparse_veclist.append(
                    vec + [Cell(0)]*(maxlen - len(vec)))
            return sparse_veclist

        def flatten(sparse_veclist):
            flattened_vec = []
            # All vectors are the same length at the time of this call, so we
            # can safely resort to the length of the first vector in the list
            # of vectors.
            for i in range(0, len(sparse_veclist[0])):
                flattened_vec.append(Cell(
                    reduce(getattr(operator, n),
                           [float(vec[i].val) for vec in sparse_veclist]),
                    sparse_veclist[0][0].title,
                    sparse_veclist[0][0].date))
            return flattened_vec

        # Args list @a is a list of vectors of cells.
        return lambda a : [flatten(sparse(a))]

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
            if n in ParseTreeNode.CELL_BINDINGS:
                return lambda a : self.traverser.cells_to_floats(
                    getattr(self.traverser, n)(*[i.val for i in a]), True)
            return lambda a : getattr(self.traverser, n)(*[i.val for i in a])

    def evaluate_function(self, func_name):
        return self.function_defs[func_name]

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
        # TODO(aditya): Abstract away these function definitions into a cleaner
        # interface.
        self.function_defs = {
            'Add' : self.operator_func('add'), # varargs.
            'Subtract' : self.operator_func('sub'), # varargs.
            'Multiply' : self.operator_func('mul'), # varargs.
            'Divide' : self.operator_func('truediv'), # varargs.
            'FloorDivide' : self.operator_func('floordiv'), # varargs.
            'Count' : (lambda a : [Cell(
                len(a),
                a[0].title if len(a) > 0 else Cell(None),
                a[0].date if len(a) > 0 else Cell(None))]), # varargs.
            'Average' : self.average_func, # varargs.
            'Floor' : (lambda a : [Cell(
                math.floor(float(a[0].val)),
                a[0].title,
                a[0].date)]),
            'Ceiling' : (lambda a : [Cell(
                math.ceil(float(a[0].val)),
                a[0].title,
                a[0].date)]),
            'Round' : (lambda a : [Cell(
                round(float(a[0].val), int(a[1].val)),
                a[0].title,
                a[0].date)]),
            'get_dates' : self.traverser_func('get_dates'),
            'get_titles' : self.traverser_func('get_titles'),
            'get_cell_by_index' : self.traverser_func('get_cell_by_index'),
            'get_cell_by_text' : self.traverser_func('get_cell_by_text'),
            'get_cells_by_date' : self.traverser_func('get_cells_by_date'),
            'get_cells_by_title' : self.traverser_func('get_cells_by_title'),
            'VectorAdd' : self.vector_operator_func('add'),
            'VectorSubtract' : self.vector_operator_func('sub'),
            'VectorMultiply' : self.vector_operator_func('mul'),
            'VectorDivide' : self.vector_operator_func('truediv'),
            'VectorFloorDivide' : self.vector_operator_func('floordiv')
        }
        self.function_argc = {
            'Floor' : 1,
            'Ceiling' : 1,
            'Round' : 2,
            'get_dates' : 0,
            'get_titles' : 0,
            'get_cell_by_index' : 2,
            'get_cell_by_text' : 2,
            'get_cells_by_date' : 1,
            'get_cells_by_title' : 1
        }

    def evaluate_with_args(self, args):
        if self.type == ParseTreeNodeType.CONSTANT:
            return [Cell(self.val, None)]
        if self.val not in self.function_defs:
            raise Exception(
                'Cannot find definition for function "' + self.val  + '".')
        if self.val in self.function_argc and \
            len(args) != self.function_argc[self.val]:
            raise Exception(
                'Expected ' + str(self.function_argc[self.val]) + ' args for ' +
                self.val + ', found ' + str(len(args)) + ' (' + str(args) + ').')
        return self.evaluate_function(self.val)(args)

    def evaluate(self):
        if self.val not in ParseTreeNode.BINDINGS and len(self.children) > 0:
            args = []
            for c in self.children:
                if self.val in ParseTreeNode.LIST_FUNCTIONS:
                    args.append(c.evaluate())
                else:
                    args += c.evaluate()
            return self.evaluate_with_args(args)
        return self.evaluate_with_args(self.children)
