"""五子棋之人机对战"""

import sys
import random
import pygame
from pygame.locals import *
import pygame.gfxdraw
from checkerboard import Checkerboard, BLACK_CHESSMAN, WHITE_CHESSMAN, offset, Point

from config import *
from BaseAI import AI as Baseline
from RandomAI import randomAI
WIN_REWARD = 10
SUCCESS_REWARD = 0.1
FAILED_REWARD = -10
LOSE_REWARD = -10

def print_text(screen, font, x, y, text, fcolor=(255, 255, 255)):
    imgText = font.render(text, True, fcolor)
    screen.blit(imgText, (x, y))


def _get_next(cur_runner):
    if cur_runner == BLACK_CHESSMAN:
        return WHITE_CHESSMAN
    else:
        return BLACK_CHESSMAN


# 画棋盘
def _draw_checkerboard(screen):
    # 填充棋盘背景色
    screen.fill(Checkerboard_Color)
    # 画棋盘网格线外的边框
    pygame.draw.rect(screen, BLACK_COLOR, (Outer_Width, Outer_Width, Border_Length, Border_Length), Border_Width)
    # 画网格线
    for i in range(Line_Points):
        pygame.draw.line(screen, BLACK_COLOR,
                         (Start_Y, Start_Y + SIZE * i),
                         (Start_Y + SIZE * (Line_Points - 1), Start_Y + SIZE * i),
                         1)
    for j in range(Line_Points):
        pygame.draw.line(screen, BLACK_COLOR,
                         (Start_X + SIZE * j, Start_X),
                         (Start_X + SIZE * j, Start_X + SIZE * (Line_Points - 1)),
                         1)
    # 画星位和天元
    for i in (3, 9, 15):
        for j in (3, 9, 15):
            if i == j == 9:
                radius = 5
            else:
                radius = 3
            # pygame.draw.circle(screen, BLACK, (Start_X + SIZE * i, Start_Y + SIZE * j), radius)
            pygame.gfxdraw.aacircle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)
            pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)


# 画棋子
def _draw_chessman(screen, point, stone_color):
    # pygame.draw.circle(screen, stone_color, (Start_X + SIZE * point.X, Start_Y + SIZE * point.Y), Stone_Radius)
    pygame.gfxdraw.aacircle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)
    pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)


# 画左侧信息显示
def _draw_left_info(screen, font, cur_runner, black_win_count, white_win_count):
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, Start_X + Stone_Radius2), BLACK_CHESSMAN.Color)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, Start_X + Stone_Radius2 * 4), WHITE_CHESSMAN.Color)

    print_text(screen, font, RIGHT_INFO_POS_X, Start_X + 3, 'AI Alpha', BLUE_COLOR)
    print_text(screen, font, RIGHT_INFO_POS_X, Start_X + Stone_Radius2 * 3 + 3, 'AI Beta', BLUE_COLOR)

    print_text(screen, font, SCREEN_HEIGHT, SCREEN_HEIGHT - Stone_Radius2 * 8, '战况：', BLUE_COLOR)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, SCREEN_HEIGHT - int(Stone_Radius2 * 4.5)), BLACK_CHESSMAN.Color)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, SCREEN_HEIGHT - Stone_Radius2 * 2), WHITE_CHESSMAN.Color)
    print_text(screen, font, RIGHT_INFO_POS_X, SCREEN_HEIGHT - int(Stone_Radius2 * 5.5) + 3, f'{black_win_count} 胜', BLUE_COLOR)
    print_text(screen, font, RIGHT_INFO_POS_X, SCREEN_HEIGHT - Stone_Radius2 * 3 + 3, f'{white_win_count} 胜', BLUE_COLOR)


def _draw_chessman_pos(screen, pos, stone_color):
    pygame.gfxdraw.aacircle(screen, pos[0], pos[1], Stone_Radius2, stone_color)
    pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], Stone_Radius2, stone_color)


# 根据鼠标点击位置，返回游戏区坐标
def _get_clickpoint(click_pos):
    pos_x = click_pos[0] - Start_X
    pos_y = click_pos[1] - Start_Y
    if pos_x < -Inside_Width or pos_y < -Inside_Width:
        return None
    x = pos_x // SIZE
    y = pos_y // SIZE
    if pos_x % SIZE > Stone_Radius:
        x += 1
    if pos_y % SIZE > Stone_Radius:
        y += 1
    if x >= Line_Points or y >= Line_Points:
        return None

    return Point(x, y)




def flatten(a):
    if not isinstance(a, (list, )):
        return [a]
    else:
        b = []
        for item in a:
            b += flatten(item)
    return b


class Environment:
    def __init__(self):
        pygame.init()
        self.lines = Line_Points
        self.action_space = Line_Points*Line_Points
        self.observation_space = Line_Points*Line_Points
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('五子棋')
        font1 = pygame.font.SysFont('SimHei', 16)
        font2 = pygame.font.SysFont('SimHei', 36)
        fwidth, fheight = font2.size('黑方获胜')
        self.checkerboard = Checkerboard(Line_Points)
        self.opponent = randomAI(Line_Points, BLACK_CHESSMAN)

        self.DQN_WIN = 0
        self.BASE_WIN = 0
        self.STEP = 0
        self.MATCH = 0
        # Assign AI as WHITE_CHESSMAN
        # import random
        # side = random.randint(0,100)
        # if side%2 == 0: # DQN as BLACK
        #     self.side = BLACK_CHESSMAN
        # else:
        #     self.side = WHITE_CHESSMAN

        self.side = BLACK_CHESSMAN
        if self.side == BLACK_CHESSMAN:
            self.opponent = Baseline(Line_Points, WHITE_CHESSMAN)
        else:
            self.opponent = Baseline(Line_Points, BLACK_CHESSMAN)

        self.cur_runner = BLACK_CHESSMAN
        self.winner = None

        # Eg. Point(15,17) ---> flatten index: 542
        #                  ---> Matrix[17][15] = 1
        #AI_point1 = Point(15, 15)
        AI_point1 = 15*Line_Points+15
        self.step(AI_point1)

    def reset(self):
        self.MATCH += 1
        self.checkerboard.reset()
        self.opponent.reset()
        self.cur_runner = BLACK_CHESSMAN
        self.winner = None
        AI_point1 = 15*Line_Points+15
        self.step(AI_point1)
        return flatten(self.checkerboard._checkerboard)

        
    def render(self):
        # _draw_checkerboard(self.screen)
        # for i, row in enumerate(self.checkerboard.checkerboard):
        #     for j, cell in enumerate(row):
        #         if cell == BLACK_CHESSMAN.Value:
        #             _draw_chessman(self.screen, Point(j, i), BLACK_CHESSMAN.Color)
        #         elif cell == WHITE_CHESSMAN.Value:
        #             _draw_chessman(self.screen, Point(j, i), WHITE_CHESSMAN.Color)
        print("Steping ---- DQN WIN {} BASE WIN {} Average Step {}".format(self.DQN_WIN,self.BASE_WIN,round(self.STEP/self.MATCH,3)))
        pygame.display.flip()

    def step(self,AI_point1):
        '''
        Input: Drop pos
        Return: s_, r, done,info
        '''
        self.STEP += 1
        GAME_OVER = True
        
        y = int(AI_point1/self.lines)
        x = int(AI_point1%self.lines)
        AI_point1 = Point(x,y)
        # Failed to drop (already exsit)
        if self.checkerboard.can_drop(AI_point1)==False:
            self.BASE_WIN += 1
            self.checkerboard.reset()
            #print("Drop Error")
            return flatten(self.checkerboard._checkerboard),FAILED_REWARD,GAME_OVER

        # Succ drop
        self.winner = self.checkerboard.drop(self.cur_runner, AI_point1)
        if self.winner is not None:
            self.DQN_WIN +=1
            return flatten(self.checkerboard._checkerboard),WIN_REWARD,GAME_OVER

        # DQN didnt kill game
        self.cur_runner = _get_next(self.cur_runner)
        self.opponent.get_opponent_drop(AI_point1)
        AI_point1 = self.opponent.AI_drop()

        if self.checkerboard.can_drop(AI_point1)==False:
            self.checkerboard.reset()
            self.DQN_WIN +=1
            print("Hit DEBUG point")
            return flatten(self.checkerboard._checkerboard),WIN_REWARD,GAME_OVER

        self.winner = self.checkerboard.drop(self.cur_runner, AI_point1)
        if self.winner is not None:
            self.BASE_WIN += 1
            return flatten(self.checkerboard._checkerboard),LOSE_REWARD,GAME_OVER

        #continue game
        self.cur_runner = _get_next(self.cur_runner)    
        GAME_OVER = False
        return flatten(self.checkerboard._checkerboard),SUCCESS_REWARD,GAME_OVER


