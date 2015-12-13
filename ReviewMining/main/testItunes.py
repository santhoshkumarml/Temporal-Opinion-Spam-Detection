__author__ = 'santhosh'

from datetime import datetime
import os
import sys

import AppUtil

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testItunes\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'it')
#         AppUtil.extractAndSerializeBnssStatisticsForBnss(csvFolder, plotDir,\
#                                                      bnsses_list=['284235722'])

#     AppUtil.detectAnomaliesForBnsses(csvFolder, plotDir,
#                                      StatConstants.MEASURE_CHANGE_THRES_ITUNES,
#                                      doPlot=False, dologStats=True)

#     AppUtil.doRanking(plotDir)
    AppUtil.doGatherEvidence(csvFolder, plotDir)