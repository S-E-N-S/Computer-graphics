import math
import numpy as np


def findPoint(points, t):
    n = len(points)
    point = np.array([0, 0])
    for i in n:
        point += math.comb(i, n) * t ** i * (1 - t) ** (n - i) * points[i]
    return point

