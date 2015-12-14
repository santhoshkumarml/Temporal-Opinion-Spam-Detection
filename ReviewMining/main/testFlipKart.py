from datetime import datetime
import os
import sys

import AppUtil
import ThresholdHelper
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

    AppUtil.detectAnomaliesForBnsses(csvFolder, plotDir,
                                     StatConstants.MEASURE_CHANGE_THRES_FLIPKART,
                                     doPlot=True, dologStats=False,
                                     find_outlier_idxs=True,
                                     bnss_list=['87b22ad1d4835e47811ab94b373f4969',
                                                'f1d442030d7e75ff158db782c1589fa6',
                                                '1e769f599d3a5cb07ae3f9e8fa6db471',
                                                '407b36eb9e12338d84225ed2a14e5bde',
                                                '5f2c7517a7012640763148a38b1372b6'])

#     AppUtil.doRanking(plotDir)
#     print ThresholdHelper.getThresholdForDifferentMeasures(plotDir, doHist=True)