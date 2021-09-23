# coding:utf-8
from MyChess.Chess_Core import Chessboard
from MyChess.Chess_Core import Chessman


def print_chessman_name(chessman):
    if chessman:
        print(chessman.name)
    else:
        print("None")


def main():
    cbd = Chessboard.Chessboard('000')
    # cbd.init_board()
    # cbd.export2file("./data/start_board")
    cbd.LoadFromFile("./data/start_board")
    #cbd.print_to_cl()
    step = 0
    while True:
        result = cbd.is_end()
        #cbd.export2file('./data/{}_board'.format(step))
        if result is not None:
            #print("Finish with {} Step".format(step))
            return result,step

        name_list = []
        step +=1
        if step>500:
            return 'failed',0
        for i in cbd.chessmans_hash:
            name_list.append(i)
        cbd.calc_chessmans_moving_list()
        # if cbd.is_red_turn:
        #     print("is_red_turn")
        # else:
        #     print("is_black_turn")
        is_correct_chessman = False
        is_correct_position = False
        chessman = None
        while not is_correct_chessman:
            # title = "请输入棋子名字: "
            # input_chessman_name = input(title)
            import random
            input_chessman_name = random.choice(name_list)
            chessman = cbd.get_chessman_by_name(input_chessman_name)
            if chessman != None and chessman.is_red == cbd.is_red_turn:
                is_correct_chessman = True
                possible_move = []
                for point in chessman.moving_list:
                    possible_move.append([point.x, point.y])
            # else:
            #     print("没有找到此名字的棋子或未轮到此方走子")
                if len(possible_move)==0:
                    is_correct_chessman = False

        while not is_correct_position:
            # title = "请输入落子的位置: "
            # input_chessman_position = input(title)
            import random
            choose_move = random.choice(possible_move)
            input_chessman_position = str(choose_move[0])+str(choose_move[1])

            is_correct_position = chessman.move(
                int(input_chessman_position[0]), int(input_chessman_position[1]))
            if is_correct_position:
                #cbd.print_to_cl()
                cbd.clear_chessmans_moving_list()


if __name__ == '__main__':
    import time
    start = time.time()
    total = 1000
    count = total
    red = 0
    black = 0
    step_sum = 0
    while total > 0:
        result,step = main()
        if result == 'failed':
            continue
        print(total)
        total = total-1
        step_sum+=step
        if result == 'red':
            red+=1
        else:
            black+=1
    end = time.time()
    print("Red: {}  Black: {}  Total:{}".format(red, black,count))
    print("Average Step: {}".format(step_sum/count))
    print("Time Consume: {} second    Average Time: {}".format(round(end-start,4),round((end-start)/count,4)))