__author__ = 'santhosh'

import os
import math

from util import StatConstants
from anomaly_detection import AnomalyDetector
import matplotlib.pyplot as plt



def doHistogramForFeature(bins, scores):
    for score in scores:
        fig = plt.figure()
        plt.title('Score histogram')
        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlabel('feature')

        ax.hist(score, bins, alpha=1.00)
        plt.show()

def readChPtsOutliers(string):
    chPtsOutliers = dict()
    string.strip('\r')
    string.strip('\n')
    string = "chPtsOutliers=" + string
    try:
        exec (string)
    except:
        pass
    return chPtsOutliers


def extractFeaturesForRankingAnomalies(bnss_key, chPtsOutliers, test_windows, measures, magnitude_divider):
    weighted_anomalies_for_window = dict()
    avg_anomaly_for_time_window = dict()
    max_anomaly_for_time_window = dict()
    ratio_of_anomalies_measure = dict()
    if not magnitude_divider:
        MAGNITURE_DIVIDER = {StatConstants.ENTROPY_SCORE:18, StatConstants.NO_OF_NEGATIVE_REVIEWS:100000,\
                             StatConstants.NO_OF_POSITIVE_REVIEWS:100000, StatConstants.NON_CUM_NO_OF_REVIEWS:100000}
    else:
        MAGNITURE_DIVIDER = magnitude_divider

    for window in test_windows:
        measures_changed = 0
        for measure_key in chPtsOutliers.keys():
            if measure_key in StatConstants.MEASURE_LEAD_SIGNALS or measure_key == StatConstants.BNSS_ID\
                    or measure_key == StatConstants.FIRST_TIME_KEY:
                continue
            chPtsOutliersIdxs, chPtsOutlierScores = chPtsOutliers[measure_key][StatConstants.LOCAL_AR]
            idx1, idx2 = window
            idxs = [idx for idx in chPtsOutliersIdxs if idx>=idx1 and idx<=idx2 and idx < len(chPtsOutlierScores)]
            if len(idxs) > 0:
                try:
                    idx = max(idxs, key= lambda x: chPtsOutlierScores[x])
                except:
                    print bnss_key, measure_key, idxs, len(chPtsOutlierScores)
                    print chPtsOutlierScores
                    raise
                measures_changed += 1
                no_of_changes_before = chPtsOutliersIdxs.index(idx)
                div = MAGNITURE_DIVIDER[measure_key] if measure_key in MAGNITURE_DIVIDER else 1.0

                if window not in weighted_anomalies_for_window:
                    weighted_anomalies_for_window[window] = 0.0
                weighted_anomalies_for_window[window] += ((1.0 / (1 + no_of_changes_before)) * (chPtsOutlierScores[idx]/div))

                if window not in avg_anomaly_for_time_window:
                    avg_anomaly_for_time_window[window] = 0.0

                if window not in max_anomaly_for_time_window:
                    max_anomaly_for_time_window[window] = 0.0

                avg_anomaly = avg_anomaly_for_time_window[window]
                max_anomaly = max_anomaly_for_time_window[window]

                avg_anomaly += (chPtsOutlierScores[idx]/div)
                max_anomaly = max(max_anomaly, (chPtsOutlierScores[idx]/div))

        if measures_changed > 0:
            avg_anomaly_for_time_window[window] = avg_anomaly
            max_anomaly_for_time_window[window] = max_anomaly

            avg_anomaly = avg_anomaly_for_time_window[window]
            avg_anomaly_for_time_window[window] = (avg_anomaly/measures_changed)

            weighted_anomalies_for_window[window] /= measures_changed

            ratio_of_anomalies_measure[window] = float(measures_changed)/(len(measures)-1)
        else:
            avg_anomaly_for_time_window[window] = 0.0
            max_anomaly_for_time_window[window] = 0.0
            weighted_anomalies_for_window[window] = 0.0
            ratio_of_anomalies_measure[window] = 0.0

    return ratio_of_anomalies_measure, weighted_anomalies_for_window, avg_anomaly_for_time_window, max_anomaly_for_time_window

def rankAllAnomalies(plotDir):
    measure_log = os.path.join(plotDir, "scores_with_outliers.log")
    measuresToBeExtracted = [measure for measure in StatConstants.MEASURES \
                             if measure != StatConstants.MAX_TEXT_SIMILARITY and measure != StatConstants.TF_IDF]
    lead_signals = [measure for measure in measuresToBeExtracted if measure in StatConstants.MEASURE_LEAD_SIGNALS]
    measuresToBeExtracted = [measure for measure in set(lead_signals).union(set(measuresToBeExtracted))]
    with open(measure_log) as f:
        aF1, aF2, aF3, aF4 = dict(), dict(), dict(), dict()
        strings = f.readlines()
        magnitude_divider = dict()
        for string in strings:
            chPtsOutliers = readChPtsOutliers(string)
            if StatConstants.BNSS_ID not in chPtsOutliers:
                continue
            for measure_key in chPtsOutliers.keys():
                if measure_key in StatConstants.MEASURE_LEAD_SIGNALS or measure_key == StatConstants.BNSS_ID\
                        or measure_key == StatConstants.FIRST_TIME_KEY:
                    continue

                chPtsOutliersIdxs, chPtsOutlierScores = chPtsOutliers[measure_key][StatConstants.LOCAL_AR]

                if len(chPtsOutlierScores) > 0:
                    max_outlier_score = max(chPtsOutlierScores)
                    if measure_key not in magnitude_divider:
                        magnitude_divider[measure_key] = max_outlier_score
                    if max_outlier_score > magnitude_divider[measure_key]:
                        magnitude_divider[measure_key] = max_outlier_score

        for string in strings:
            chPtsOutliers = readChPtsOutliers(string)
            if StatConstants.BNSS_ID not in chPtsOutliers:
                continue
            bnss_key = chPtsOutliers[StatConstants.BNSS_ID]
            avg_idxs, chOutlierScores = chPtsOutliers[StatConstants.AVERAGE_RATING][StatConstants.CUSUM]
            diff_test_windows = [AnomalyDetector.getRangeIdxs(idx) for idx in sorted(avg_idxs)]

            f1, f2, f3, f4 = \
                extractFeaturesForRankingAnomalies(bnss_key,
                                                   chPtsOutliers,
                                                   diff_test_windows,
                                                   measuresToBeExtracted,
                                                   magnitude_divider)
            for window in diff_test_windows:
                aF1[(bnss_key, window)] = f1[window]
                aF2[(bnss_key, window)] = f2[window]
                aF3[(bnss_key, window)] = f3[window]
                aF4[(bnss_key, window)] = f4[window]


        # doHistogramForFeature(bins=10,scores=[scores1, scores2, scores3, scores4])

        rankAnomaliesPartially(aF1, aF2, aF3, aF4, strings)
        # rankAnomaliesByAllFeatures(aF1, aF2, aF3, aF4, strings)


def rankAnomaliesPartially(aF1, aF2, aF3, aF4, strings, topK=50):
    Keys1D = sorted(aF1.keys(), key=lambda key: aF1[key], reverse=True)
    Keys2D = sorted(aF2.keys(), key=lambda key: aF2[key], reverse=True)
    Keys3D = sorted(aF3.keys(), key=lambda key: aF3[key], reverse=True)
    Keys4D = sorted(aF4.keys(), key=lambda key: aF4[key], reverse=True)

    ranked_bnss = []
    visited_bnss = set()
    bnss_first_time_dict = dict()

    for string in strings:
        chPtsOutliers = readChPtsOutliers(string)
        if StatConstants.BNSS_ID not in chPtsOutliers:
            continue
        bnss_key = chPtsOutliers[StatConstants.BNSS_ID]
        bnss_first_time_dict[bnss_key] = chPtsOutliers[StatConstants.FIRST_TIME_KEY]

    idx = 0
    while len(visited_bnss) < topK:
        key1 = Keys1D[idx]
        key2 = Keys2D[idx]
        key3 = Keys3D[idx]
        key4 = Keys4D[idx]

        if key1 not in visited_bnss:
            ranked_bnss.append(key1)
            visited_bnss.add(key1)

        if key2 not in visited_bnss:
            ranked_bnss.append(key2)
            visited_bnss.add(key2)

        if key3 not in visited_bnss:
            ranked_bnss.append(key3)
            visited_bnss.add(key3)

        if key4 not in visited_bnss:
            ranked_bnss.append(key4)
            visited_bnss.add(key4)

        idx += 1

    print '-------------------------------------------------------------------------------------------------'
    for key_idx in range(0, topK):
        key = ranked_bnss[key_idx]
        bnss_key, (idx1, idx2) = key
        idx1 += bnss_first_time_dict[bnss_key]
        idx2 += bnss_first_time_dict[bnss_key]
        print bnss_key, (idx1, idx2)
    print '-------------------------------------------------------------------------------------------------'

def rankAnomaliesByAllFeatures(aF1, aF2, aF3, aF4, strings, topK=50):
    bnss_first_time_dict = dict()
    final_scores_dict = dict()

    scores1 = sorted(aF1.values())
    scores2 = sorted(aF2.values())
    scores3 = sorted(aF3.values())
    scores4 = sorted(aF4.values())

    for string in strings:
        chPtsOutliers = readChPtsOutliers(string)
        if StatConstants.BNSS_ID not in chPtsOutliers:
            continue
        bnss_key = chPtsOutliers[StatConstants.BNSS_ID]
        bnss_first_time_dict[bnss_key] = chPtsOutliers[StatConstants.FIRST_TIME_KEY]
        avg_idxs, chOutlierScores = chPtsOutliers[StatConstants.AVERAGE_RATING][StatConstants.CUSUM]
        diff_test_windows = [AnomalyDetector.getRangeIdxs(idx) for idx in sorted(avg_idxs)]

        for window in diff_test_windows:
            score1 = aF1[(bnss_key, window)]
            score2 = aF2[(bnss_key, window)]
            score3 = aF3[(bnss_key, window)]
            score4 = aF4[(bnss_key, window)]

            nscore1 = float(scores1.index(score1)) / float(len(scores1))
            nscore2 = float(scores2.index(score2)) / float(len(scores2))
            nscore3 = float(scores3.index(score3)) / float(len(scores3))
            nscore4 = float(scores4.index(score4)) / float(len(scores4))

            # nscore1 = (nscore1 ** 2) * 0.4
            # nscore2 = (nscore2 ** 2) * 0.2
            # nscore3 = (nscore3 ** 2) * 0.2
            # nscore4 = (nscore4 ** 2) * 0.2

            nscore1 = (nscore1 ** 2)
            nscore2 = (nscore2 ** 2)
            nscore3 = (nscore3 ** 2)
            nscore4 = (nscore4 ** 2)


            final_score = math.sqrt(sum([nscore1, nscore2, nscore3, nscore4]) / 4)
            final_scores_dict[(bnss_key, window)] = (final_score, nscore1, nscore2, nscore3, nscore4)

    sorted_keys = sorted(final_scores_dict.keys(), key= lambda  v : final_scores_dict[v][0], reverse=True)
    print '-------------------------------------------------------------------------------------------------'
    for key_idx in range(0, topK):
        key = sorted_keys[key_idx]
        bnss_key, (idx1, idx2) = key
        idx1 += bnss_first_time_dict[bnss_key]
        idx2 += bnss_first_time_dict[bnss_key]
        print bnss_key, (idx1, idx2) , final_scores_dict[key]
    print '-------------------------------------------------------------------------------------------------'

