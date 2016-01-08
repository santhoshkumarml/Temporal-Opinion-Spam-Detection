'''
Created on Jan 6, 2016

@author: santhosh
'''

from main import AppUtil
from datetime import datetime
import sys, os
import matplotlib.pyplot as plt
import numpy


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
        print 'Usage: python -m \"evidence.test\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]

    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'it')

#     currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
#     bnss_key_time_wdw_list = [('284235722', (140, 142)),
#                               ('284819997', (150, 152)),
#                               ('319927587', (120, 122)),
#                               ('284819997', (166, 171)), ('284819997', (173, 178)),
#                               ('284819997', (180, 185)), ('284819997', (187, 192)),
#                               ('319927587', (189, 194)), ('404593641', (158, 163)),
#                               ('412629178', (148, 153)), ('284235722', (147,152))]
#     AppUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list=bnss_key_time_wdw_list)

