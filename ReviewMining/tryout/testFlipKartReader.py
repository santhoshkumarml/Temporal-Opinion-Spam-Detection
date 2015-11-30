import sys, os
from flipkart_utils import FlipkartDataReader
from datetime import datetime
import AppUtil
from util import GraphUtil

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testFlipkKartReader\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    reader = FlipkartDataReader.FlipkartDataReader()
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'fk_bnss_stats')
    AppUtil.doSerializeAllBnss(csvFolder, plotDir, timeLength='1-W', rdr=reader)