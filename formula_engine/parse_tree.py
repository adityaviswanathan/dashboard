#!/usr/bin/env python

'''
Encodes the parse tree for a functional expression and provides relevant
utilities to build and evaluate the parse tree from an input string.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

from parse_tree_node import ParseTreeNode, ParseTreeNodeType

class ParseTree(object):
    token_arg_start = '('
    token_arg_end = ')'
    token_arg_delimiter = ','

    def __init__(self, input_str):
        self.input = input_str
        self.root = None

    def evaluate_tree(self):
        '''
        Recursively evaluates the ParseTree.
        '''
        if self.root is None:
            self.build_tree()
        return self.root.evaluate()

    def build_tree(self):
        '''
        Builds a ParseTree over self.input by doing a linear scan of the input
        string and mutating the ParseTree in-place.
        '''
        stutter_index = 0
        self.root = curr = None
        for index, c in enumerate(self.input):
            if c == ParseTree.token_arg_start:
                func = ParseTreeNode(self.input[stutter_index:index].strip(),
                                     ParseTreeNodeType.FUNCTION,
                                     curr)
                if self.root is None:
                    self.root = func
                else:
                    curr.children.append(func)
                curr = func
                stutter_index = index + 1
            if c == ParseTree.token_arg_end:
                if stutter_index != index:
                    # Arg before delimiter must have been CONSTANT.
                    arg = ParseTreeNode(self.input[stutter_index:index].strip(),
                                        ParseTreeNodeType.CONSTANT,
                                        curr)
                    curr.children.append(arg)
                curr = curr.parent
                stutter_index = index + 1
            if c == ParseTree.token_arg_delimiter:
                if stutter_index != index:
                    # Arg before delimiter must have been CONSTANT.
                    arg = ParseTreeNode(self.input[stutter_index:index].strip(),
                                        ParseTreeNodeType.CONSTANT,
                                        curr)
                    curr.children.append(arg)
                stutter_index = index + 1
