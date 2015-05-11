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
    ax = fig.add_subplot(1, 1, 1)
    # plt.yticks(numpy.arange(0, 3, 0.5))

    ax.plot(range(len(data)), data, 'b')

    if len(scores) > 0:
        ax2 = ax.twinx()
        # plt.yticks(numpy.arange(0, 3, 0.5))
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

# change_scores1 = runChangeFinder(data1, 'ARMA')
# plotDataAndChanges(data1, scores=change_scores1)
#
# data2 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(100,2,20,CHPT_NORMAL_INCREASE),\
#                                                 (140,3,20,CHPT_NORMAL_DECREASE)])
# change_scores2 = runChangeFinder(data1, 'ARMA')
# plotDataAndChanges(data2, scores=change_scores2)
#
#
# data3 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(100,2,1,OUTLIER_INCREASE),\
#                                                 (140,3,1,OUTLIER_INCREASE),\
#                                                 (160,1,1,OUTLIER_INCREASE)])
# change_scores3 = runChangeFinder(data1, 'ARMA')
# plotDataAndChanges(data3, scores=change_scores3)
#
#
# data4 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(100,2,1,OUTLIER_DECREASE),\
#                                                 (160,3,1,OUTLIER_DECREASE)])
# change_scores4 = runChangeFinder(data1, 'ARMA')
# plotDataAndChanges(data4, scores=change_scores4)
#
#
# data5 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(20,2,1,OUTLIER_DECREASE),\
#                                                 (60,3,1,OUTLIER_INCREASE)])
# change_scores5 = runChangeFinder(data1, 'ARMA')
# plotDataAndChanges(data5, scores=change_scores5)

# change_scores = runChangeFinder(data1, 'AR')
#
# plotDataAndChanges(data, scores=change_scores)
#
# change_scores = runChangeFinder(data1, 'ARMA')
#
# plotDataAndChanges(data, scores=change_scores)

def logloss(real_val, pred_val):
    import math
    return -math.log(math.exp(-0.5*(real_val-pred_val)**2)/math.sqrt(2*math.pi))

from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.arima_model import ARMA

data = [2.22974507,1.77638876,1.36251694,0.63430955,1.56276414,1.45049636
,1.49355146,1.33083748,1.45067782, 1.68305934,1.54421536,1.74168241
,1.37840367,1.40733197,1.50468499, 1.58443507,1.4767025, 1.66373543
,1.46783808,1.32792633,1.65257529, 1.68632441,1.9030402, 1.96999589
,1.84691613,2.07700135,2.23981053, 1.66073599,2.14179324,2.03673212
,2.14653166,2.14159997,2.13133767, 0.97888903,0.4334023, 0.65564258
,0.64874987,1.24975657,0.50703108, 0.77332397,1.10924767,0.81356824
,0.80387861,0.53311585,0.73540776, 0.79021073,1.23688976]

data = [1.03328336,1.48207205,1.51375305,1.51579082,1.56124504,1.14842646,1.23729834,1.57941601,1.84673416,1.73875868,2.23399791,1.6364921, 1.15677965,1.52173791,1.51964453,0.89477794,1.21513233,1.2670422, 1.75034574,1.72928696,1.5224434,2.01607321,0.83662014,0.61629464,0.67232625,0.52825708,0.76687291,0.58897955,0.60068777,0.67027366]

order = 3
input_length = 20
pred_length = 5

ar_mod = AR(data[:input_length])
ar_res = ar_mod.fit(ic='bic')
order = len(ar_res.params)

pred = ar_res.predict(order, input_length+pred_length, dynamic=False)


# arma_mod = ARMA(data[:20], order=(3, 2))
# arma_res = arma_mod.fit()
# pred = arma_res.predict(order, len(data))


out = numpy.zeros(order)
out = numpy.concatenate([out,\
                         numpy.array(pred)\
                         ])

scores = numpy.zeros(len(data))
for i in range(order, input_length+pred_length):
    score = logloss(data[i], out[i])
    scores[i] = score
scores = out

plotDataAndChanges(data, scores=scores)