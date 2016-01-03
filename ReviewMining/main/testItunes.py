'''
@author: santhosh
'''
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

#     AppUtil.doRanking(plotDir)\(180, 185), (187, 192)
#     AppUtil.printSortedReviews(csvFolder, plotDir)
    bnss_key_time_wdw_list = [('284819997', (166,171)),
                              ('284819997', (173, 178)),
                              ('284819997', (180, 185)),
                              ('284819997', (187, 192)),
                              ('319927587', (189, 194)),
                              ('404593641', (158, 163)),
                              ('412629178', (148, 153))]
    AppUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list=bnss_key_time_wdw_list)

