import math
import numpy as np


def findPoint(points, t):
    n = len(points)
    point = np.array([0, 0])
    for i in n:
        point += math.comb(i, n) * t**i * (1 - t)**(n-i) * points[i]
    return point

class Bezier_manager:
    
    def __init__(self, n=3):
        self.n = n
        self.points = np.array([[0, 10], [50, 100], [100, 30]])


    def set_points(new_points):
        self.points = new_points
        self.n = len(new_points)
    
    
    def get_points(self, t):
        extra_points = [points]
        for i in range(n-2):
            level_points = []
            for j in range(len(extra_points[i]) - 1):
                level_points += t * extra_points[i][j] + (1 - t) * extra_points[i][j + 1]
            extra_points += level_points
        extra_points += [findPoint(points, t)]
        return extra_points