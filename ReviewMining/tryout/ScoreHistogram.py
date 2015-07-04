__author__ = 'santhosh'

import matplotlib.pyplot as plt
import numpy
import os
from util import StatConstants

def doScoreHistogram(measure_scores):

    for key in measure_scores.keys():
        fig = plt.figure()
        plt.title('Score histogram')

        scores = measure_scores[key]

        max_score = max(scores)
        min_score = min(scores)

        bins = numpy.linspace(min_score, max_score, 100)

        ax = fig.add_subplot(1, 1, 1)

        ax.set_xlabel(key)

        ax.hist(scores, bins, alpha=0.25, label=key)

        plt.show()


def readScores(plotDir):
    onlyfiles = [f for f in os.listdir(plotDir) if os.path.isfile(os.path.join(plotDir, f))]
    measure_scores = dict()
    for fil in onlyfiles:
        scores = []
        measure = fil.replace('.log', '')
        if measure == StatConstants.NON_CUM_NO_OF_REVIEWS or measure == StatConstants.NO_OF_REVIEWS:
            continue
        with open(os.path.join(plotDir, fil)) as f:
            string = f.read()
            scores = [float(s) for s in string.split() if float(s) > 0]
        measure_scores[measure] = scores
    return measure_scores


measure_scores = readScores('/media/santhosh/Data/workspace/datalab/data/stats/s2/')
doScoreHistogram(measure_scores)