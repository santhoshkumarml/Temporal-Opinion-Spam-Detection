__author__ = 'santhosh'

import numpy
import matplotlib.pyplot as plt
from anomaly_detection import AnomalyDetector
from util import StatConstants
from anomaly_detection import cusum
from anomaly_detection import ChangeFinder as cfr

CHPT_CONST_INCREASE = 'INCREASE_CONSTANT'
CHPT_CONST_DECREASE = 'DECREASE_CONSTANT'
CHPT_NORMAL_INCREASE = 'INCREASE_NORMAL'
CHPT_NORMAL_DECREASE = 'DECREASE_NORMAL'
OUTLIER_INCREASE = 'OUTLIER_INCREASE'
OUTLIER_DECREASE = 'OUTLIER_DECREASE'


AR = 'AR'
ARMA = 'ARMA'

def plotDataAndChanges(data, scores=[], changes=[]):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(range(len(data)), data, 'b')

    if len(scores) > 0:
        ax2 = ax.twinx()
        ax2.plot(range(len(scores)), scores,'r')

    for idx in changes:
        ax.axvline(x=idx, linewidth=2, color='r')

    plt.show()


def makeNormalData(mean=0.7, varaince =0.05, data_size=200, induced_outlier_or_chpts=[]):
    data = numpy.random.normal(mean, varaince, data_size)
    outlier_ch_idxs_visited = set()
    for idx in range(len(induced_outlier_or_chpts)):
        induced_outlier_ch_idx, induced_outlier_ch_magnitude, persistence_time, outlier_ch_type = induced_outlier_or_chpts[idx]

        assert induced_outlier_ch_idx not in outlier_ch_idxs_visited
        if outlier_ch_type == OUTLIER_INCREASE or outlier_ch_type == OUTLIER_DECREASE:
            assert persistence_time == 1
            if outlier_ch_type == OUTLIER_INCREASE:
                data[induced_outlier_ch_idx] = mean+induced_outlier_ch_magnitude
            else:
                data[induced_outlier_ch_idx] = mean-induced_outlier_ch_magnitude
            outlier_ch_idxs_visited.add(induced_outlier_ch_idx)
        elif outlier_ch_type == CHPT_CONST_INCREASE:
            start = induced_outlier_ch_idx
            end = start+persistence_time
            val = data[start-1] if start >=1 else mean
            data[start:end] = val+induced_outlier_ch_magnitude
            outlier_ch_idxs_visited |= set([indx for indx in range(start, end)])
        elif outlier_ch_type == CHPT_CONST_DECREASE:
            start = induced_outlier_ch_idx
            end = start+persistence_time
            val = data[start-1] if start >=1 else mean
            data[start:end] = val-induced_outlier_ch_magnitude
            outlier_ch_idxs_visited |= set([indx for indx in range(start, end)])
        elif outlier_ch_type == CHPT_NORMAL_INCREASE:
            start = induced_outlier_ch_idx
            end = start+persistence_time
            val = data[start-1] if start >=1 else mean
            data[start:end] = numpy.random.normal(val+induced_outlier_ch_magnitude, varaince, persistence_time)
            outlier_ch_idxs_visited |= set([indx for indx in range(start, end)])
        elif outlier_ch_type == CHPT_NORMAL_DECREASE:
            start = induced_outlier_ch_idx
            end = start+persistence_time
            val = data[start-1] if start >=1 else mean
            data[start:end] = numpy.random.normal(val-induced_outlier_ch_magnitude, varaince, persistence_time)
            outlier_ch_idxs_visited |= set([indx for indx in range(start, end)])
    return data


def runChangeFinder(data, algo):
    if algo == AR:
        r, order, smooth = 0.2, 2, 4
        cf = cfr.ChangeFinder(r, order, smooth)
    else:
        term, smooth, order = 4, 3, (2, 0)
        cf = cfr.ChangeFinderARIMA(term, smooth, order)

    change_scores = []
    for i in range(len(data)):
        score = cf.update(data[i])
        change_scores.append(score)
    chOutlierScores = change_scores
    return chOutlierScores


change_scores = []

data1 = makeNormalData(0.07, 0.05, 200,\
                      induced_outlier_or_chpts=[(100,2,20,CHPT_NORMAL_INCREASE),\
                                                (140,3,20,CHPT_NORMAL_INCREASE)])

change_scores1 = runChangeFinder(data1, 'ARMA')
plotDataAndChanges(data1, scores=change_scores1)

data2 = makeNormalData(0.07, 0.05, 200,\
                      induced_outlier_or_chpts=[(100,2,20,CHPT_NORMAL_INCREASE),\
                                                (140,3,20,CHPT_NORMAL_DECREASE)])
change_scores2 = runChangeFinder(data1, 'ARMA')
plotDataAndChanges(data2, scores=change_scores2)


data3 = makeNormalData(0.07, 0.05, 200,\
                      induced_outlier_or_chpts=[(100,2,1,OUTLIER_INCREASE),\
                                                (140,3,1,OUTLIER_INCREASE),\
                                                (160,1,1,OUTLIER_INCREASE)])
change_scores3 = runChangeFinder(data1, 'ARMA')
plotDataAndChanges(data3, scores=change_scores3)


data4 = makeNormalData(0.07, 0.05, 200,\
                      induced_outlier_or_chpts=[(100,2,1,OUTLIER_DECREASE),\
                                                (160,3,1,OUTLIER_DECREASE)])
change_scores4 = runChangeFinder(data1, 'ARMA')
plotDataAndChanges(data4, scores=change_scores4)


data5 = makeNormalData(0.07, 0.05, 200,\
                      induced_outlier_or_chpts=[(20,2,1,OUTLIER_DECREASE),\
                                                (60,3,1,OUTLIER_INCREASE)])
change_scores5 = runChangeFinder(data1, 'ARMA')
plotDataAndChanges(data5, scores=change_scores5)

# change_scores = runChangeFinder(data1, 'AR')
#
# plotDataAndChanges(data, scores=change_scores)
#
# change_scores = runChangeFinder(data1, 'ARMA')
#
# plotDataAndChanges(data, scores=change_scores)