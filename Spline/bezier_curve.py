from math import comb
import numpy as np


class BezierManager:
    def __init__(self, n=3):
        self.n = n
        self.points = np.array([[0, 10], [50, 100], [100, 30]])

    def set_points(self, new_points):
        self.points = new_points
        self.n = len(new_points)
    
    def get_points(self, t):
        extra_points = [self.points]
        for i in range(self.n - 2):
            level_points = []
            for j in range(len(extra_points[i]) - 1):
                level_points += [t * extra_points[i][j] + (1 - t) * extra_points[i][j + 1]]
            extra_points += [np.array(level_points)]
        extra_points += [self.find_point(t)]
        return extra_points

    def find_point(self, t):
        point = np.array([0, 0])
        for i in range(self.n):
            x = np.array(comb(i, self.n) * t ** i * (1. - t) ** (self.n - i) * self.points[i])
            point[0] += x[0]
            point[0] += x[1]
        return point
