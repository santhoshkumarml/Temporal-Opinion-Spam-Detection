"""
Simple demo with multiple subplots.
"""
import numpy as np
import matplotlib.pyplot as plt


x1 = np.linspace(0.0, 5.0)
x2 = np.linspace(0.0, 2.0)

y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
y2 = np.cos(2 * np.pi * x2)

plt.figure(figsize=(16,18))
for i in range(1, 10):    
    ax= plt.subplot(len(range(1,10)), 1, i)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid('off')
    ax.plot(x1, y1, 'yo-')
    plt.title('A tale of 2 subplots')
    plt.ylabel('Damped oscillation'+str(i))

# plt.subplot(3, 1, 2)
# plt.plot(x2, y2, 'r.-')
# plt.xlabel('time (s)')
# plt.ylabel('Undamped')
# 
# 
# plt.subplot(3, 1, 3)
# plt.plot(x2, y2, 'g.-')
# plt.xlabel('time2 (s)')
# plt.ylabel('damped')
plt.tight_layout()
plt.show()
