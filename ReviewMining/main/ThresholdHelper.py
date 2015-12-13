import os

from matplotlib import pyplot as plt

from anomaly_detection import AnomalyDetector
import AppUtil
from util import StatConstants


def doHistogramForMeasure(bins, algo, measure_key, scores):
    fig = plt.figure()
    plt.title('Score histogram')
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel(measure_key)
    print algo, measure_key
    thr1 = AppUtil.getThreshold(scores, 0.20)
    thr2 = AppUtil.getThreshold(scores, 0.15)
    thr3 = AppUtil.getThreshold(scores, 0.10)
    if measure_key in [StatConstants.NO_OF_POSITIVE_REVIEWS, StatConstants.NO_OF_NEGATIVE_REVIEWS,
                       StatConstants.NON_CUM_NO_OF_REVIEWS]:
        ax.hist(scores, bins, alpha=1.00, label=algo+' '+measure_key)
    else:
        ax.hist(scores, bins, alpha=1.00, label=algo+' '+measure_key)

    ax.axvline(x=thr1, linewidth=2, color='r')
    ax.axvline(x=thr2, linewidth=2, color='g')
    ax.axvline(x=thr3, linewidth=2, color='c')
    plt.show()


# strings = f.read()
# p = re.compile('[{][^{]+([{][^{]+[}])+[^}]+BNSS_ID[^}]+[}]')
# p = re.compile('[{].*BNSS_ID[^}]+[}]')
# strings = p.findall(a)
def readScoresFromMeasureLog(plotDir, file_name):
    chPtsOutliers = dict()
    measure_scores = dict()
    measure_log = os.path.join(plotDir, file_name)
    with open(measure_log) as f:
        strings = f.readlines()
        for string in strings:
            string.strip('\r')
            string.strip('\n')
            string = "chPtsOutliers="+string
            try:
                exec(string)
            except:
                continue
            avg_idxs, chOutlierScores = chPtsOutliers[StatConstants.AVERAGE_RATING][StatConstants.CUSUM]
            diff_test_idxs = set()
            for idx in sorted(avg_idxs):
                idx1, idx2 = AnomalyDetector.getRangeIdxs(idx)
                for indx in range(idx1, idx2+1):
                    diff_test_idxs.add(indx)

            for measure_key in chPtsOutliers.keys():
                if measure_key == StatConstants.AVERAGE_RATING \
                        or measure_key == StatConstants.NO_OF_REVIEWS or \
                                measure_key == 'BNSS_ID':
                    continue

                chPtsOutliersEntry = chPtsOutliers[measure_key]
                for algo in chPtsOutliersEntry.keys():
                    chOutlierIdxs, chOutlierScores = chPtsOutliersEntry[algo]

                    if measure_key not in measure_scores:
                        measure_scores[measure_key] = dict()

                    if algo not in measure_scores[measure_key]:
                        measure_scores[measure_key][algo] = []
                    test_measure_scores = []
                    if algo == StatConstants.LOCAL_AR:
                        test_measure_scores = [chOutlierScores[idx] for idx in range(len(chOutlierScores))
                                               if idx in diff_test_idxs]
                    else:
                        test_measure_scores = chOutlierScores

                    test_measure_scores = [score for score in test_measure_scores]

                    measure_scores[measure_key][algo].extend(test_measure_scores)

    return measure_scores


def getThresholdForDifferentMeasures(plotDir, doHist=False):
    measure_scores = readScoresFromMeasureLog(plotDir, "measure_scores.log")
    result = dict()
    measure_noise_threshold = {StatConstants.NO_OF_NEGATIVE_REVIEWS:10000 ,
                               StatConstants.NON_CUM_NO_OF_REVIEWS:2652956,
                               StatConstants.NO_OF_POSITIVE_REVIEWS:2652956}
    for measure_key in measure_scores.keys():
        for algo in measure_scores[measure_key].keys():
            if(algo  == StatConstants.LOCAL_AR):
                continue
            scores = measure_scores[measure_key][algo]
            if measure_key in measure_noise_threshold:
                scores = [sc for sc in scores if sc < measure_noise_threshold[measure_key]]
            thr = AppUtil.getThreshold(scores, 0.15)
            if doHist:
                doHistogramForMeasure(20, algo, measure_key, scores)
            result[measure_key] = thr
    return result