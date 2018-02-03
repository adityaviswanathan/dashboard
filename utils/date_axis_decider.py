#!/usr/bin/env python

'''
Utility to help decide if a particular axis likely contains date values and
therefore corresponds to the date (time) axis of the report.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import re
from decider import Decider

class DateAxisDecider(Decider):
    months1 = set([
        'january',
        'february',
        'march',
        'april',
        'may',
        'june',
        'july',
        'august',
        'september',
        'october',
        'november',
        'december',
    ])
    months2 = set([
        'jan',
        'feb',
        'mar',
        'apr',
        'may',
        'jun',
        'jul',
        'aug',
        'sep',
        'oct',
        'nov',
        'dec'
    ])
    unformatted_patterns = set([
        '(\d+/\d+/\d+)'
    ])
    formatted_patterns = set([
        '({month} \d+)',
        '(.*{month}.*)'
    ])

    @staticmethod
    def score(regstr, cell):
        regexp = re.compile(regstr, re.IGNORECASE)
        match = re.search(regexp, cell)
        match_prefix = re.match(regexp, cell)
        # If entry matches a date pattern, score high.
        if match is not None:
            return 2 if match_prefix is not None else 1
        return 0

    def score_cell(self, cell):
        entry_score = 0
        # If entry is an empty or all whitespace string, score low.
        if not cell.strip():
            return 0
        for pattern in (DateAxisDecider.formatted_patterns |
                        DateAxisDecider.unformatted_patterns):
            if pattern in DateAxisDecider.formatted_patterns:
                for mo in (DateAxisDecider.months1 |
                           DateAxisDecider.months2):
                    entry_score += self.score(pattern.format(month=mo), cell)
            else:
                entry_score += self.score(pattern, cell)
        return entry_score
