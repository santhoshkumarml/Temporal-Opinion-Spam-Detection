__author__ = 'santhosh'

import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt

import AppUtil
import RankHelper
from util import SIAUtil
from anomaly_detection import AnomalyDetector
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
    thr4 = AppUtil.getThreshold(scores, 0.05)
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



def tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot, timeLength = '1-W'):
    measuresToBeExtracted = [measure for measure in StatConstants.measures \
                             if measure != StatConstants.max_text_similarity and measure != StatConstants.tf_idf]
    lead_signals = [measure for measure in measuresToBeExtracted if measure in StatConstants.measure_lead_signals]
    measuresToBeExtracted = [measure for measure in set(lead_signals).union(set(measuresToBeExtracted))]

    bnss_stats_dir = os.path.join(plotDir, AppUtil.BNSS_STATS_FOLDER)
    # file_list_size = []
    # for root, dirs, files in os.walk(bnss_stats_dir):
    #     for name in files:
    #         file_list_size.append((name, os.path.getsize(os.path.join(bnss_stats_dir, name))))
    #     file_list_size = sorted(file_list_size, key= lambda x:x[1], reverse=true)
    #
    # bnsskeys = [file_name for file_name,
    #                           size in file_list_size]
    bnssKeys = ['412362331', '425165540', '412629178', '380467238', '314050952',
                '319927587', '396833011', '448999087', '307386350', '318594291',
                '329158810', '489302558', '447556667', '438931724', '360819574',
                '289738462', '399975973', '395697081', '364982249', '303032761',
                '408858076', '340175157', '371119201', '320641659', '334236299',
                '304932383', '379459295', '380507093', '415894489', '363494433',
                '406134561', '299948601', '446708554', '368052618', '423192164',
                '399334913', '330560517', '363955204', '407181075', '376344614',
                '469329213', '327769277', '348824026', '363667391', '481012158',
                '386392481', '332452121']
    # bnsskeys = ['284819997', '412362331', '425165540', '412629178', '380467238',
    #             '314050952', '319927587', '396833011', '448999087', '307386350',
    #             '318594291', '329158810', '489302558', '447556667', '438931724',
    #             '360819574', '289738462', '399975973', '294328109']
    # bnsskeys = ['316239742', '351598228', '391704995', '399734002', '481096722',
    #             '326477287', '385786751', '477148788', '481589275', '448679509']
    # bnsskeys = ['363590051', '351598228', '337950299', '374091507',
    #             '481012158', '320578069', '449453028', '316937016',
    #             '481012158', '433701402', '334982585', '494481220',
    #             '394900607', '403654673', '481012158', '481185291',
    #             '329643619', '494481220', '481185291']
    # bnsskeys = ['481012158']

    for bnss_key in bnssKeys:
        print '------------------------------------------------------------------------------------------------------------'
        statistics_for_bnss = AppUtil.deserializeBnssStats(bnss_key, AppUtil.BNSS_STATS_FOLDER)
        chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(statistics_for_bnss, timeLength,find_outlier_idxs=true)
        # apputil.logstats(bnss_key, plotdir, chptsoutliers, statistics_for_bnss[statconstants.first_time_key])
        if doPlot:
            AppUtil.plotBnssStats(bnss_key, statistics_for_bnss, chPtsOutliers, plotDir,
                                  measuresToBeExtracted, timeLength)
        print '------------------------------------------------------------------------------------------------------------'

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testAlgos\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), '1')
    # bnss_to_reviews_dict = AppUtil.readReviewsForBnssOrUser(plotDir)
    tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot=True)
    # ranked_bnss, bnss_first_time_dict = RankHelper.rankAllAnomalies(plotDir)
    # RankHelper.printRankedBnss(bnss_first_time_dict, ranked_bnss, 50,
    #                            bnss_review_threshold=20, bnss_to_reviews_dict= bnss_to_reviews_dict)
    # print getThresholdForDifferentMeasures(plotDir, doHist=True)