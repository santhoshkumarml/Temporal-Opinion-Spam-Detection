__author__ = 'santhosh'
from oct2py import octave
from oct2py import Oct2Py
import numpy
import os

octave.addpath('/media/santhosh/Data/ubuntu/workspaces/datalab/Granger_source/GrangerAD/')
octave.addpath('/media/santhosh/Data/ubuntu/workspaces/datalab/Granger_source/GrangerAD/lasso/')
octave.addpath(os.getcwd())

oc = Oct2Py()




def plotSeries(real_vals, predicted_vals):
    import matplotlib.pyplot as plt
    assert real_vals.shape == predicted_vals.shape

    r, c = real_vals.shape
    fig = plt.figure()

    for s in range(r):
        r_val = real_vals[s,:]
        p_val = predicted_vals[s,:]
        ymax = max((max(r_val), max(p_val)))
        ymin = min((min(r_val), min(p_val)))

        ax1 = fig.add_subplot(r, 1, s+1)

        plt.yticks(numpy.arange(ymin, ymax, 0.2))
        ax1.plot(r_val, 'b')

        ax2 = ax1.twinx()
        plt.yticks(numpy.arange(ymin, ymax, 0.2))
        ax2.plot(p_val, 'r')

    plt.show()


def logloss(real_val, pred_val):
    import math
    return -math.log(math.exp(-0.5*(real_val-pred_val)**2)/math.sqrt(2*math.pi))


def calculateLogLoss(te_id_start, te_id_end, data, predicted_vals):
    real_vals = data[:, range(te_id_start-1, te_id_end)]

    log_loss_vals = numpy.zeros(shape=(no_of_series, series_length), dtype=float)

    for s in range(no_of_series):
        for i in range(0,te_id_end-te_id_start+1):
            score = logloss(real_vals[s][i], predicted_vals[s][i])
            log_loss_vals[s][te_id_start+i] = score
    return log_loss_vals


def doCrossValidationAndGetLagLambda(data, tr_id_start, tr_id_end, lag_start = 2, lag_end = 2, lambda_start=10, lambda_end = 10):
    no_of_series, series_length = data.shape
    optim_lag, optim_lambda = lag_start, lambda_end
    min_log_loss = float('inf')

    for lambda_param in range(lambda_start, lambda_end):
        for lag in range(lag_start, lag_end):
            predicted_vals = callOctaveAndFindGrangerCasuality(data, tr_id_start, tr_id_end, tr_id_start, tr_id_end, lag, lambda_param)
            log_loss = calculateLogLoss(tr_id_start, tr_id_end, data, predicted_vals)
            log_loss = numpy.sum(numpy.sum(log_loss))
            if log_loss < min_log_loss:
                min_log_loss = log_loss
                optim_lag, optim_lambda = lag, lambda_param
    return optim_lag, optim_lambda




def callOctaveAndFindGrangerCasuality(data, tr_id_start, tr_id_end, te_id_start, te_id_end, lag=2, lambda_param=10):
    no_of_series, series_length = data.shape
    octave.eval('pkg load communications')
    coeffsMatrix = octave.ts_ls_gran(data, tr_id_start, tr_id_end, lag, lambda_param)
    coeffPyMatrix = numpy.zeros(shape=(no_of_series, no_of_series, lag))

    for idx in range(no_of_series):
        coeffPyMatrix[idx] = coeffsMatrix[idx]
    predicted_vals = numpy.zeros(shape=(no_of_series, te_id_end - te_id_start + 1))

    for s in range(no_of_series):
        curr_matrix = coeffPyMatrix[s]
        for tidx in range(te_id_start-1, te_id_end):
            lagged_vals = numpy.array(
                [[data[j][tidx - i - 1] * curr_matrix[j][lag - i - 1] for i in range(lag - 1, -1, -1)] for j in
                 range(no_of_series)])
            predicted_val = numpy.sum(numpy.sum(lagged_vals))
            predicted_vals[s][tidx - te_id_start] = predicted_val
    return predicted_vals


no_of_series = 5
series_length = 83
lag = 2

data1 = [2.22974507, 1.77638876,1.36251694,0.63430955,1.56276414,1.45049636,1.49355146,1.33083748,1.45067782,1.68305934,1.54421536,1.74168241,1.37840367,1.40733197,1.50468499,1.58443507,1.4767025,1.66373543,1.46783808,1.32792633,1.65257529,1.68632441,1.9030402,1.96999589,1.84691613,2.07700135,2.23981053,1.66073599,2.14179324,2.03673212,2.14653166,2.14159997,2.13133767,0.97888903,0.4334023,0.65564258,0.64874987,1.24975657,0.50703108,0.77332397,1.10924767,0.81356824,0.80387861,0.53311585,0.73540776,0.79021073,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,1.23688976,0.0]
data2 = [0.9689441, 0.91743119,0.94186047,0.96,0.87254902,0.91479821,0.9253112,0.84210526,0.84100418,0.89361702,0.8028169,0.89380531,0.84507042,0.78195489,0.84158416,0.9047619,0.87951807,0.8852459,0.96296296,0.86458333,0.91346154,0.87096774,0.79439252,0.86111111,0.81092437,0.80536913,0.78409091,0.87387387,0.82795699,0.81818182,0.77966102,0.72277228,0.87804878,0.93192869,0.95528086,0.94703872,0.94246176,0.88693957,0.94637332,0.94028662,0.94227273,0.93467543,0.93321678,0.9125,0.92724458,0.8986421,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,1.0]
# data3 = [161, 109, 86,25,102,223,241,228,239,188,142,113,142,133,101,84,83,244,945,192,208,186,107,144,238,149,88,111,93,132,118,101,123,617,5501,1756,1373,513,2909,1256,2200,2434,2860,240,1938,2062,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,158,1];
data4 = [0.7826087, 0.70642202,0.72093023,0.76,0.60784314,0.78026906,0.74688797,0.6622807,0.69456067,0.70744681,0.57746479,0.76106195,0.63380282,0.63909774,0.67326733,0.70238095,0.71084337,0.75819672,0.8952381,0.74479167,0.78846154,0.77956989,0.60747664,0.70833333,0.67226891,0.60402685,0.65909091,0.76576577,0.66666667,0.6969697,0.6440678,0.62376238,0.71544715,0.87358185,0.90201781,0.88952164,0.88710852,0.82066277,0.90959092,0.9044586,0.90363636,0.90591619,0.90524476,0.90416667,0.91331269,0.88894277,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,0.87974684,1.0]
data5 = [0.98905899, 0.92661201,0.94296344,0.96,0.91810011,0.96071851,0.95574006,0.91146039,0.86956916,0.90964569,0.85379189,0.907415,0.87706689,0.83458754,0.88118902,0.91666667,0.92771084,0.9057377,0.97013506,0.89237044,0.93750876,0.89587494,0.80467133,0.8824706,0.84386129,0.86577245,0.81565007,0.883858,0.83973056,0.83333333,0.82013881,0.7799657,0.90243902,0.93854357,0.95677982,0.94959703,0.94465228,0.8997202,0.9474999,0.94272511,0.94375231,0.93712477,0.93627149,0.91265851,0.93039989,0.90218525,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,0.87977814,1.0]
data6 = [0.71912204, 0.87731491,1.04376258,1.40563906,0.88967452,0.54856211,0.53175152,0.55124426,0.55343821,0.62240886,0.74833934,0.85191151,0.7632238,0.79266917,0.94361834,1.04220472,1.02522303,0.52746524,0.19799156,0.6144071,0.58449179,0.63295556,0.93026894,0.7709049,0.53611494,0.74182611,0.96449673,0.8470438,0.98779719,0.81249067,0.84709773,0.87185117,0.82816918,0.27686884,0.04748681,0.12145272,0.1041873,0.31396252,0.07103816,0.15854998,0.10125327,0.09326488,0.07942194,0.03908175,0.11218925,0.10670825,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.0]

data = numpy.zeros(shape=(no_of_series, series_length))

data[0] = numpy.array(data1)
data[1] = numpy.array(data2)
# data[2] = numpy.array(data3)
data[2] = numpy.array(data4)
data[3] = numpy.array(data5)
data[4] = numpy.array(data6)

tr_id_start = 1
tr_id_end = 30
te_id_start = 31
te_id_end = 37

optim_lag, optim_lambda = doCrossValidationAndGetLagLambda(data, tr_id_start, tr_id_end, 2, 4, 3, 20)

predicted_vals = callOctaveAndFindGrangerCasuality(data, tr_id_start, tr_id_end, te_id_start, te_id_end, optim_lag, optim_lambda)

real_vals = data[:, range(te_id_start-1, te_id_end)]

# for s in range(no_of_series):
#         print 'Series', s
#         for i in range(0,te_id_end-te_id_start+1):
#             print predicted_vals[s][i], real_vals[s][i]
#
# plotSeries(real_vals, predicted_vals)

log_loss_vals = calculateLogLoss(te_id_start, te_id_end, data, predicted_vals)
plotSeries(data, log_loss_vals)

