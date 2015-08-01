# -*- coding: utf-8 -*-
import statsmodels.api as sm
import numpy as np
import scipy as sp
import math




class DTO():
    def __init__(self, nh=8, p=0.125, lh=0.000195, rh=0.005,\
                 a=0.0, b=8.0):
        # self.scores = []
        self.nh = nh
        self.p = p
        self.lh = lh
        self.rh = rh
        self.q = [0.0 for i in range(self.nh)]
        self.whichHs = {idx: 0.0 for idx in range(self.nh)}
        self.a = a
        self.b = b

    def update(self, score):
        idx = 0
        total = 0
        for idx in range(self.nh):
            total += self.q[idx]
            if total >= 1-self.p:
                break
        l = idx

        # print [self.a+((self.b-self.a)*(idx)/(self.nh-2)) for idx in range(self.nh)]

        threshold = self.a+((self.b-self.a)*(l+1)/(self.nh-2))


        whichH = [idx for idx in range(1, self.nh)\
                  if self.a+((self.b-self.a)*(idx-1)/(self.nh-2)) <= score\
                  and self.a+((self.b-self.a)*(idx)/(self.nh-2)) > score]

        if len(whichH) == 0:
            whichH = 0
        else:
            whichH = whichH[0]

        self.whichHs[whichH] += 1

        # if score > 5:
        #     print threshold, {idx: (self.q[idx], self.whichHs[idx]) for idx in range(self.nh)}
        #     print self.a+((self.b-self.a)*(whichH-1)/(self.nh-2)),self.a+((self.b-self.a)*(whichH)/(self.nh-2)),\
        #         score, l, threshold

        # if len(self.scores) > 100 and len(self.scores)<105:
        #     print l
        #     import matplotlib.pyplot as plt
        #     plt.yticks([a+((b-a)*idx/(self.nh-2)) for idx in range(self.nh)])
        #     plt.plot(self.scores,'ro')
        #     plt.show()
        #     plt.plot(self.q, 'ro')
        #     plt.show()

        #
        # print len(self.scores), whichH, threshold, self.scores[-1], a+((b-a)*(whichH-1)/(self.nh-2)), a+((b-a)*whichH/(self.nh-2))
        # if len(self.scores) == 101:
        #     print [a+((b-a)*(idx+1)/(self.nh-2)) for idx in range(self.nh)]
        #     print self.scores

        for idx in range(self.nh):
            if idx == whichH:
                self.q[idx] = (1-self.rh)*self.q[idx]+self.rh
            else:
                self.q[idx] = (1-self.rh)*self.q[idx]

        norm_constant = sum(self.q)+(self.nh*self.lh)

        for idx in range(self.nh):
            self.q[idx] = (self.q[idx]+self.lh)/norm_constant

        # print score, threshold, whichH, self.q

        if score > threshold:
            return True
        else:
            return False

def LevinsonDurbin(r, lpcOrder):
    """
    from http://aidiary.hatenablog.com/entry/20120415/1334458954
    """
    a = np.zeros(lpcOrder + 1,dtype=np.float64)
    e = np.zeros(lpcOrder + 1,dtype=np.float64)

    a[0] = 1.0
    a[1] = - r[1] / r[0]
    e[1] = r[0] + r[1] * a[1]
    lam = - r[1] / r[0]

    for k in range(1, lpcOrder):
        lam = 0.0
        for j in range(k + 1):
            lam -= a[j] * r[k + 1 - j]
        lam /= e[k]

        U = [1]
        U.extend([a[i] for i in range(1, k + 1)])
        U.append(0)

        V = [0]
        V.extend([a[i] for i in range(k, 0, -1)])
        V.append(1)

        a = np.array(U) + lam * np.array(V)
        e[k + 1] = e[k] * (1.0 - lam * lam)

    return a, e[-1]


class _SDAR_1Dim(object):
    def __init__(self, r, order):
        self._r = r
        self._mu = np.random.random()
        self._sigma = np.random.random()
        self._order = order
        self._c = np.zeros(self._order+1)

    def update(self,x,term):
        assert len(term) >= self._order, "term must be order or more"
        term = np.array(term)
        self._mu = (1 - self._r) * self._mu + self._r * x
        for i in range(1,self._order):
            self._c[i] = (1-self._r)*self._c[i]+self._r * (x-self._mu) * (term[-i]-self._mu)
        self._c[0] = (1-self._r)*self._c[0]+self._r * (x-self._mu)*(x-self._mu)
        what,e = LevinsonDurbin(self._c,self._order)
        xhat = np.dot(-what[1:],(term[::-1]  - self._mu))+self._mu
        self._sigma = (1-self._r)*self._sigma + self._r * (x-xhat) * (x-xhat)
        return -math.log(math.exp(-0.5 *(x-xhat)**2/self._sigma)/((2 * math.pi)**0.5 * self._sigma**0.5))

class ChangeFinderSinglepass(object):
    def __init__(self, r = 0.5, order = 1, smooth=7):
        assert order > 0, "order must be 1 or more."
        assert smooth > 2, "term must be 3 or more."
        self._smooth = smooth
        self._order = order
        self._r = r
        self._ts = []
        self._first_scores = []
        self._smoothed_scores = []
        self._convolve = np.ones(self._smooth)
        self._sdar_first = _SDAR_1Dim(r,self._order)
        self.dto = DTO()

    def _add_one(self,one,ts,size):
        ts.append(one)
        if len(ts)==size+1:
            ts.pop(0)

    def _smoothing(self, ts):
        ts = np.array(ts)
        return np.convolve(ts,self._convolve,'valid')[0]

    def _smoothing2(self,ts):
        ts = np.array(ts)
        return np.convolve(ts,self._convolve2,'valid')[0]

    def update(self,x):
        score = 0
        if len(self._ts) == self._order:
            score = self._sdar_first.update(x,self._ts)
            self._add_one(score,self._first_scores, self._smooth)
        self._add_one(x,self._ts, self._order)
        second_target = None
        if len(self._first_scores) == self._smooth:#平滑化
            score = self._smoothing(self._first_scores)
            return score
        else:
            return 0.0
