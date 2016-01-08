'''
Created on Jan 8, 2016

@author: santhosh
'''

import matplotlib.pyplot as plt
import matplotlib
import math, numpy


def tryPlottingText():
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

def tryPlottingLogScaleWithTicks():
    f = plt.figure()
    ax = f.add_subplot(111)
    y = numpy.arange(0, 0.09, 0.01)
    ax.plot(y)
    yticks =  ax.get_yticks()

    indx_inc =  len(yticks) / 5
    print indx_inc, len(yticks)

    ytick_indx = [i for i in numpy.arange(0, len(yticks), indx_inc)]

    ax.set_yticks([yticks[i] for i in ytick_indx])

    plt.show()


tryPlottingLogScaleWithTicks()