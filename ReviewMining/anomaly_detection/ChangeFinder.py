__author__ = 'Santhosh'

import numpy
import statsmodels.api as sm

class ChangeFinder(object):
    def __init__(self, r=0.7, order=2, smooth=4):
        assert order > 0
        assert smooth > 2
        self.ts = []
        self.first_scores = []
        self.second_scores = []
        self.first_pass = sm.tsa.AR(r, self._order)
        self.second_pass = sm.tsa.AR(r, self._order)

    def update(self, x):
        score = 0
        pass