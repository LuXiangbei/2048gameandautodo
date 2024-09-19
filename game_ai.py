import numpy as np

from game_functions import random_move, CELL_COUNT, add_new_tile, \
    move_down, move_left, move_right, move_up

NUMBER_OF_MOVES = CELL_COUNT

SPM_SCALE_PARAM = 18
SL_SCALE_PARAM = 7
SEARCH_PARAM = 50


def get_search_params(move_number):
    searches_per_move = SPM_SCALE_PARAM * (1 + (move_number // SEARCH_PARAM))  # 广度
    search_length = SL_SCALE_PARAM * (1 + (move_number // SEARCH_PARAM))  # 深度
    if searches_per_move > 50:
        searches_per_move = 50
    if search_length > 20:
        search_length = 20
    return searches_per_move, search_length


def ai_move(board, searches_per_move, search_length):
    possible_first_moves = [move_left, move_up, move_down, move_right]
    first_move_scores = np.zeros(NUMBER_OF_MOVES)
    for first_move_index in range(len(possible_first_moves)):
        first_move_function = possible_first_moves[first_move_index]
        board_with_first_move, first_move_made, first_move_score, vis = first_move_function(board)
        if first_move_made:
            board_with_first_move = add_new_tile(board_with_first_move)
            first_move_scores[first_move_index] += first_move_score
        else:
            continue
        for _ in range(searches_per_move):
            move_number = 1
            search_board = np.copy(board_with_first_move)  # 保存副本
            game_valid = True
            while game_valid and move_number < search_length:
                search_board, game_valid, score, vis = random_move(search_board)  # 随机移动
                if game_valid:
                    search_board = add_new_tile(search_board)
                    first_move_scores[first_move_index] += score  # 储存各个方向的分数
                    move_number += 1
    best_move_index = np.argmax(first_move_scores)  # 查找最大值并且返回索引（0-3）
    best_move = possible_first_moves[best_move_index]
    search_board, game_valid, score, vis = best_move(board)
    return search_board, game_valid, score, vis


def move(board, move_count):
    searches_per_move, search_length = get_search_params(move_count)
    search_board, game_valid, score, vis = ai_move(board, searches_per_move, search_length)
    return search_board, game_valid, score, vis
