__author__ = 'santhosh'
from oct2py import octave
from oct2py import Oct2Py
import numpy
import os
from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.arima_model import ARMA

octave.addpath('/media/santhosh/Data/ubuntu/workspaces/datalab/Granger_source/GrangerAD/')
octave.addpath('/media/santhosh/Data/ubuntu/workspaces/datalab/Granger_source/GrangerAD/lasso/')
octave.addpath(os.getcwd())

# oc = Oct2Py()




def plotSeriesWithScores(real_vals, predicted_vals):
    import matplotlib.pyplot as plt
    assert real_vals.shape == predicted_vals.shape

    r, c = real_vals.shape
    fig = plt.figure(figsize=(20,20))


    for s in range(r):
        r_val = real_vals[s,:]
        p_val = predicted_vals[s,:]
        ymax = max((max(r_val), max(p_val)))
        ymin = min((min(r_val), min(p_val)))

        ax1 = fig.add_subplot(r, 1, s+1)
        # plt.yticks(numpy.arange(ymin, ymax, 0.2))
        ax1.plot(r_val, 'b')

        ax2 = ax1.twinx()
        # plt.yticks(numpy.arange(ymin, ymax, 0.2))
        ax2.plot(p_val, 'r')

    plt.show()


def plotSeries(data):
    import matplotlib.pyplot as plt
    r, c = data.shape
    fig = plt.figure(figsize=(20,20))


    for s in range(r):
        r_val = data[s,:]
        ymax = max(r_val)
        ymin = min(r_val)

        ax1 = fig.add_subplot(r, 1, s+1)
        plt.ylim((ymin,ymax))
        ax1.plot(r_val, 'b')

    plt.show()


def logloss(real_val, pred_val):
    import math
    return -math.log(math.exp(-0.5*(real_val-pred_val)**2)/math.sqrt(2*math.pi))


def calculateLogLoss(te_id_start, te_id_end, data, predicted_vals):
    real_vals = data[:, range(te_id_start-1, te_id_end)]

    no_of_series, series_length = data.shape

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

    real_vals = data[:, range(tr_id_start-1, tr_id_end)]

    for lambda_param in range(lambda_start, lambda_end):
        for lag in range(lag_start, lag_end):
            total_log_loss = 0
            train_size = tr_id_end-tr_id_start+1
            start = tr_id_start
            while start < tr_id_end:
                c_tr_start = start
                c_tr_end = start+10-lag
                c_te_start = c_tr_end+1
                c_te_end = start+10
                coeffMatrix = callOctaveAndFindGrangerCasuality(data, c_tr_start, c_tr_end, c_te_start, c_te_end, lag, lambda_param)
                predicted_vals = makePredictionsUsingGranger(coeffMatrix, data, lag, c_te_start, c_te_end)
            # plotSeries(real_vals, predicted_vals)
                log_loss = calculateLogLoss(c_te_start, c_te_end, data, predicted_vals)
                log_loss = numpy.sum(numpy.sum(log_loss))
                total_log_loss += log_loss
                start = c_te_end
            print lag, lambda_param, total_log_loss
            if log_loss < min_log_loss:
                min_log_loss = log_loss
                optim_lag, optim_lambda = lag, lambda_param
    return optim_lag, optim_lambda


def makePredictionsUsingGranger(coeffPyMatrix, data, lag, te_id_start, te_id_end):
    no_of_series, series_length = data.shape
    predicted_vals = numpy.zeros(shape=(no_of_series, te_id_end - te_id_start + 1))
    for s in range(no_of_series):
        curr_matrix = coeffPyMatrix[s]
        for tidx in range(te_id_start - 1, te_id_end):
            lagged_vals = numpy.array(
                [[data[j][tidx - i - 1] * curr_matrix[j][lag - i - 1] for i in range(lag - 1, -1, -1)] for j in
                 range(no_of_series)])
            predicted_val = numpy.sum(numpy.sum(lagged_vals))
            predicted_vals[s][tidx - te_id_start] = predicted_val
    return predicted_vals


def callOctaveAndFindGrangerCasuality(data, tr_id_start, tr_id_end, te_id_start, te_id_end, lag=2, lambda_param=10, print_coeff=False):
    no_of_series, series_length = data.shape
    octave.eval('pkg load communications')
    coeffsMatrix = octave.ts_ls_gran(data, tr_id_start, tr_id_end, lag, lambda_param)
    coeffPyMatrix = numpy.zeros(shape=(no_of_series, no_of_series, lag))

    for idx in range(no_of_series):
        coeffPyMatrix[idx] = numpy.reshape(coeffsMatrix[idx], newshape=(no_of_series, lag))

    return coeffPyMatrix


def makeARPredictions(data, te_id_start, te_id_end, order, params):
    pred = []
    # vals_to_look_at = [data[te_id_start-p] for p in range(order, 0, -1)]
    for i in range(te_id_start-1, te_id_end):
        val = 0
        r_params = params[::-1]
        for p in range(order):
            # val += data[i-(order - p - 1)] * params[p]
            val += data[i-(order-p)] * r_params[p]
        # val += numpy.random.normal(0, 1, 1)*math.exp(10**(-6))
        pred.append(val)
        # vals_to_look_at.append(val)
        print val, data[i]
    print '----------------------------------'
    return pred


def runLocalAR(data, tr_id_start, tr_id_end, te_id_start, te_id_end, order=None):
    no_of_series, series_length = data.shape
    all_preds = []
    for s in range(no_of_series):
        series_data = data[s]
        train_data = data[[s], range(tr_id_start - 1, tr_id_end)]
        ar_res = None
        ar_mod = AR(train_data)
        if order:
            ar_res = ar_mod.fit(order)
        else:
            ar_res = ar_mod.fit(ic='bic')

        order = len(ar_res.params)
        # preds1 = numpy.array(makeARPredictions(series_data, tr_id_start, tr_id_end, order, ar_res.params))
        pred = numpy.array(makeARPredictions(series_data, te_id_start, te_id_end, order, ar_res.params))
        # pred = numpy.concatenate([preds1, pred])
        all_preds.append(pred)
    pred_vals = numpy.array(all_preds)
    # plotSeriesWithScores(real_vals, pred_vals)
    log_loss_vals = calculateLogLoss(te_id_start, te_id_end, data, pred_vals)
    plotSeriesWithScores(data, log_loss_vals)



def plotCoeffMatrix(coeffMatrix):
    import matplotlib.pyplot as plt
    series, no_of_series, series_length = coeffMatrix.shape

    fig = plt.figure()

    for s in range(series):
        r_val = numpy.transpose(coeffMatrix[s])[0]

        ymax = max(r_val)
        ymin = min(r_val)

        ax1 = fig.add_subplot(series, 1, s+1)
        #plt.ylabel(DATA.labels[s])
        plt.ylim((ymin,ymax))

        #plt.xticks([f for f  in range(len(DATA.labels))],[f for f  in DATA.labels])

        ax1.plot(r_val, 'b')

    plt.show()

def runLocalGranger(data, tr_id_start, tr_id_end, te_id_start, te_id_end):
    # optim_lag, optim_lambda = doCrossValidationAndGetLagLambda(data, tr_id_start, tr_id_end, 2, 6, 3, 20)
    # print optim_lag, optim_lambda
    optim_lag, optim_lambda = 1, 3
    coeffMatrix = callOctaveAndFindGrangerCasuality(data, tr_id_start, tr_id_end, \
                                                    te_id_start, te_id_end, optim_lag, optim_lambda)

    predicted_vals = makePredictionsUsingGranger(coeffMatrix, data, optim_lag, te_id_start, te_id_end)
    log_loss_vals = calculateLogLoss(te_id_start, te_id_end, data, predicted_vals)
    real_vals = data[:, range(te_id_start - 1, te_id_end)]
    # log_loss_val = log_loss_vals[:, range(te_id_start - 1, te_id_end)]
    plotSeriesWithScores(data, log_loss_vals)


# no_of_series = 5
# series_length  = 100
#
# tr_id_start = 1
# tr_id_end = series_length/2
# te_id_start = series_length/2+1
# te_id_end = series_length/2+8
#
# data = SynData.getSyntheticData(no_of_series, series_length, insert_random_anom=True)
# plotSeries(data)
#
# # optim_lag, optim_lambda = doCrossValidationAndGetLagLambda(data, tr_id_start, tr_id_end, 2, 6, 3, 20)
# #
# # print optim_lag, optim_lambda
#
# predicted_vals = callOctaveAndFindGrangerCasuality(data, tr_id_start,\
#                                                    tr_id_end, te_id_start, te_id_end, 2, 3)
# real_vals = data[:,range(te_id_start-1,te_id_end)]
#
# plotSeriesWithScores(real_vals, predicted_vals)