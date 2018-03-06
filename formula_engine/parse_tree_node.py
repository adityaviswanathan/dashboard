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
# will need to cast to 0.0.
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

    def evaluate_with_args(self, args):
        return (Function.constant_func(self.val) \
                if self.type == ParseTreeNodeType.CONSTANT \
                else Function(self.val, self.traversers, self.parent).evaluate(args))

    def evaluate(self):
        if self.val not in Function.BINDINGS and len(self.children) > 0:
            args = []
            for c in self.children:
                if self.val in Function.LIST_FUNCTIONS:
                    args.append(c.evaluate())
                else:
                    args += c.evaluate()
            return self.evaluate_with_args(args)
        return self.evaluate_with_args(self.children)
