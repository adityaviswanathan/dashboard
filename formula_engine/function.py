#!/usr/bin/env python

'''
Defines functions that can be evaluated in ParseTreeNode.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import math
import operator
import os
import sys
# Append parent dir to $PYTHONPATH to import ReportTraverser, whose public
# methods have bindings into the ParseTreeNode.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from report_utils import Cell

class Function(object):
    LIST_BINDINGS = set(['get_dates', 'get_titles', 'get_cells_by_date', 'get_cells_by_title'])
    LIST_FUNCTIONS = set(['VectorAdd', 'VectorSubtract', 'VectorMultiply', 'VectorDivide', 'VectorFloorDivide'])
    SINGLETON_BINDINGS = set(['get_cell_by_index', 'get_cell_by_text'])
    CELL_BINDINGS = set([
        'get_cells_by_date',
        'get_cells_by_title',
        'get_cell_by_index',
        'get_cell_by_text'])
    BINDINGS = LIST_BINDINGS | SINGLETON_BINDINGS

    @staticmethod
    def operator_func(n):
        '''
        Private helper that applies a well-defined Python built-in operator
        as a function to an argument list.
        '''
        return (lambda a : [Cell(
            reduce(getattr(operator, n), [float(i.val) for i in a]),
            a[0].title,
            a[0].date)])

    @staticmethod
    def vector_operator_func(n):
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

    @staticmethod
    def constant_func(val):
        return [Cell(val, None)]

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
        if n in Function.SINGLETON_BINDINGS:
            # If return type of ReportTraverser method is a singleton, we need to
            # convert the returned string into its equivalent float value before
            # continuing evaluation, which is handled via
            # ReportTraverser.cell_to_float().
            return lambda a : [self.traverser.cell_to_float(
                getattr(self.traverser, n)(*[i.val for i in a]))]
        if n in Function.LIST_BINDINGS:
            if n in Function.CELL_BINDINGS:
                return lambda a : self.traverser.cells_to_floats(
                    getattr(self.traverser, n)(*[i.val for i in a]), True)
            return lambda a : getattr(self.traverser, n)(*[i.val for i in a])

    FUNCTION_ARGC = {
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

    def is_recognized_function(self):
        return self.func_name in self.function_defs.keys()

    def __init__(self, func_name, traverser):
        self.func_name = func_name
        self.traverser = traverser
        self.function_defs = {
            'Add' : Function.operator_func('add'), # varargs.
            'Subtract' : Function.operator_func('sub'), # varargs.
            'Multiply' : Function.operator_func('mul'), # varargs.
            'Divide' : Function.operator_func('truediv'), # varargs.
            'FloorDivide' : Function.operator_func('floordiv'), # varargs.
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
            'VectorAdd' : Function.vector_operator_func('add'),
            'VectorSubtract' : Function.vector_operator_func('sub'),
            'VectorMultiply' : Function.vector_operator_func('mul'),
            'VectorDivide' : Function.vector_operator_func('truediv'),
            'VectorFloorDivide' : Function.vector_operator_func('floordiv')
        }

    def evaluate(self, args=[]):
        if not self.is_recognized_function():
            raise Exception(
                'Cannot find definition for function "' + self.func_name + '".')
        if self.func_name in Function.FUNCTION_ARGC and \
                len(args) != Function.FUNCTION_ARGC[self.func_name]:
            raise Exception(
                'Expected ' + str(Function.FUNCTION_ARGC[self.func_name]) + \
                ' args for ' + self.func_name + ', found ' + \
                str(len(args)) + ' (' + str(args) + ').')
        return self.function_defs[self.func_name](args)
