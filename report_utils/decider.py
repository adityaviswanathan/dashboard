#!/usr/bin/env python

'''
Base class for deciders.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

class Decider(object):
    def __init__(self, data):
        self.data = data
        self.entries_scores = []
        self.top_indexes = []

    def is_axis(self):
        self.score_entries()
        return len(self.top_indexes) > 0

    def score_entries(self):
        for index, entries in enumerate(self.data):
            s = sum([self.score_cell(e) for e in entries]) / \
                    float(len(entries))
            self.entries_scores.append(s)
        if len(self.entries_scores) == 0:
            return
        top_score = max(self.entries_scores)
        if top_score >= 0.0:
            self.top_indexes = [i for i, _ in enumerate(self.entries_scores)
                                if self.entries_scores[i] == top_score]

    def score_cell(self, cell):
        pass
