from checkerboard import Checkerboard, BLACK_CHESSMAN, WHITE_CHESSMAN, offset, Point
from config import *
import random
class randomAI:
    def __init__(self, line_points, chessman):
        self._line_points = line_points
        self._my = chessman
        self._opponent = BLACK_CHESSMAN if chessman == WHITE_CHESSMAN else WHITE_CHESSMAN
        self._checkerboard = [[0] * line_points for _ in range(line_points)]
    def reset(self):
        self._checkerboard = [[0] * self._line_points for _ in range(self._line_points)]
    
    def get_drop(self, point):
        self._checkerboard[point.Y][point.X] = self._my.Value

    def get_opponent_drop(self, point):
        if point == None:
            return 
        self._checkerboard[point.Y][point.X] = self._opponent.Value

    def check_near_direction(self, point, x_offset, y_offset):
        x = point.X
        y = point.Y
        for step in range(2):
            x = point.X + step * x_offset
            y = point.Y + step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points:
                if self._checkerboard[y][x]!=0:
                    return True
        return False

    def checkAndSkip(self,point):
        for os in offset:
            if self.check_near_direction(point, os[0], os[1]) == True:
                return True
        return False

    def AI_drop(self):
        point = None
        temp_point = None
        score = 0
        maybe_point = []
        count = 0 
        for i in range(self._line_points):
            for j in range(self._line_points):
                if self._checkerboard[j][i] == 0:
                    count +=1
                    cur_point = Point(i,j)
                    if self.checkAndSkip(cur_point):
                        maybe_point.append(cur_point)
        if len(maybe_point)==0:
            print(count)
            for i in range(self._line_points):
                for j in range(self._line_points):
                    print(self._checkerboard[j][i],end="")
                print('\n')
        point = random.choice(maybe_point)    
        self._checkerboard[point.Y][point.X] = self._my.Value
        return point
