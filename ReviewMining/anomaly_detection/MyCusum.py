__author__ = 'santhosh'

import numpy

def run_cusum(data, threshold,magnitude=0.5):
    nS, pS= [0 for i in range(len(data)+1)], [0 for i in range(len(data)+1)]
    nG, pG= [0 for i in range(len(data)+1)], [0 for i in range(len(data)+1)]
    start = 0
    changes = []
    magnitude = float(magnitude)
    threshold = float(threshold)
    k = 1
    while k < len(data):
        nS[start] = pS[start] = nG[start] = pG[start] = 0
        current_sample = data[k]
        mean = numpy.mean(data[start:k])
        std = numpy.std(data[start:k+1])
        if std > 0:
            sp = (magnitude/(std**2))*(current_sample - mean - (magnitude/2))
            sn = -((magnitude/(std**2))*(current_sample - mean + (magnitude/2)))
            pS[k] = pS[k-1] + sp
            nS[k] = nS[k-1] + sn
            pG[k] = max(pG[k-1] + current_sample, 0)
            nG[k] = max(nG[k-1] + current_sample, 0)
            if pG[k] > threshold > 0 or nG[k] > threshold > 0:
                nd = k
                if pG[k] > threshold > 0:
                    nc = min(range(start + 1, k + 1), key=lambda key: pS[key - 1])
                else:
                    nc = min(range(start + 1, k + 1), key=lambda key: nS[key - 1])
                nS[nc] = pS[nc] = nG[nc] = pG[nc] = 0
                k = start = nc + 1
                changes.append(nc)
                # print nd, nc
        k += 1
    return changes