__author__ = 'santhosh'
'''
Created on Feb 19, 2015

@author: santhosh
'''

from datetime import datetime
from util import StatConstants
import anomaly_detection
import changefinder
import cusum
import numpy
from util import GraphUtil
import scipy
import math
from statsmodels.tsa.ar_model import AR
import copy
from oct2py import octave
from oct2py import Oct2Py
import numpy
import os



LIMITS = { StatConstants.RATING_ENTROPY: (0.0, None),\
                           StatConstants.RATIO_OF_SINGLETONS: (0.0, 1.0),\
                           StatConstants.RATIO_OF_FIRST_TIMERS: (0.0, 1.0), StatConstants.YOUTH_SCORE: (0.0, None),\
                           StatConstants.ENTROPY_SCORE: (0.0, None), StatConstants.NON_CUM_NO_OF_REVIEWS :(0.0, None)}



def getRangeIdxs(idx):
    start = 2
    end = 3
    while start < end:
        if idx - start < 0:
            start -= 1
        else:
            break
    return (idx-start, idx+end)

def determineTimeWindows(avg_idxs, total_length):
    diff_test_windows = [getRangeIdxs(idx) for idx in sorted(avg_idxs)]
    diff_train_windows = []
    start = 0
    for window in diff_test_windows:
        idx1, idx2 = window
        end = idx1 - 1
        length_of_training_data = end - start + 1
        if length_of_training_data <= 8:
            if (len(diff_train_windows)) > 0:
                last_tr_window = diff_train_windows[-1]
                diff_train_windows.append(last_tr_window)
            else:
                diff_train_windows.append((start, total_length - 1))
        else:
            diff_train_windows.append((start, end))
        start = idx2 + 1
    return diff_test_windows, diff_train_windows

def logloss(real_val, pred_val):
    import math
    return -math.log(math.exp(-0.5*(real_val-pred_val)**2)/math.sqrt(2*math.pi))


def calculateLogLoss(te_id_start, te_id_end, data, predicted_vals):
    real_vals = data[:, range(te_id_start-1, te_id_end)]

    no_of_series, series_length = data.shape

    log_loss_vals = numpy.zeros(shape=(no_of_series, series_length), dtype=float)

    for s in range(no_of_series):
        for i in range(0, te_id_end-te_id_start+1):
            score = logloss(real_vals[s][i], predicted_vals[s][i])
            log_loss_vals[s][te_id_start+i] = score
    return log_loss_vals


def doCrossValidationAndGetLagLambda(data, tr_id_start, tr_id_end,
                                     lag_start = 2, lag_end = 2,
                                     lambda_start=10, lambda_end = 10):
    no_of_series, series_length = data.shape
    optim_lag, optim_lambda = lag_start, lambda_end
    min_log_loss = float('inf')

    for lambda_param in range(lambda_start, lambda_end):
        for lag in range(lag_start, lag_end):
            total_log_loss = 0
            train_size = tr_id_end-tr_id_start+1
            limit = train_size/10
            if limit < 3:
                limit = 8
            start = tr_id_start
            while start <= tr_id_end-limit:
                c_tr_start = start
                c_tr_end = start+int(math.fabs(0.60*limit))
                c_te_start = c_tr_end+1
                c_te_end = start+limit
                print start, c_tr_start, c_tr_end, c_te_start,\
                    c_te_end, int(math.fabs(0.60*limit)), c_tr_start+1, c_tr_end+1
                print lag, lambda_param
                coeffMatrix = callOctaveAndFindGrangerCasuality(data, c_tr_start+1, c_tr_end+1, lag, lambda_param)
                for idx in range(c_te_start, c_te_end):
                    pred = makePredictionsUsingGranger(coeffMatrix, data, lag, idx)
                    for s in range(no_of_series):
                        error = squaredResidualError(data[s][idx], pred[s])
                        total_log_loss += error

            # plotSeries(real_vals, predicted_vals)
            #     log_loss = calculateLogLoss(c_te_start, c_te_end, data, predicted_vals)
            #     log_loss = numpy.sum(numpy.sum(log_loss))
            #     total_log_loss += log_loss
                start = c_te_end
            # print lag, lambda_param, total_log_loss
            if total_log_loss < min_log_loss:
                min_log_loss = total_log_loss
                optim_lag, optim_lambda = lag, lambda_param

    return optim_lag, optim_lambda


def makePredictionsUsingGranger(coeffPyMatrix, data, lag, idx):
    no_of_series, series_length = data.shape
    predicted_vals = numpy.zeros(no_of_series)
    for s in range(no_of_series):
        curr_matrix = coeffPyMatrix[s]
        lagged_vals = numpy.array(
            [[data[j][idx - i - 1] * curr_matrix[j][lag - i - 1] for i in range(lag - 1, -1, -1)] for j in
             range(no_of_series)])
        predicted_vals[s] = numpy.sum(numpy.sum(lagged_vals))
    return predicted_vals


def callOctaveAndFindGrangerCasuality(data, tr_id_start, tr_id_end, lag=2, lambda_param=10):
    octave.addpath('/media/santhosh/Data/ubuntu/workspaces/datalab/Data-Mining/Granger_source/GrangerAD/')
    octave.addpath('/media/santhosh/Data/ubuntu/workspaces/datalab/Data-Mining/Granger_source/GrangerAD/lasso/')
    octave.addpath(os.getcwd())
    # oc = Oct2Py()
    no_of_series, series_length = data.shape
    octave.eval('pkg load communications')
    coeffsMatrix = octave.ts_ls_gran(data, tr_id_start, tr_id_end, lag, lambda_param)
    coeffPyMatrix = numpy.zeros(shape=(no_of_series, no_of_series, lag))

    for idx in range(no_of_series):
        coeffPyMatrix[idx] = numpy.reshape(coeffsMatrix[idx], newshape=(no_of_series, lag))

    return coeffPyMatrix

def runLocalGranger(statistics_for_bnss, GRANGER_MEASURES, avg_idxs, find_outlier_idxs=True):
    GRANGER_MEASURES = [measure_key for measure_key in GRANGER_MEASURES if measure_key in statistics_for_bnss]
    no_of_series = len(GRANGER_MEASURES)
    series_length = len(statistics_for_bnss[GRANGER_MEASURES[0]])

    data = numpy.zeros(shape=(no_of_series, series_length), dtype=numpy.float)
    for s in range(no_of_series):
        measure_key = GRANGER_MEASURES[s]
        data[s] = statistics_for_bnss[measure_key]

    diff_test_windows, diff_train_windows = determineTimeWindows(avg_idxs, series_length)
    no_of_windows = len(diff_test_windows)
    test_error_scores, test_outlier_idxs = {key:[] for key in GRANGER_MEASURES}, {key:[] for key in GRANGER_MEASURES}
    for wid in range(no_of_windows):
        tr_id_start, tr_id_end = diff_train_windows[wid]
        te_id_start, te_id_end = diff_test_windows[wid]

        optim_lag, optim_lambda = doCrossValidationAndGetLagLambda(data, tr_id_start, tr_id_end, 2, 4, 5, 10)

        # optim_lag, optim_lambda = 1, 3
        coeffMatrix = callOctaveAndFindGrangerCasuality(data, tr_id_start, tr_id_end, optim_lag, optim_lambda)

        for idx in range(te_id_start, te_id_end+1):
            predicted_val = makePredictionsUsingGranger(coeffMatrix, data, optim_lag, idx)
            for s in range(no_of_series):
                error = squaredResidualError(data[s][idx], predicted_val[s])
                test_error_scores[GRANGER_MEASURES[s]].append(error)
                if find_outlier_idxs and error > StatConstants.MEASURE_CHANGE_LOCAL_GRANGER_THRES[GRANGER_MEASURES[s]]:
                    test_outlier_idxs[GRANGER_MEASURES[s]].append(idx)
    return test_error_scores, test_outlier_idxs




def calculateRankingUsingAnomalies(statistics_for_bnss, chPtsOutliers):
    dimensions = 0
    windows = None
    numberOfReviewsInEachTimeStamp = dict()
    firstTimeKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    scores = dict()
    changed_dimensions = dict()
    for measure_key in StatConstants.MEASURES:
        if measure_key not in statistics_for_bnss or measure_key not in chPtsOutliers:
            continue
        statistics = statistics_for_bnss[measure_key][firstTimeKey:]
        chOutlierIdxs, chOutlierScores = chPtsOutliers[measure_key]
        if measure_key == StatConstants.AVERAGE_RATING:
                windows = [getRangeIdxs(idx) for idx in chOutlierIdxs ]
                scores = {key:0.0 for key in windows}
                changed_dimensions = {key: set() for key in windows}
        elif measure_key == StatConstants.NON_CUM_NO_OF_REVIEWS:
                numberOfReviewsInEachTimeStamp = {(idx1, idx2): (numpy.amax(statistics[idx1:idx2])-numpy.amin(statistics[idx1:idx2]))\
                                                    for idx1, idx2 in windows}
        else:
            if measure_key != StatConstants.NO_OF_REVIEWS:
                dimensions += 1
                if len(chOutlierIdxs) > 0:
                    globalMaxima = numpy.amax(statistics)
                    globalMinima = numpy.amin(statistics)
                    for window in windows:
                        idx1, idx2 = window
                        if numpy.any(numpy.array([True for idx in chOutlierIdxs if idx in range(idx1,idx2)])):
                            localMaxima = numpy.amax(statistics[idx1:idx2])
                            localMinima = numpy.amin(statistics[idx1:idx2])
                            score_for_window = (localMaxima - localMinima)/(globalMaxima - globalMinima)
                            scores[window] += score_for_window
                            changed_dimensions[window].add(measure_key)
    for window in windows:
        scores[window] /= dimensions
        if numberOfReviewsInEachTimeStamp[window] == 0:
            scores[window] = 0
        else:
            scores[window] *= math.log(numberOfReviewsInEachTimeStamp[window])
    return scores, changed_dimensions

def squaredResidualError(actual_data, pred_data):
    return (actual_data-pred_data)**2

def makeARPredictions(data, params, idx, measure_key = None):
    order = len(params)
    val = 0
    for p in range(order):
        # val += data[idx-(order - p - 1)] * params[p]
        val += data[idx-p-1] * params[p]
    # val += numpy.random.normal(0, 1, 1)*math.exp(10**(-6))

    if measure_key in LIMITS:
        start_limit, end_limit = LIMITS[measure_key]
        # if end_limit and val > end_limit:
        #     val = end_limit
        if val < start_limit:
            val = start_limit

    return val

def doLocalARCrossValidation(data, tr_idx_start, tr_idx_end):
    length_of_training_data = tr_idx_end-tr_idx_start+1
    ar_mod = AR(data[tr_idx_start:tr_idx_end+1])
    error_dict = dict()
    for order in range(1, min([5, length_of_training_data])):
        ar_res = ar_mod.fit(maxlag=order)
        params = ar_res.params
        error = 0
        for idx in range(tr_idx_start, tr_idx_end+1):
            pred = makeARPredictions(data, params, idx)
            error += squaredResidualError(data[idx], pred)
        error_dict[order] = error
    return min(error_dict.keys(), key=lambda key: error_dict[key])

def localAR(data, avg_idxs, measure_key, find_outlier_idxs = True):
    thres = StatConstants.MEASURE_CHANGE_LOCAL_AR_THRES[measure_key]
    needed_direction = StatConstants.MEASURE_DIRECTION[measure_key]
    val_change_thres = StatConstants.MEASURE_CHANGE_THRES[measure_key]
    diff_test_windows, diff_train_windows = determineTimeWindows(avg_idxs, len(data))

    total_length = len(data)

    no_of_windows = len(diff_train_windows)
    outierIds = []
    outies_scores = []
    for wid in range(no_of_windows):
        tr_idx_start, tr_idx_end = diff_train_windows[wid]
        te_idx_start, te_idx_end = diff_test_windows[wid]

        last_filled_idx = len(outies_scores)-1

        order = doLocalARCrossValidation(data, tr_idx_start, tr_idx_end)

        # print 'Low Error Order', order

        ar_mod = AR(data[tr_idx_start:tr_idx_end+1])
        ar_res = ar_mod.fit(maxlag=order)

        if last_filled_idx > te_idx_start:
            te_idx_start = last_filled_idx+1

        copied_data = copy.copy(data)

        corr_start = 0
        corr_end = te_idx_start-1

        if (tr_idx_end-tr_idx_start+1) == total_length:
            corr_start = last_filled_idx+1
        elif tr_idx_start > last_filled_idx:
            corr_end = tr_idx_end-tr_idx_start
        else:
            corr_start = last_filled_idx-tr_idx_start+1
            corr_end = tr_idx_end-tr_idx_start

        train_pred = []
        train_error_scores = []
        for i in range(corr_start, corr_end+1):
            pred = makeARPredictions(copied_data, ar_res.params, i, measure_key)
            error = squaredResidualError(copied_data[tr_idx_start+i], pred)
            train_pred.append(pred)
            train_error_scores.append(error)

        outies_scores.extend(train_error_scores)
        # print len(train_error_scores), tr_idx_start, tr_idx_end, corr_start, corr_end, corr_end-corr_start+1, len(scores)

        test_pred = []
        test_error_scores = []
        for i in range(te_idx_start, te_idx_end+1):
            if i >= len(copied_data):
                break
            pred = makeARPredictions(copied_data, ar_res.params, i, measure_key)
            error = squaredResidualError(copied_data[i], pred)
            direction = copied_data[i]-copied_data[i-1]
            test_pred.append(pred)
            test_error_scores.append(error)

            if find_outlier_idxs:
                diff = math.fabs(direction)
                if direction < 0:
                    direction = StatConstants.DECREASE
                else:
                    direction = StatConstants.INCREASE
                # and diff>=val_change_thres

                # import tryout.ScoreHistogram as sc
                # if measure_key in sc.THRES and error > sc.THRES[measure_key]:
                #     print '***************************************************************'
                #     print data[i], pred, measure_key, error
                #     print '***************************************************************'

                if thres and error >= thres:
                    if needed_direction == StatConstants.BOTH or direction == needed_direction:
                        outierIds.append(i)
                    # copied_data[i] = pred

        outies_scores.extend(test_error_scores)

    print '-----------------------------------------------------'
    return outierIds, outies_scores





def twitterAnomalyDetection(dates, values):
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    importr("AnomalyDetection")
    anomaly_detection = robjects.r['AnomalyDetectionTs']

    # robjects.r('''
    #     rdateFn <- function(d , m, y) {
    #         dat <- paste(paste(toString(d),toString(m),sep="/"),toString(y), sep="/")
    #         return(dat)
    #     }
    #     ''')
    # rdateFn = robjects.globalenv['rdateFn']

    date_value_dict = {'a':robjects.POSIXct(dates), 'b':robjects.IntVector(values)}
    dataf = robjects.DataFrame(date_value_dict)
    res = anomaly_detection(dataf, plot= True)
    anoms_data_f = res[res.names.index('anoms')]
    anoms_dates = set()
    for d in anoms_data_f.rx2(1):
        anoms_dates.add(datetime.fromtimestamp(d).date())
    idxs = []
    dates = [dates[i].date() for i in range(len(dates))]
    for i in range(len(dates)):
        if dates[i] in anoms_dates:
            idxs.append(i)
    values = numpy.atleast_1d(values).astype('int64')
    return idxs




def compactChOutlierScoresAndIdx(choutlierIdxs, choutlierScores, measure_key,\
                                 statistics_for_measure, avg_idxs, algo):
    if algo == StatConstants.AR_UNIFYING:
        result = scipy.signal.argrelextrema(numpy.array(choutlierScores), numpy.greater)
        idxs = result[0]
    elif algo == StatConstants.CUSUM:
        ta, tai, taf, amp = choutlierIdxs
        idxs = ta
    else:
        idxs = choutlierIdxs

    new_idxs = set()

    if StatConstants.MEASURE_DIRECTION[measure_key] == StatConstants.INCREASE:
        for idx in idxs:
            idxRangePresent = False
            for range_idx in range(idx-2, idx+3):
                if range_idx in avg_idxs:
                    idxRangePresent = True
                    break
            if idxRangePresent:
                idx1,idx2 = getRangeIdxs(idx)
                new_idx = scipy.signal.argrelextrema(numpy.array(statistics_for_measure[idx1:idx2]), numpy.greater)
                new_idx = new_idx[0]
                new_idx = [idx1+indx for indx in new_idx]
                #print idx, new_idx
                for indx in new_idx:
                    diff = math.fabs(statistics_for_measure[indx]-min(statistics_for_measure[idx1:indx+1]))
                    if not StatConstants.MEASURE_CHANGE_THRES[measure_key] \
                            or diff > StatConstants.MEASURE_CHANGE_THRES[measure_key]:
                        new_idxs.add(indx)
    elif StatConstants.MEASURE_DIRECTION[measure_key] == StatConstants.DECREASE:
        for idx in idxs:
            idxRangePresent = False
            for range_idx in range(idx-2,idx+3):
                if range_idx in avg_idxs:
                    idxRangePresent = True
                    break
            if idxRangePresent:
                idx1,idx2 = getRangeIdxs(idx)
                new_idx = scipy.signal.argrelextrema(numpy.array(statistics_for_measure[idx1:idx2]), numpy.less)
                new_idx = new_idx[0]
                new_idx = [idx1+indx for indx in new_idx]
                #print idx,new_idx
                for indx in new_idx:
                    diff = math.fabs(statistics_for_measure[indx]-max(statistics_for_measure[idx1:indx+1]))
                    # print indx, diff
                    if not StatConstants.MEASURE_CHANGE_THRES[measure_key] \
                            or diff > StatConstants.MEASURE_CHANGE_THRES[measure_key]:
                        new_idxs.add(indx)
    else:
        for idx in idxs:
            idxRangePresent = False
            for range_idx in range(idx-2, idx+3):
                if range_idx in avg_idxs:
                    idxRangePresent = True
                    break
            if idxRangePresent:
                new_idxs.add(idx)

    choutlierIdxs = sorted([idx for idx in list(new_idxs)])

    return choutlierIdxs, choutlierScores

# r - Coefficient of forgetting type AR model. 0 <r <1
# order - Degree of forgetting type AR model
# smooth - section length of time to be moving average smoothing the calculated outliers score

def detectChPtsAndOutliers(statistics_for_bnss, timeLength = '1-M', find_outlier_idxs=True):
    beforeDetection = datetime.now()
    firstKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    lastKey = statistics_for_bnss[StatConstants.LAST_TIME_KEY]
    firstDateTime = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    total_time_slots = len(statistics_for_bnss[StatConstants.AVERAGE_RATING])
    chPtsOutliers= dict()
    avg_idxs = None
    GRANGER_MEASURES = [measure_key for measure_key in StatConstants.MEASURES_CHANGE_FINDERS
                        if StatConstants.LOCAL_GRANGER in StatConstants.MEASURES_CHANGE_DETECTION_ALGO[measure_key]
                        ]
    isGrangerNeeded = False

    for measure_key in StatConstants.MEASURES:
        chOutlierIdxs, chOutlierScores = [], []
        if measure_key in statistics_for_bnss:
            if measure_key == StatConstants.NO_OF_REVIEWS:
                continue
            data = statistics_for_bnss[measure_key][firstKey:lastKey+1]

            algoList, params = StatConstants.MEASURES_CHANGE_FINDERS[measure_key]

            for algo in algoList:
                if algo == StatConstants.AR_UNIFYING:
                    r, order, smooth = params
                    import ChangeFinderSinglePass as ch
                    cf = ch.ChangeFinderSinglepass(r, order, smooth)
                    change_scores = []
                    for d in data:
                        score = cf.update(d)
                        change_scores.append(score)
                    chOutlierScores = change_scores

                    if find_outlier_idxs:
                        chOutlierIdxs, chOutlierScores = compactChOutlierScoresAndIdx(chOutlierIdxs,
                                                                                      chOutlierScores, measure_key,
                                                                                      statistics_for_bnss[measure_key][firstKey:],
                                                                                      avg_idxs, algo)
                elif algo == StatConstants.CUSUM:
                    chOutlierIdxs = cusum.detect_cusum(data, threshold=params, show=False)
                    if measure_key == StatConstants.AVERAGE_RATING:
                        ta, tai, taf, amp = chOutlierIdxs
                        chOutlierIdxs = [idx for idx in ta]
                        chOutlierScores = []
                        avg_idxs = set(ta)

                elif algo == StatConstants.TWITTER_SEASONAL_ANOM_DETECTION:
                    chOutlierIdxs = twitterAnomalyDetection(\
                        GraphUtil.getDates(firstDateTime, range(firstKey, total_time_slots), timeLength)\
                        ,data)
                elif algo == StatConstants.LOCAL_AR:
                    chOutlierIdxs, chOutlierScores = localAR(data, avg_idxs, measure_key, find_outlier_idxs)

                elif algo == StatConstants.LOCAL_GRANGER:
                    isGrangerNeeded = True
                    continue
                if algo not in chPtsOutliers:
                    chPtsOutliers[measure_key] = dict()
                chPtsOutliers[measure_key][algo]= (chOutlierIdxs, chOutlierScores)

    if isGrangerNeeded:
        test_outlier_scores, test_outlier_idxs = runLocalGranger(statistics_for_bnss, GRANGER_MEASURES,
                                                                 avg_idxs, find_outlier_idxs)
        for measure_key in test_outlier_scores.keys():
            chPtsOutliers[measure_key] = (test_outlier_idxs[measure_key], test_outlier_scores[measure_key])

    afterDetection = datetime.now()
    print 'Time Taken For Anamoly Detection for Bnss Key', statistics_for_bnss[StatConstants.BNSS_ID],\
        ':', afterDetection-beforeDetection

    return chPtsOutliers