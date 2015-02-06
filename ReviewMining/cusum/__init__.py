from __future__ import division
import numpy as np
import cusum
from util import PlotUtil

x = 2*np.sin(2*np.pi*np.arange(0, 3, .01))
ta, tai, taf, amp = cusum.cusum(x, 1, .05)
print ta, tai, taf, amp