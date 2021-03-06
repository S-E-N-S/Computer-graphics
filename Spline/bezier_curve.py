from math import comb
import numpy as np


class BezierManager:

    def set_points(self, new_points):
        self.points = new_points
        self.n = len(new_points)
    
    def get_points(self, t):
        extra_points = [self.points]
        for i in range(self.n - 2):
            level_points = []
            for j in range(len(extra_points[i]) - 1):
                level_points += [(1 - t) * extra_points[i][j] + t * extra_points[i][j + 1]]
            extra_points += [np.array(level_points)]
        extra_points += [[self.find_point(t)]]
        return extra_points

    def find_point(self, t):
        point = np.array([0, 0], dtype=float)
        for i in range(self.n):
            x = np.array(comb(self.n-1, i) * t ** i * (1. - t) ** (self.n - 1 - i) * self.points[i])
            point += x
        return point
