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
from MonteCarlo import MonteCarloAI
from MaxMin import MaxMinAI

def print_text(screen, font, x, y, text, fcolor=(255, 255, 255)):
    imgText = font.render(text, True, fcolor)
    screen.blit(imgText, (x, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('五子棋')

    font1 = pygame.font.SysFont('SimHei', 16)
    font2 = pygame.font.SysFont('SimHei', 36)
    fwidth, fheight = font2.size('黑方获胜')
    black_win_count = 0
    white_win_count = 0

    checkerboard = Checkerboard(Line_Points)
    #computer1 = Baseline(Line_Points, BLACK_CHESSMAN)
    computer1 = MaxMinAI(Line_Points, BLACK_CHESSMAN)
    computer2 = Baseline(Line_Points, WHITE_CHESSMAN)
    MonteCarloAI

    cur_runner = BLACK_CHESSMAN
    winner = None
    AI_point1 = Point(15, 15)
    checkerboard.drop(cur_runner, AI_point1)
    computer1.get_drop(AI_point1)
    cur_runner = _get_next(cur_runner)

    import time
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
        
        computer2.get_opponent_drop(AI_point1)
        AI_point1 = computer2.AI_drop()
        winner = checkerboard.drop(cur_runner, AI_point1)
 

        if winner is None:
            cur_runner = _get_next(cur_runner)
            computer1.get_opponent_drop(AI_point1)
            AI_point1 = computer1.AI_drop()
            winner = checkerboard.drop(cur_runner, AI_point1)

            if winner is not None:
                black_win_count += 1
            cur_runner = _get_next(cur_runner)
        else:
            white_win_count += 1
        #time.sleep(0.1)
 

        # 画棋盘
        _draw_checkerboard(screen)

        # 画棋盘上已有的棋子
        for i, row in enumerate(checkerboard.checkerboard):
            for j, cell in enumerate(row):
                if cell == BLACK_CHESSMAN.Value:
                    _draw_chessman(screen, Point(j, i), BLACK_CHESSMAN.Color)
                elif cell == WHITE_CHESSMAN.Value:
                    _draw_chessman(screen, Point(j, i), WHITE_CHESSMAN.Color)

        _draw_left_info(screen, font1, cur_runner, black_win_count, white_win_count)

        if winner:
            print_text(screen, font2, (SCREEN_WIDTH - fwidth)//2, (SCREEN_HEIGHT - fheight)//2, winner.Name + '获胜', RED_COLOR)
            computer1.reset()
            computer2.reset()
            checkerboard.reset()
            cur_runner = BLACK_CHESSMAN
            winner = None
            AI_point1 = Point(15, 15)
            checkerboard.drop(cur_runner, AI_point1)
            computer1.get_drop(AI_point1)
            cur_runner = _get_next(cur_runner)
            for i in range(21):
                for j in range(21):
                    print(checkerboard.checkerboard[i][j],end=" ")
                print("\n")
        pygame.display.flip()


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



if __name__ == '__main__':
    main()