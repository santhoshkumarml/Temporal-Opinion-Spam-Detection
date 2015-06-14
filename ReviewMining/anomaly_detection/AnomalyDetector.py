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
from statsmodels.tsa.arima_model import ARMA



def getRangeIdxs(idx):
    start = 3
    end = 4
    while start < end:
        if idx - start < 0:
            start -= 1
        else:
            break
    return (idx-start, idx+end)

def calculateRankingUsingAnomalies(statistics_for_bnss, chPtsOutliers):
    dimensions = 0
    windows = None
    numberOfReviewsInEachTimeStamp = dict()
    firstTimeKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    scores = dict()
    changed_dimensions = dict()
    for measure_key in StatConstants.MEASURES:
        if measure_key not in statistics_for_bnss:
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


def detect_outliers_using_cusum(x, threshold=1):
    x = numpy.atleast_1d(x).astype('float64')
    gp, gn = numpy.zeros(x.size), numpy.zeros(x.size)
    ta, tai, tapi, tani = numpy.array([[], [], [], []], dtype=int)
    tap, tan = 0, 0
    # Find changes (online form)
    i = 1
    while i < x.size:
        idx = 0 if not ta.size else ta[-1]
        prev_idx = 0 if ta.size <=1 else ta[-2]
        # s = x[i] - x[i-1]
        # s = -1
        if prev_idx != idx:
            sd = numpy.std(x[prev_idx:idx])
            s = (threshold/sd)*(x[i] - numpy.mean(x[idx:i]) - (threshold/2))
        else:
            s = x[i] - numpy.mean(x[idx:i])
        #print i, idx, x[i], numpy.mean(x[idx:i]),x[i] - numpy.mean(x[idx:i]), gp[i-1]+s, gn[i-1]-s

        gp[i] = gp[i-1] + s  # cumulative sum for + change
        gn[i] = gn[i-1] - s  # cumulative sum for - change
        if gp[i] < 0:
            gp[i], tap = 0, i
        if gn[i] < 0:
            gn[i], tan = 0, i
        if gp[i] > threshold or gn[i] > threshold:
            ta = numpy.append(ta, i)
            if gp[i] > threshold:
                tai = numpy.append(tai, tap)
                tapi = numpy.append(tapi,i)
            else:
                tai = numpy.append(tai, tan)
                tani = numpy.append(tani,i)
            gp[i], gn[i] = 0, 0
            # gp[i], gn[i] = threshold, threshold      # reset alarm
    return ta, tai, tapi, tani

def squaredResidualError(actual_data, pred_data):
    data_length = len(actual_data)
    loss = numpy.zeros(data_length)
    for i in range(data_length):
        loss[i] = (actual_data[i]-pred_data[i])**2
    return loss

def makeARPredictions(data, params, te_idx_start, te_idx_end):
    pred = []
    order = len(params)
    for i in range(te_idx_start, te_idx_end+1):
        val = 0
        for p in range(order):
            val += data[i-(order - p - 1)] * params[p]
        # val += numpy.random.normal(0, 1, 1)*math.exp(10**(-6))
        pred.append(val)
    return pred

def localAR(data, avg_idxs):
    diff_test_windows = [getRangeIdxs(idx) for idx in sorted(avg_idxs)]
    diff_train_windows = []
    start = 0
    total_length = len(data)
    for window in diff_test_windows:
        idx1, idx2 = window
        end = idx1-1
        length_of_training_data = end-start+1
        if length_of_training_data <= 6:
            if(len(diff_train_windows)) > 0:
                last_tr_window = diff_train_windows[-1]
                diff_train_windows.append(last_tr_window)
            else:
                diff_train_windows.append((start, total_length-1))
        else:
            diff_train_windows.append((start, end))
        start = idx2+1

    no_of_windows = len(diff_train_windows)
    scores = []
    for wid in range(no_of_windows):
        tr_idx_start, tr_idx_end = diff_train_windows[wid]
        te_idx_start, te_idx_end = diff_test_windows[wid]
        ar_mod = AR(data[tr_idx_start:tr_idx_end+1])
        ar_res = ar_mod.fit(ic='bic')
        train_pred = makeARPredictions(data, ar_res.params, tr_idx_start, tr_idx_end)
        train_error_scores = squaredResidualError(data[tr_idx_start:tr_idx_end+1], train_pred)
        last_filled_idx = len(scores)-1

        if last_filled_idx > te_idx_start:
            te_idx_start = last_filled_idx+1

        corr_start = 0
        corr_end = te_idx_start-1

        if (tr_idx_end-tr_idx_start+1) == total_length:
            corr_start = last_filled_idx+1
        elif tr_idx_start > last_filled_idx:
            corr_end = tr_idx_end-tr_idx_start
        else:
            corr_start = last_filled_idx-tr_idx_start+1
            corr_end = tr_idx_end-tr_idx_start
        print corr_start, corr_end
        scores.extend(train_error_scores[corr_start:corr_end+1])
        test_pred = makeARPredictions(data, ar_res.params, te_idx_start, te_idx_end)
        test_error_scores = squaredResidualError(data[te_idx_start:te_idx_end+1], test_pred)
        scores.extend(test_error_scores)
        print tr_idx_start, tr_idx_end, len(train_error_scores)
        print te_idx_start, te_idx_end, len(test_error_scores)
        print len(scores)
    # print scores, len(scores), len(data)
    print '-----------------------------------------------------'
    return scores



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




def compactChOutlierScoresAndIdx(firstTimeKey, choutlierIdxs, choutlierScores, measure_key,\
                               statistics_for_measure, avg_idxs, algo):
    if algo == StatConstants.AR_UNIFYING:
        result = scipy.signal.argrelextrema(numpy.array(choutlierScores), numpy.greater)
        idxs = result[0]
    elif algo == StatConstants.CUSUM:
        ta, tai, taf, amp = choutlierIdxs
        idxs = ta
    else:
        idxs = choutlierIdxs

        # print idxs
        # idxs = [i for i in range(1,len(chOutlierScores))\
        #           if (chOutlierScores[i]!=len(chOutlierScores)-1 and\
        #               chOutlierScores[i-1]<chOutlierScores[i] and chOutlierScores[i-1]<=chOutlierScores[i])\
        #           or (chOutlierScores[i]==len(chOutlierScores)-1 and\
        #               chOutlierScores[i-1]<chOutlierScores[i])]
        # print idxs

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
            # if measure_key == StatConstants.AVERAGE_RATING:
            #     #print idxs
            #     for indx in range(0,len(idxs)):
            #         new_idxs.add(idxs[indx])
            #     break
            # else:
            idxRangePresent = False
            for range_idx in range(idx-2,idx+3):
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

def detectChPtsAndOutliers(statistics_for_bnss, timeLength = '1-M'):
    beforeDetection = datetime.now()
    firstKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    lastKey = statistics_for_bnss[StatConstants.LAST_TIME_KEY]
    firstDateTime = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    total_time_slots = len(statistics_for_bnss[StatConstants.AVERAGE_RATING])
    chPtsOutliers= dict()
    avg_idxs = None
    for measure_key in StatConstants.MEASURES:
        chOutlierIdxs, chOutlierScores = [], []
        if measure_key in statistics_for_bnss:
            data = statistics_for_bnss[measure_key][firstKey:lastKey+1]

            algo, params = StatConstants.MEASURES_CHANGE_FINDERS[measure_key]

            if algo == StatConstants.AR_UNIFYING:
                r, order, smooth = params
                cf = changefinder.ChangeFinder(r, order, smooth)
                change_scores = []
                for i in range(len(data)):
                    score = cf.update(data[i])
                    change_scores.append(score)
                chOutlierScores = change_scores
                chOutlierIdxs, chOutlierScores = compactChOutlierScoresAndIdx(firstKey, chOutlierIdxs, chOutlierScores,\
                                                                            measure_key, statistics_for_bnss[measure_key][firstKey:],\
                                                                            avg_idxs, algo)
            elif algo == StatConstants.CUSUM:
                chOutlierIdxs = cusum.detect_cusum(data, threshold=params, show=False)

            elif algo == StatConstants.TWITTER_SEASONAL_ANOM_DETECTION:
                chOutlierIdxs = twitterAnomalyDetection(\
                    GraphUtil.getDates(firstDateTime, range(firstKey, total_time_slots), timeLength)\
                    ,data)
            elif algo == StatConstants.LOCAL_AR:
                chOutlierScores = localAR(data, avg_idxs)

            if measure_key == StatConstants.AVERAGE_RATING:
                    ta, tai, taf, amp = chOutlierIdxs
                    chOutlierIdxs = ta
                    avg_idxs = set(ta)

            chPtsOutliers[measure_key] = (chOutlierIdxs, chOutlierScores)
    
    afterDetection = datetime.now()
    print 'Time Taken For Anamoly Detection for Bnss Key',statistics_for_bnss[StatConstants.BNSS_ID],\
        ':', afterDetection-beforeDetection

    return chPtsOutliers