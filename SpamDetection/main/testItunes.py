'''
@author: santhosh
'''
from datetime import datetime
import os
import sys

import AppUtil
from util import StatConstants


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"main.testItunes\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'it')

    bnss_list = ['284235722', '284819997', '319927587', '404593641', '412629178']
    AppUtil.detectAnomaliesForBnsses(csvFolder, plotDir,
                                     StatConstants.MEASURE_CHANGE_THRES_ITUNES,
                                     doPlot=True, dologStats=True, bnss_list=bnss_list)
