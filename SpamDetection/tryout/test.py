'''
Created on Jan 6, 2016

@author: santhosh
'''
from main import AppUtil
from datetime import datetime
import sys, os
import matplotlib.pyplot as plt
import numpy
from util.data_reader_utils.anon_ecomm_utils.AnonEcommDataReader import AnonEcommDataReader


def tryPlotting():
    fig, axarr = plt.subplots(9, 2, figsize=(20, 20))
    for x in range(9):
        for y in range(2):
            ax = axarr[x][y]
            ax.plot(numpy.random.normal((2*x)+y, 0.2, 150), color='g')
            if y == 1:
                ax.set_xticklabels([])
            position = ax.get_position()
            left = position.x0
            top = position.y0
            right = position.x0 + position.width
            bottom = position.y0 + position.height

            ax.text(0.5*(left + right), 0.5*(bottom + top), 'text',
                            horizontalalignment='center',
                            verticalalignment='center',
                            fontsize=10, color='red',
                            transform=ax.transAxes)


    fig.subplots_adjust(wspace=0.05, hspace=1)
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.test\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'fk')

    bnss_set = set(['8edd789d64c7279592057487ff5bb264', 'd2c9f8c737d5d402593917a618d47821',
                    'f04bc4093557a51a3fdde40ef92464c9', 'beaa44a68be8aa0858cbe3e83a23964a',
                    'dc9d0a3389e58f134ff9dc0435e18962'])
    rdr = AnonEcommDataReader()
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = AppUtil.readData(csvFolder,
                                                                                    readReviewsText=True,
                                                                                    rdr=rdr)
    del bnssIdToBusinessDict, usrIdToUserDict
    revwLogFolder = os.path.join(os.path.join(plotDir, 'bnss_revw'), 'fb57b2749835facf54d9c73f0d9a8d4c')

    if not os.path.exists(revwLogFolder):
        os.makedirs(revwLogFolder)

    for revwId in reviewIdToReviewsDict.keys():
        revw = reviewIdToReviewsDict[revwId]
        if revw.getBusinessID() in bnss_set:
            with open(os.path.join(revwLogFolder, revw.getBusinessID()), 'w') as f:
                f.write('----------------------------------------------------------\n')
                f.write(revw.getReviewText())
                f.write('\n')
                f.write('----------------------------------------------------------\n')

#     currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
#     bnss_key_time_wdw_list = [('284235722', (140, 142)),
#                               ('284819997', (150, 152)),
#                               ('319927587', (120, 122)),
#                               ('284819997', (166, 171)), ('284819997', (173, 178)),
#                               ('284819997', (180, 185)), ('284819997', (187, 192)),
#                               ('319927587', (189, 194)), ('404593641', (158, 163)),
#                               ('412629178', (148, 153)), ('284235722', (147,152))]
#     AppUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list=bnss_key_time_wdw_list)

