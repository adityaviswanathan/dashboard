#!/usr/bin/env python

'''
Utility to help decide if a particular axis likely contains date values and
therefore corresponds to the date (time) axis of the report.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import re

class DateAxisDecider:
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
        '({month} \d+)'
    ])

    @staticmethod
    def score(regexp, cell):
        match = re.search(regexp, cell)
        match_prefix = re.search(regexp, cell)
        # If entry matches a date pattern, score high.
        if match is not None:
            return 2 if match_prefix is not None else 1
        return 0

    def __init__(self, data):
        self.data = data
        self.entries_scores = []
        self.top_indexes = []

    def is_date_axis(self):
        self.score_entries()
        return len(self.top_indexes) > 0

    def score_cell(self, cell):
        entry_score = 0
        # If entry is an empty or all whitespace string, score low.
        if not cell.strip():
            return 0
        for pattern in (DateAxisDecider.formatted_patterns |
                        DateAxisDecider.unformatted_patterns):
            if pattern in DateAxisDecider.formatted_patterns:
                for mo in (DateAxisDecider.months1 | DateAxisDecider.months2):
                    regexp = re.compile(pattern.format(month=mo), re.IGNORECASE)
                    entry_score += self.score(regexp, cell)
            else:
                regexp = re.compile(pattern, re.IGNORECASE)
                entry_score += self.score(regexp, cell)
        return entry_score

    def score_entries(self):
        for index, entries in enumerate(self.data):
            # Score per-entries list is computed as the sum of all scores
            # in the list normalized by the size of the list. This way, a
            # single entry that has a very high score should not necessarily
            # yield a high entries list score since its contribution is blended
            # with that of the other entries in the list.
            s = sum([self.score_cell(e) for e in entries]) / float(len(entries))
            self.entries_scores.append(s)
        top_score = max(self.entries_scores)
        if top_score > 0.0:
            self.top_indexes = [i for i, _ in enumerate(self.entries_scores)
                                if self.entries_scores[i] == top_score]
