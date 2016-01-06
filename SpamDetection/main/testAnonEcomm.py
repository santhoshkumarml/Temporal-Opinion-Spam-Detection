'''
@author: santhosh
'''

from datetime import datetime
import os
import sys

import AppUtil
import ThresholdHelper
from util.data_reader_utils.anon_ecomm_utils import AnonEcommDataReader
from util import StatConstants


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testAnonEcomm\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    reader = AnonEcommDataReader.AnonEcommDataReader()
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'fk')
    AppUtil.detectAnomaliesForBnsses(csvFolder, plotDir,
                                     StatConstants.MEASURE_CHANGE_THRES_FLIPKART,
                                     doPlot=True, dologStats=False,
                                     find_outlier_idxs=True,
                                     bnss_list=['a9856cb97ebd363a0581d08f27f8b379',
                                                '8edd789d64c7279592057487ff5bb264',
                                                '8df49a65474732e4f63d378df4bd67e4',
                                                '5f2c7517a7012640763148a38b1372b6',
                                                '5f2c7517a7012640763148a38b1372b6',
                                                'fb57b2749835facf54d9c73f0d9a8d4c'])

#     AppUtil.doRanking(plotDir)
#     print ThresholdHelper.getThresholdForDifferentMeasures(plotDir, doHist=True)
#     bnss_key_time_wdw_list = [('8df49a65474732e4f63d378df4bd67e4', (93, 98)),
#                                ('5f2c7517a7012640763148a38b1372b6', (71, 76)),
#                                 ('fb57b2749835facf54d9c73f0d9a8d4c', (32, 37)),
#                                  ('8edd789d64c7279592057487ff5bb264', (31, 36)),
#                                   ('a9856cb97ebd363a0581d08f27f8b379', (30, 35))]
#     AppUtil.doGatherEvidence(csvFolder, plotDir,
#                              rdr=reader,
#                              bnss_key_time_wdw_list=bnss_key_time_wdw_list)