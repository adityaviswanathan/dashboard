#!/usr/bin/env python

'''
Defines the node for the parse tree. More importantly, implements recursive
evaluation of a node and defines all legal functions.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import enum
import os
import sys
from function import Function

# TODO(aditya): Handle None return values from ReportTraverser (in most cases
# will need to cast to 0.0).
# TODO(aditya): Handle divide by zero.
# TODO(aditya): Handle float arithmetic correctly. Python will return
# approximate floating point values for float arithmetic instead of the real,
# expected value.

class ParseTreeNodeType(enum.Enum):
    CONSTANT = 0
    FUNCTION = 1

class ParseTreeNode(object):
    def __init__(self, val, node_type, traversers, parent):
        self.val = val
        self.type = node_type
        self.traversers = traversers
        self.parent = parent
        self.children = []
        self.is_list = False

    def set_is_list(self, is_list):
        self.is_list = is_list

    def evaluate_with_args(self, args):
        f = Function(self.val, self.traversers, self.parent)
        # If the function to be evaluated is IfElse and the caller requests
        # a return value of list, we need to return the list which is the first
        # and only element in the response from Function.
        if self.val == 'IfElse' and self.is_list:
            return f.evaluate(args)[0]
        return (Function.constant_func(self.val) \
                if self.type == ParseTreeNodeType.CONSTANT \
                else f.evaluate(args))

    def evaluate(self):
        # Specially handles arguments for IfElse. In particular, the first arg
        # is a boolean numeric condition whereas the following two args are
        # success/failure blocks that are substituted depending on the outcome
        # of the condition.
        def insert_if_else_arg(child, child_index, args):
            if self.val == 'IfElse':
                if child_index > 0 and child.val in Function.RETURNS_LIST:
                    args.append(child.evaluate())
                else:
                    args += child.evaluate()
                return True
            return False

        if self.val not in Function.BINDINGS and len(self.children) > 0:
            args = []
            for child_index, child in enumerate(self.children):
                # Handle IfElse function args.
                if insert_if_else_arg(child, child_index, args):
                    continue
                # Append the list responses from vector functions to @args.
                elif self.val in Function.VECTOR_FUNCTIONS:
                    args.append(child.evaluate())
                # Merge the list responses from non-vector functions to @args.
                else:
                    args += child.evaluate()
            return self.evaluate_with_args(args)
        return self.evaluate_with_args(self.children)
