import os
import sys
from datetime import datetime

import AppUtil
from anomaly_detection import AnomalyDetector
from flipkart_utils import FlipkartDataReader
from util import StatConstants

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testFlipkKart\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    reader = FlipkartDataReader.FlipkartDataReader()
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'fk')
#     bnss_list = AppUtil.extractAndSerializeBnssStatisticsForBnss(csvFolder, plotDir,
#                                                                  bnss_list_start=0,
#                                                                  bnss_list_end=500000,
#                                                                  rdr=reader)
    AppUtil.detectAnomaliesForBnsses(csvFolder, plotDir, doPlot=False, dologStats=True)