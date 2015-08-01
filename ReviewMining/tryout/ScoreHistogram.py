__author__ = 'santhosh'

import matplotlib.pyplot as plt
import numpy
import os
from util import StatConstants


THRES = {StatConstants.ENTROPY_SCORE: 1090.0}

BINS = {StatConstants.RATING_ENTROPY: numpy.arange(0.0, 15.0, 0.25),\
        StatConstants.RATIO_OF_SINGLETONS: numpy.arange(0.0, 1.0, 0.2),\
        StatConstants.RATIO_OF_FIRST_TIMERS: numpy.arange(0.0, 1.0, 0.2),\
        StatConstants.YOUTH_SCORE: numpy.arange(0.0, 3.0, 0.25),\
        StatConstants.ENTROPY_SCORE: numpy.arange(0.0, 6.0, 0.25)}

def doScoreHistogram(measure_scores):
    for key in measure_scores.keys():
        fig = plt.figure()
        plt.title('Score histogram')

        scores = measure_scores[key]

        max_score = max(scores)
        min_score = min(scores)

        bins = BINS[key]

        if max_score > bins[-1]:
            bins = numpy.append(bins, [max_score])

        ax = fig.add_subplot(1, 1, 1)

        ax.set_xlabel(key)
        # ax.set_xticks(bins)

        ax.hist(scores, bins, alpha=1.00, label=key)

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
            scores = [float(s) for s in string.split() if float(s) < 1090]

            bins = BINS[measure]
            max_score = max(scores)

            if max_score > bins[-1]:
                bins = numpy.append(bins, [max_score])

        #     anom_scores = [float(s) for s in string.split() if float(s) > THRES[measure]]
        # #     print measure, len(anom_scores)
        #     if len(anom_scores) > 0:
        #         print measure, len(anom_scores)
        #         print sorted(anom_scores)
        #         print max(anom_scores)
            measure_scores[measure] = scores
    return measure_scores

def readScoresFromMeasureLog(measure_log):
    import re
    chPtsOutliers = dict()
    measure_scores = dict()
    with open(measure_log) as f:
        string = f.read()
        p = re.compile('[{][^{]+[}]')
        strings = p.findall(string)
        for string in strings:
            string = "chPtsOutliers="+string
            exec(string)

            avg_idxs, chOutlierScores = chPtsOutliers[StatConstants.AVERAGE_RATING]
            from anomaly_detection import AnomalyDetector
            diff_test_idxs = set()
            for idx in sorted(avg_idxs):
                idx1, idx2 = AnomalyDetector.getRangeIdxs(idx)
                for indx in range(idx1, idx2+1):
                    diff_test_idxs.add(indx)

            for measure_key in chPtsOutliers.keys():
                if measure_key == StatConstants.AVERAGE_RATING or measure_key not in BINS:
                    continue

                chOutlierIdxs, chOutlierScores = chPtsOutliers[measure_key]

                # bins = BINS[measure_key]
                if measure_key not in measure_scores:
                    measure_scores[measure_key] = []

                if measure_key in THRES:
                    measure_scores[measure_key].extend([chOutlierScores[idx] for idx in range(len(chOutlierScores))\
                                                        if chOutlierScores[idx] < THRES[measure_key]\
                                                        and idx in diff_test_idxs])
                else:

                    measure_scores[measure_key].extend([chOutlierScores[idx] for idx in range(len(chOutlierScores))\
                                                        if idx in diff_test_idxs])

    return measure_scores


def print_hist_bins(measure_scores):
    for measure_key in measure_scores.keys():
        scores = measure_scores[measure_key]
        bins = BINS[measure_key]
        max_score = max(scores)

        if max_score > bins[-1]:
            bins = numpy.append(bins, [max_score])

        hist, bin_edges = numpy.histogram(scores, bins=bins, density=False)
        print '*********************************'
        print measure_key
        print hist
        print bin_edges
        print '*********************************'


def main_fn():
    # scores = readScoresFromMeasureLog('/media/santhosh/Data/workspace/datalab/data/stats/s5/measure_scores.log')
    measure_scores1 = readScoresFromMeasureLog(
        '/media/santhosh/Data/workspace/datalab/data/stats/measure_scores.log')
    # measure_scores2 = readScoresFromMeasureLog(
    #     '/media/santhosh/Data/workspace/datalab/data/stats/Global AR/measure_scores.log')
    # for measure_key in measure_scores1.keys():
    #     scores1 = measure_scores1[measure_key]
    #     scores2 = measure_scores2[measure_key]
    #     print measure_key
    #     print min(scores1), min(scores2)
    #     print max(scores1), max(scores2)
    doScoreHistogram(measure_scores1)
    # measure_scores2 = readScoresFromMeasureLog(
    #     '/media/santhosh/Data/workspace/datalab/data/stats/Local AR/measure_scores.log')
    # THRES_RANGE = StatConstants.RATING_ENTROPY: numpy.arange(0.25, 5),\
    #         StatConstants.RATIO_OF_SINGLETONS: numpy.arange(0.0, 1.0, 0.2),\
    #         StatConstants.RATIO_OF_FIRST_TIMERS: numpy.arange(0.0, 1.0, 0.2),\
    #         StatConstants.YOUTH_SCORE: numpy.arange(0.0, 3.0, 0.25),\
    #         StatConstants.ENTROPY_SCORE: numpy.arange(0.0, 6.0, 0.25)



main_fn()


