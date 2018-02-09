#!/usr/bin/env python

'''
Utility to help decide if a particular axis likely contains title values and
therefore corresponds to the title axis of the report.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import re
from decider import Decider

class TitleAxisDecider(Decider):
    neg_patterns = set([
        '\d+'
        # '.*\d+' # e.g. "JUNE 2017" but this is very flaky.
    ])
    def score(self, regstr, cell):
        regexp = re.compile(regstr, re.IGNORECASE)
        match_prefix = re.match(regexp, cell)
        # If entry matches a date pattern, score high.
        return 1 if match_prefix is not None else 0

    def score_cell(self, cell):
        entry_score = 0
        # If entry is an empty or all whitespace string, score low.
        if not cell.strip():
            return 0
        for pattern in (TitleAxisDecider.neg_patterns):
            entry_score -= self.score(pattern, cell)
        return entry_score
