from checkerboard import Checkerboard, BLACK_CHESSMAN, WHITE_CHESSMAN, offset, Point
from config import *
import random
from RandomAI import randomAI
def _get_next(cur_runner):
    if cur_runner == BLACK_CHESSMAN:
        return WHITE_CHESSMAN
    else:
        return BLACK_CHESSMAN

class MonteCarloAI:
    def __init__(self, line_points, chessman):
        self._line_points = line_points
        self._my = chessman
        self._opponent = BLACK_CHESSMAN if chessman == WHITE_CHESSMAN else WHITE_CHESSMAN
        self._checkerboard = [[0] * line_points for _ in range(line_points)]
        self.LastDrop = [None,None]

    def reset(self):
        self._checkerboard = [[0] * self._line_points for _ in range(self._line_points)]
    
    def get_drop(self, point):
        self.LastDrop[0] = point
        self._checkerboard[point.Y][point.X] = self._my.Value

    def get_opponent_drop(self, point):
        self._checkerboard[point.Y][point.X] = self._opponent.Value
        self.LastDrop[1] = point


    def check_near_direction(self, point, x_offset, y_offset):
        x = point.X
        y = point.Y
        for step in range(1, 2):
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
        score = 0
        for i in self.LastDrop:
            if i is not None:
                for k in range(-1,2):
                    for l in range(-1,2):
                        if k==l and k==0:
                            continue
                        if self._checkerboard[i.Y + l][i.X + k] == 0:
                            cur_point = Point(i.X + k,i.Y + l)
                            _score = self._get_point_score(cur_point)
                            if _score > score:
                                score = _score
                                point = cur_point
                            elif _score == score and _score > 0:
                                r = random.randint(0, 100)
                                if r % 2 == 0:
                                    point = cur_point
        if score!=0:
            self._checkerboard[point.Y][point.X] = self._my.Value
            return point

        for i in range(self._line_points):
            for j in range(self._line_points):
                if self._checkerboard[j][i] == 0:
                    cur_point = Point(i,j)
                    if self.checkAndSkip(cur_point):
                        _score = self._get_point_score(cur_point)
                        if _score > score:
                            score = _score
                            point = cur_point
                        elif _score == score and _score > 0:
                            r = random.randint(0, 100)
                            if r % 2 == 0:
                                point = cur_point

        self._checkerboard[point.Y][point.X] = self._my.Value
        return point

    def _get_point_score(self, point):
        score = 0
        for i in range(10):      
            score += self.simulator(point)
        print(score)
        return score

    def simulator(self,point):
        import copy
        
        fake_board = Checkerboard(Line_Points)
        fake_ai1 = randomAI(Line_Points, self._my)
        fake_ai2 = randomAI(Line_Points, self._opponent)
        fake_board._checkerboard = copy.deepcopy(self._checkerboard)
        fake_board.drop(self._my,point)
        fake_ai1._checkerboard = copy.deepcopy(fake_board._checkerboard)
        fake_ai2._checkerboard = copy.deepcopy(fake_board._checkerboard)
        cur_runner = self._opponent
        # print("+++++++++++++++++++++++++++++++++++")
        # for i in range(self._line_points):
        #     for j in range(self._line_points):
        #         print(self._checkerboard[j][i],end="")
        #     print('\n')
        while True:
            # print("Step",fake_board.step)
            # if fake_board.is_full():
            #     print("Hit Full")
            fake_ai2.get_opponent_drop(point)
            point = fake_ai2.AI_drop()
            winner = fake_board.drop(cur_runner, point)
 

            if winner is None:
                cur_runner = _get_next(cur_runner)
                # if fake_board.is_full():
                #     print("Hit Full")
                fake_ai1.get_opponent_drop(point)
                point = fake_ai1.AI_drop()
                winner = fake_board.drop(cur_runner, point)
                if winner is not None:
                    del fake_board
                    del fake_ai1
                    del fake_ai2
                    return 1
                cur_runner = _get_next(cur_runner)
            else:
                del fake_board
                del fake_ai1
                del fake_ai2
                return 0
            
        #time.sleep(0.1)
 

        # 画棋盘
        

        
        


if __name__ == '__main__':
    main()