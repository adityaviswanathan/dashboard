#!/usr/bin/env python

'''
Encodes the parse tree for a functional expression and provides relevant
utilities to build and evaluate the parse tree from an input string.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

from parse_tree_node import ParseTreeNode, ParseTreeNodeType

class ParseTree(object):
    TOKEN_ARG_START = '('
    TOKEN_ARG_END = ')'
    TOKEN_ARG_DELIMITER = ','

    def __init__(self, input_str, traversers=[]):
        self.input = input_str
        self.traversers = traversers
        self.root = None

    @staticmethod
    def evaluate_trees(trees):
        vals = []
        for tree in trees:
            vals.append(tree.evaluate_tree(is_list=False))
        return vals

    def evaluate_tree(self, is_list=False):
        '''
        Recursively evaluates the ParseTree.
        '''
        if self.root is None:
            self.build_tree()
        self.root.set_is_list(is_list)
        if is_list:
            return self.root.evaluate()
        return self.root.evaluate()[0]

    def build_tree(self):
        '''
        Builds a ParseTree over self.input by doing a linear scan of the input
        string and mutating the ParseTree in-place.
        '''
        stutter = 0
        self.root = curr = None
        for index, c in enumerate(self.input):
            if c == ParseTree.TOKEN_ARG_START:
                func = ParseTreeNode(self.input[stutter:index].strip(),
                                     ParseTreeNodeType.FUNCTION,
                                     self.traversers,
                                     curr)
                if self.root is None:
                    self.root = func
                else:
                    curr.children.append(func)
                curr = func
                stutter = index + 1
            elif c == ParseTree.TOKEN_ARG_END:
                if stutter != index and self.input[stutter:index].strip():
                    # Arg before delimiter must have been CONSTANT.
                    arg = ParseTreeNode(self.input[stutter:index].strip(),
                                        ParseTreeNodeType.CONSTANT,
                                        self.traversers,
                                        curr)
                    curr.children.append(arg)
                curr = curr.parent
                stutter = index + 1
            elif c == ParseTree.TOKEN_ARG_DELIMITER:
                if stutter != index:
                    # Arg before delimiter must have been CONSTANT.
                    arg = ParseTreeNode(self.input[stutter:index].strip(),
                                        ParseTreeNodeType.CONSTANT,
                                        self.traversers,
                                        curr)
                    curr.children.append(arg)
                stutter = index + 1
