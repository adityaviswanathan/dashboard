#!/usr/bin/env python

'''
Defines the node for the parse tree. More importantly, implements recursive
evaluation of a node and defines all legal functions.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import enum
import operator

class ParseTreeNodeType(enum.Enum):
    CONSTANT = 0
    FUNCTION = 1

class ParseTreeNode(object):
    def operator_func(n):
        '''
        Private helper that applies a well-defined Python built-in operator
        as a function to an argument list.
        '''
        return lambda a : reduce(getattr(operator, n), [float(c) for c in a])

    def average_func(args):
        divide_args = (ParseTreeNode.function_defs['Add'](args),
             ParseTreeNode.function_defs['Count'](args))
        return ParseTreeNode.function_defs['Divide'](divide_args)

    function_defs = {
        'Add' : operator_func('add'), # varargs.
        'Subtract' : operator_func('sub'), # varargs.
        'Multiply' : operator_func('mul'), # varargs.
        'Divide' : operator_func('truediv'), # varargs.
        'FloorDivide' : operator_func('floordiv'), # varargs.
        'Count' : lambda a : len(a), # varargs.
        'Average' : average_func # varargs.
    }
    # TODO(aditya): extend @function_defs with bindings to ReportTraverser
    # API so that we can parse both analytical function names and
    # ReportTraverser function names in ParseTree traversal.

    def __init__(self, val, node_type, parent):
        self.val = val
        self.type = node_type
        self.parent = parent
        self.children = []

    def evaluate_with_args(self, args):
        if self.type == ParseTreeNodeType.CONSTANT:
            return self.val
        if self.val not in ParseTreeNode.function_defs:
            raise Exception(
                'Cannot find definition for function "' + self.val  + '".')
        return ParseTreeNode.function_defs[self.val](args)

    def evaluate(self):
        if len(self.children) > 0:
            return self.evaluate_with_args([c.evaluate() for c in self.children])
        return self.evaluate_with_args([])
