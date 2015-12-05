import os
import sys
from datetime import datetime

import AppUtil
from anomaly_detection import AnomalyDetector
from flipkart_utils import FlipkartDataReader
from util import StatConstants


def tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot, timeLength = '1-W'):
    measuresToBeExtracted = [measure for measure in StatConstants.MEASURES \
                             if measure != StatConstants.MAX_TEXT_SIMILARITY and measure != StatConstants.TF_IDF]
    lead_signals = [measure for measure in measuresToBeExtracted if measure in StatConstants.MEASURE_LEAD_SIGNALS]
    measuresToBeExtracted = [measure for measure in set(lead_signals).union(set(measuresToBeExtracted))]

    bnss_stats_dir = os.path.join(plotDir, AppUtil.FLIPKART_BNSS_STATS_FOLDER)
    file_list_size = []
    for root, dirs, files in os.walk(bnss_stats_dir):
        for name in files:
            file_list_size.append((name, os.path.getsize(os.path.join(bnss_stats_dir, name))))
        file_list_size = sorted(file_list_size, key=lambda x: x[1], reverse=True)

    bnssKeys = [file_name for file_name,
                              size in file_list_size]
    bnssKeys = bnssKeys[30:60]

    for bnss_key in bnssKeys:
        print '------------------------------------------------------------------------------------------------------------'
        statistics_for_bnss = AppUtil.deserializeBnssStats(bnss_key, os.path.join(plotDir, AppUtil.FLIPKART_BNSS_STATS_FOLDER))
        chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(statistics_for_bnss, timeLength, find_outlier_idxs=False)
        # AppUtil.logStats(bnss_key, plotDir, chPtsOutliers, statistics_for_bnss[StatConstants.FIRST_TIME_KEY])
        if doPlot:
            AppUtil.plotBnssStats(bnss_key, statistics_for_bnss, chPtsOutliers, plotDir,
                                  measuresToBeExtracted, timeLength)
        print '------------------------------------------------------------------------------------------------------------'

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testFlipkKart\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    reader = FlipkartDataReader.FlipkartDataReader()
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'fk')
    # AppUtil.doSerializeAllBnss(csvFolder, plotDir, rdr=reader)
    tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot=True)