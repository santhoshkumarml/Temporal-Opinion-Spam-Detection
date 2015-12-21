__author__ = 'santhosh'

from util import StatConstants
from statsmodels.tsa.ar_model import AR
import copy

def getRangeIdxs(idx):
    start = 3
    end = 4
    while start < end:
        if idx - start < 0:
            start -= 1
        else:
            break
    return (idx-start, idx+end)


def plot(actual_data, pred, scores=[], idxs = []):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    plt.title('EScore')
    plt.xticks(range(0, 160, 10))
    ax1 = fig.add_subplot(1,1,1)
    ax1.plot(actual_data, color='g')
    xvals = range(0, len(pred))
    if len(pred) > 0:
        ax2 = ax1.twinx()
        ax2.plot(pred, color='r')

    if len(scores) > 0:
        ax3 = ax1.twinx()
        ax3.plot(scores, color='b')

    for idx in idxs:
            ax1.axvline(x=xvals[idx], linewidth=2, color='r')

    plt.show()

def squaredResidualError(actual_data, pred_data):
    return (actual_data-pred_data)**2

def makeARPredictions(data, params, idx):
    order = len(params)
    val = 0
    if idx >= 112 and idx<=114:
        print '------------------------'
        print idx
    for p in range(order):
        if idx >= 112 and idx<=114:
            print idx-1-p, data[idx-1-p], data[idx-p-1] * params[p]
        val += data[idx-p-1] * params[p]
    if idx >= 112 and idx<=114:
        print data[idx], val
        print '------------------------'
    # val += numpy.random.normal(0, 1, 1)*math.exp(10**(-6))
    return val

def localAR(data, avg_idxs, measure_key):
    thres = StatConstants.MEASURE_CHANGE_THRES_ITUNES[measure_key]
    needed_direction = StatConstants.MEASURE_DIRECTION[measure_key]
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
    outierIds = []
    outies_scores = []
    preds = []
    print diff_train_windows
    print diff_test_windows
    for wid in range(no_of_windows):
        tr_idx_start, tr_idx_end = diff_train_windows[wid]
        te_idx_start, te_idx_end = diff_test_windows[wid]

        last_filled_idx = len(outies_scores)-1

        ar_mod = AR(data[tr_idx_start:tr_idx_end+1])
        ar_res = ar_mod.fit(ic='bic')
        print ar_res.params

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
            pred = makeARPredictions(copied_data, ar_res.params, i)
            error = squaredResidualError(copied_data[tr_idx_start+i], pred)
            train_pred.append(pred)
            train_error_scores.append(error)

        preds.extend(train_pred)
        outies_scores.extend(train_error_scores)
        # print len(train_error_scores), tr_idx_start, tr_idx_end, corr_start, corr_end, corr_end-corr_start+1, len(scores)

        test_pred = []
        test_error_scores = []
        for i in range(te_idx_start, te_idx_end+1):
            pred = makeARPredictions(copied_data, ar_res.params, i)
            error = squaredResidualError(copied_data[i], pred)
            direction = copied_data[i]-copied_data[i-1]
            if direction < 0:
                direction = StatConstants.DECREASE
            else:
                direction = StatConstants.INCREASE
            if thres and error >= thres:
                if needed_direction == StatConstants.BOTH or direction == needed_direction:
                    outierIds.append(i)
                    copied_data[i] = pred
            test_pred.append(pred)
            test_error_scores.append(error)
        if measure_key == StatConstants.ENTROPY_SCORE:
            print te_idx_start, te_idx_end, data[te_idx_start:te_idx_end+1], test_pred
        preds.extend(test_pred)
        outies_scores.extend(test_error_scores)
        # print len(test_error_scores), te_idx_start, te_idx_end, te_idx_end-te_idx_start+1, len(scores)
        # print '-----------------------------------------------------'
    print '-----------------------------------------------------'
    return preds, outies_scores, outierIds


eSCore = [ 0.31287909,0.93666738,1.12164076,0.91829583,1.37878349,1.37878349,
           0.32997428,0.6098403, 0.77934984,0.83154355,1.37878349,0.82498026,
           1.23890126,1.15677965,1.39214722,0.0,0.0,1.0,0.86312057,1.24067053,
           0.5411884, 0.54356444,0.76420451,0.65002242,0.25253077,0.39845927,
           0.44412605,0.45371634,0.53635965,0.53635965,0.60060858,0.44886449,
           0.48546076,0.55862937,0.62924922,0.52661707,0.61256089,0.33228663,
           0.47983202,0.43949699,0.58301942,0.82805573,0.74959526,0.55726699,
           0.73550858,0.69621226,0.77934984,0.75537541,0.65002242,0.79185835,
           0.55098444,0.79504028,0.69621226,0.50951572,0.81127812,0.86631371,
           0.70627409,0.76420451,0.70883567,0.66096234,0.63945713,0.63945713,
           1.35164412,0.97986876,0.8812909, 0.75537541,0.84535094,0.93666738,
           1.30929667,1.24067053,0.79504028,0.91829583,0.74959526,0.65002242,
           0.66096234,0.65002242,0.3562048, 0.11443935,0.18717626,0.19143325,
           0.27138959,0.40985537,0.50325833,0.55862937,0.61938219,0.79504028,
           0.49716776,0.52936087,0.61938219,0.49123734,0.56650951,0.79504028,
           0.94448853,0.39481485,0.57135497,0.96374599,0.99176015,0.74959526,
           0.86312057,0.62924922,0.94028596,0.7085967,0.50951572,0.47434544,
           0.50951572,0.42200052,0.58301942,0.72192809,0.91829583,0.76420451,
           0.41868431,0.97801556,0.76420451,0.8812909,0.99403021,0.81127812,
           0.68403844,0.46899559,0.8812909, 0.9456603,1.45914792,1.06127812,
           0.77934984,0.67229482,0.79504028,0.8812909,0.91328296,0.63945713,
           0.5746357, 0.75537541,0.97095059,0.60060858,0.73828487,0.77934984,
           0.76420451,0.81127812,0.76420451,0.81127812,0.86312057,0.69621226,
           0.8058576, 0.67229482,0.66096234,0.13303965,0.16670414,0.58301942,
           0.73550858,0.93666738,0.04248305,0.01574348,0.0474844,
           0.13206536,0.22641095,0.31381296,0.37440885,0.03801022,
           0.03801022,0.23987383,0.197453,0.22228483,0.30745653,0.36811501,
         0.33729007,0.08847398,0.03683389,0.03535863,0.1388005, 0.25253077,
         0.38774318,0.20905981,0.08702012,0.06634398,0.09423852,0.08561717,
         0.10035355,0.1350362, 0.13016279,0.11304439,0.07387539,0.05470309,0.11014543,
         0.05295935,0.05363317,0.10384365,0.0,0.0,0.0,0.0,0.07001205,0.18927843,
         0.12148048,0.08283655,0.08366188,0.1670268, 0.11860415,0.0888797, 0.06326231,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,0.17616857,
         .17616857,0.17616857,0.17616857, 0.0]

eSCore = eSCore[36:160]

preds, scores, idxs = localAR(eSCore, set([114]), StatConstants.ENTROPY_SCORE)
actual = eSCore[:len(preds)]
print preds[110:120]
print actual[110:120]
print scores[110:120]
plot(actual, preds, [], idxs)