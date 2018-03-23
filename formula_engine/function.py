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
# methods have bindings into Function.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from report_utils import ReportTraverser, Cell

class Function(object):
    NAMES = set([
        'Add',
        'Subtract',
        'Multiply',
        'Divide',
        'FloorDivide',
        'GreaterThan',
        'GreaterEqualThan',
        'LessThan',
        'LessEqualThan',
        'Count',
        'Average',
        'Floor',
        'Ceiling',
        'Round',
        'get_dates',
        'get_titles',
        'get_cell_by_index',
        'get_cell_by_text',
        'get_cells_by_date',
        'get_cells_by_title',
        'VectorAdd',
        'VectorSubtract',
        'VectorMultiply',
        'VectorDivide',
        'VectorFloorDivide',
        'IfElse'
    ])
    # Returns a list of cells.
    LIST_BINDINGS = set([
        'get_dates',
        'get_titles',
        'get_cells_by_date',
        'get_cells_by_title'])
    # Expects list arguments.
    VECTOR_FUNCTIONS = set([
        'VectorAdd',
        'VectorSubtract',
        'VectorMultiply',
        'VectorDivide',
        'VectorFloorDivide'])
    # Expects numeric arguments. Skips arg if cast to numeric fails.
    NUMERIC_FUNCTIONS = set([
        'Add',
        'Subtract',
        'Multiply',
        'Divide',
        'FloorDivide',
        'VectorAdd',
        'VectorSubtract',
        'VectorMultiply',
        'VectorDivide',
        'VectorFloorDivide',
        'GreaterThan',
        'GreaterEqualThan',
        'LessThan',
        'LessEqualThan',
        'Average',
        'Floor',
        'Ceiling',
        'Round'])
    # Returns a singleton cell list.
    SINGLETON_BINDINGS = set([
        'get_cell_by_index',
        'get_cell_by_text'])
    # Returns items of type Cell.
    CELL_BINDINGS = set([
        'get_cells_by_date',
        'get_cells_by_title',
        'get_cell_by_index',
        'get_cell_by_text'])
    FUNCTION_ARGC = {
        'Floor' : 1,
        'Ceiling' : 1,
        'Round' : 2,
        'IfElse' : 3,
        'get_dates' : 1,
        'get_titles' : 1,
        'get_cell_by_index' : 3,
        'get_cell_by_text' : 3,
        'get_cells_by_date' : 2,
        'get_cells_by_title' : 2
    }
    BINDINGS = LIST_BINDINGS | SINGLETON_BINDINGS
    RETURNS_LIST = LIST_BINDINGS | VECTOR_FUNCTIONS

    @staticmethod
    def operator_func(n):
        '''
        Private helper that applies a well-defined Python built-in operator
        as a function to an argument list.
        '''
        return (lambda a : [ReportTraverser.cell_to_float(Cell(
            reduce(getattr(operator, n), [float(i.val) for i in a]),
            a[0].title,
            a[0].date))])

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
        fails = 0
        subtract_args = [self.function_defs['Count'](args)[0],
            Function.constant_func(fails)[0]]
        real_count = self.function_defs['Subtract'](subtract_args)[0]
        divide_args = [self.function_defs['Add'](args)[0], real_count]
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
        def dispatch(arr, is_list):
            traverser_index = int(float(arr[0].val)) # 1st arg is report index.
            traverser_args = arr[1:] if len(arr) > 1 else []
            # Execute the ReportTraverser binding.
            vals = lambda a : [i.val for i in a]
            res = getattr(self.traversers[traverser_index], n)(*vals(traverser_args))
            wrapped_res = res if is_list else [res]
            # Don't typecast to float if the caller does not require a numeric
            # response.
            if self.parent is None or self.parent.val not in Function.NUMERIC_FUNCTIONS:
                return wrapped_res
            return ReportTraverser.cells_to_floats(wrapped_res, True)

        return lambda a : dispatch(a, n in Function.LIST_BINDINGS)

    def if_else_func(self, args):
        # Expects boolean numeric as condition value.
        check_condition = lambda args : args[0].val > 0.0
        def success_case(args):
            # If the return value of the success block is list and this is not
            # the root node, then return the list itself instead of wrapping a
            # singleton.
            if isinstance(args[1], list) and self.parent is not None:
                return args[1]
            return [args[1]]
        def failure_case(args):
            # If the return value of the success block is list and this is not
            # the root node, then return the list itself instead of wrapping a
            # singleton.
            if isinstance(args[2], list) and self.parent is not None:
                return args[2]
            return [args[2]]
        return success_case(args) if check_condition(args) else failure_case(args)

    def is_recognized_function(self):
        return self.func_name in self.function_defs.keys()

    def __init__(self, func_name, traversers=[], parent=None):
        self.func_name = func_name
        self.traversers = traversers
        self.parent = parent

        self.function_defs = {
            'Add' : Function.operator_func('add'), # varargs.
            'Subtract' : Function.operator_func('sub'), # varargs.
            'Multiply' : Function.operator_func('mul'), # varargs.
            'Divide' : Function.operator_func('truediv'), # varargs.
            'FloorDivide' : Function.operator_func('floordiv'), # varargs.
            'GreaterThan' : Function.operator_func('gt'), # boolean (0/1) return type.
            'GreaterEqualThan' : Function.operator_func('ge'), # boolean (0/1) return type.
            'LessThan' : Function.operator_func('lt'), # boolean (0/1) return type.
            'LessEqualThan' : Function.operator_func('le'), # boolean (0/1) return type.
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
            'VectorFloorDivide' : Function.vector_operator_func('floordiv'),
            'IfElse' : self.if_else_func
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
