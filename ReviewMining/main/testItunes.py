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
    bnss_key_time_wdw_list = [('5f2c7517a7012640763148a38b1372b6',(71, 76)),
                              ('8df49a65474732e4f63d378df4bd67e4',(93, 98))]
    AppUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list)