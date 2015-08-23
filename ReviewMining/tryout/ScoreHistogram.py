__author__ = 'santhosh'

import matplotlib.pyplot as plt
import numpy
import os
from util import StatConstants


BINS = {StatConstants.RATING_ENTROPY: numpy.arange(0.0, 5.75, 0.25),\
        StatConstants.RATIO_OF_SINGLETONS: numpy.arange(0.0, 1.2, 0.1),\
        StatConstants.RATIO_OF_FIRST_TIMERS: numpy.arange(0.0, 1.2, 0.1),\
        StatConstants.YOUTH_SCORE: numpy.arange(0.0, 3.0, 0.15),\
        StatConstants.ENTROPY_SCORE: numpy.arange(0.0, 3.0, 0.25),
        StatConstants.NO_OF_POSITIVE_REVIEWS: numpy.arange(0.0, 500.0, 20),
        StatConstants.NO_OF_NEGATIVE_REVIEWS: numpy.arange(0.0, 500.0, 20),
        StatConstants.NON_CUM_NO_OF_REVIEWS: numpy.arange(0.0, 2000.0, 20)}
def getRangeIdxs(idx):
    start = 2
    end = 3
    while start < end:
        if idx - start < 0:
            start -= 1
        else:
            break
    return (idx-start, idx+end)

def doScoreHistogram(measure_scores):
    for key in measure_scores.keys():


        scores = measure_scores[key]

        max_score = max(scores)
        min_score = min(scores)
        bin_width = (max_score - min_score) / 10.0

        # if key in BINS:
        #     bins = BINS[key]
        #     if max_score > bins[-1]:
        #         bins = numpy.append(bins, [max_score])
        # else:
        bins = numpy.arange(min_score, max_score, bin_width)

        doHistogramForMeasure(bins, key, scores)


def doHistogramForMeasure(bins, key, scores):
    fig = plt.figure()
    plt.title('Score histogram')
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel(key)
    # ax.set_xticks(bins)
    # if key == StatConstants.NO_OF_NEGATIVE_REVIEWS or key == StatConstants.NO_OF_POSITIVE_REVIEWS\
    #     or key == StatConstants.NON_CUM_NO_OF_REVIEWS:
    #     ax.hist(scores, bins, alpha=1.00, label=key, log=True)
    # else:
    ax.hist(scores, bins, alpha=1.00, label=key)
    plt.show()


def readScores(plotDir):
    onlyfiles = [f for f in os.listdir(plotDir) if os.path.isfile(os.path.join(plotDir, f))]
    measure_scores = dict()
    for fil in onlyfiles:
        scores = []
        measure = fil.replace('.log', '')
        if measure == StatConstants.NON_CUM_NO_OF_REVIEWS or\
                        measure == StatConstants.NO_OF_REVIEWS or\
                        measure == StatConstants.AVERAGE_RATING:
            continue
        with open(os.path.join(plotDir, fil)) as f:
            string = f.read()
            scores = [float(s) for s in string.split()]

            # bins = BINS[measure]
            # max_score = max(scores)
            #
            # if max_score > bins[-1]:
            #     bins = numpy.append(bins, [max_score])

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
            diff_test_idxs = set()
            for idx in sorted(avg_idxs):
                idx1, idx2 = getRangeIdxs(idx)
                for indx in range(idx1, idx2+1):
                    diff_test_idxs.add(indx)

            for measure_key in chPtsOutliers.keys():
                if measure_key == StatConstants.AVERAGE_RATING\
                        or measure_key == StatConstants.NO_OF_REVIEWS or\
                                measure_key == 'BNSS_ID':
                    continue

                chPtsOutliersEntry = chPtsOutliers[measure_key]

                chOutlierIdxs, chOutlierScores = chPtsOutliersEntry

                # bins = BINS[measure_key]
                if measure_key not in measure_scores:
                    measure_scores[measure_key] = []

                # if measure_key in THRES:
                #     measure_scores[measure_key].extend([chOutlierScores[idx] for idx in range(len(chOutlierScores))\
                #                                         if chOutlierScores[idx] < THRES[measure_key]\
                #                                         and idx in diff_test_idxs])
                # else:
                test_measure_scores = [chOutlierScores[idx] for idx in range(len(chOutlierScores))\
                                                        if idx in diff_test_idxs]
                measure_scores[measure_key].extend(test_measure_scores)
    for measure_key in measure_scores.keys():
        print measure_key, max(measure_scores[measure_key]), min(measure_scores[measure_key])

    return measure_scores

DONT_CONSIDER = [StatConstants.NO_OF_NEGATIVE_REVIEWS, StatConstants.NO_OF_POSITIVE_REVIEWS,
                 StatConstants.NON_CUM_NO_OF_REVIEWS]
def print_hist_bins(measure_scores):
    for measure_key in measure_scores.keys():
        scores = measure_scores[measure_key]
        bins = BINS[measure_key]
        max_score = max(scores)
        # min_score = min(scores)
        # bin_width = (max_score - min_score) / 30.0
        # bins = numpy.arange(min_score, max_score, bin_width)

        # if max_score > bins[-1] and measure_key not in DONT_CONSIDER:
        #     bins = numpy.append(bins, [max_score])

        hist, bin_edges = numpy.histogram(scores, bins= bins, density=False)
        print '*********************************'
        print measure_key
        print [(hist[i], bin_edges[i]) for i in range(len(hist))], bin_edges[-1]

        print '*********************************'
        doHistogramForMeasure(bin_edges, measure_key, scores)


def main_fn():
    # scores = readScoresFromMeasureLog('/media/santhosh/Data/workspace/datalab/data/stats/s5/measure_scores.log')
    measure_scores = readScoresFromMeasureLog(
        '/media/santhosh/Data/workspace/datalab/data/stats/Local_AR/measure_scores.log')
    print_hist_bins(measure_scores)
    # print max(measure_scores1[StatConstants.ENTROPY_SCORE])
    # measure_scores2 = readScoresFromMeasureLog(
    #     '/media/santhosh/Data/workspace/datalab/data/stats/Global AR/measure_scores.log')
    # for measure_key in measure_scores1.keys():
    #     scores1 = measure_scores1[measure_key]
    #     scores2 = measure_scores2[measure_key]
    #     print measure_key
    #     print min(scores1), min(scores2)
    #     print max(scores1), max(scores2)
    # doScoreHistogram(measure_scores)
    # measure_scores2 = readScoresFromMeasureLog(
    #     '/media/santhosh/Data/workspace/datalab/data/stats/Local AR/measure_scores.log')
    # THRES_RANGE = StatConstants.RATING_ENTROPY: numpy.arange(0.25, 5),\
    #         StatConstants.RATIO_OF_SINGLETONS: numpy.arange(0.0, 1.0, 0.2),\
    #         StatConstants.RATIO_OF_FIRST_TIMERS: numpy.arange(0.0, 1.0, 0.2),\
    #         StatConstants.YOUTH_SCORE: numpy.arange(0.0, 3.0, 0.25),\
    #         StatConstants.ENTROPY_SCORE: numpy.arange(0.0, 6.0, 0.25)



main_fn()


