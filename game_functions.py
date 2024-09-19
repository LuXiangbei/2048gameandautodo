import math

import numpy as np

POSSIBLE_MOVES_COUNT = 4
CELL_COUNT = 4  # 几乘几
NUMBER_OF_SQUARES = CELL_COUNT * CELL_COUNT
NEW_TILE_DISTRIBUTION = np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2])


def initialize_game():
    board = np.zeros(NUMBER_OF_SQUARES, dtype="int")
    # vis = np.zeros((CELL_COUNT, CELL_COUNT), dtype="int")
    initial_twos = np.random.default_rng().choice(NUMBER_OF_SQUARES, 2, replace=False)  # 在棋盘中选择两个不同的随机数
    board[initial_twos] = 2
    board = board.reshape((CELL_COUNT, CELL_COUNT))  # 按照行优先顺序进行重构
    # ndarray.reshape是 Numpy 数组对象的一个方法，用于重新构造数组的形状。该方法的语法如下：
    # ndarray.reshape(shape, order='C')
    # order：可选参数。用于指定元素存储的顺序，可以是’C’, ‘F’，或 ‘A’。默认为 ‘C’。
    # 其中，'C’按行优先顺序存储元素，'F’按列优先顺序存储元素，'A’表示让 Numpy 自动使用最优的方式。
    return board


def push_board_right(board):  # 向右移动的方法（不进行合并）
    new = np.zeros((CELL_COUNT, CELL_COUNT), dtype="int")
    done = False
    for row in range(CELL_COUNT):
        count = CELL_COUNT - 1
        for col in range(CELL_COUNT - 1, -1, -1):  # 从CELL_COUNT - 1开始迭代，直到-1（不包括-1），步长为-1
            if board[row][col] != 0:
                new[row][count] = board[row][col]
                if col != count:
                    done = True
                count -= 1
    return new, done


def merge_elements(board):  # 合并相同的格子
    score = 0
    done = False
    vis = np.zeros((CELL_COUNT, CELL_COUNT), dtype="int")  # 格子是否被合并
    for row in range(CELL_COUNT):
        for col in range(CELL_COUNT - 1, 0, -1):  # 从CELL_COUNT - 1开始迭代，直到0（不包括0），步长为-1
            if board[row][col] == board[row][col - 1] and board[row][col] != 0:
                board[row][col] *= 2
                score += board[row][col] * 4
                board[row][col - 1] = 0
                vis[row][col] = 2  # 2是合并
                done = True
            elif board[row][col] != board[row][col - 1] and board[row][col] != 0:
                vis[row][col] = 1  # 有数字且没合并
    for row in range(CELL_COUNT):
        for col in range(CELL_COUNT - 1, 0, -1):
            if board[row][col] == 0:
                score += 2 ^ 8 + 1
    return board, done, score, vis  # 传出参数


def move_up(board):  # 向上移动的方法（包含合并）
    board = np.rot90(board, -1)  # 顺时针旋转90°把向上变成向右
    board, has_pushed = push_board_right(board)
    board, has_merged, score, vis = merge_elements(board)
    board, _ = push_board_right(board)  # 将合并后的格子转移到最右
    vis, _ = push_board_right(vis)
    board = np.rot90(board)  # 逆时针旋转90°变回向上
    vis = np.rot90(vis)
    move_made = has_pushed or has_merged  # 判断是否移动或者合并
    return board, move_made, score, vis


def move_down(board):  # 向下移动的方法（包含合并）
    board = np.rot90(board)  # 逆时针旋转90°
    board, has_pushed = push_board_right(board)
    board, has_merged, score, vis = merge_elements(board)
    board, _ = push_board_right(board)
    vis, _ = push_board_right(vis)
    board = np.rot90(board, -1)  # 顺时针旋转90°
    vis = np.rot90(vis, -1)
    move_made = has_pushed or has_merged  # 判断是否移动或者合并
    return board, move_made, score, vis


def move_left(board):  # 向左移动的方法（包含合并）
    board = np.rot90(board, 2)  # 逆时针旋转180°
    board, has_pushed = push_board_right(board)
    board, has_merged, score, vis = merge_elements(board)
    board, _ = push_board_right(board)
    vis, _ = push_board_right(vis)
    board = np.rot90(board, -2)  # 顺时针旋转180°
    vis = np.rot90(vis, -2)
    move_made = has_pushed or has_merged  # 判断是否移动或者合并
    return board, move_made, score, vis


def move_right(board):  # 向右移动的方法（包含合并）
    board, has_pushed = push_board_right(board)
    board, has_merged, score, vis = merge_elements(board)
    board, _ = push_board_right(board)
    vis, _ = push_board_right(vis)
    move_made = has_pushed or has_merged  # 判断是否移动或者合并
    return board, move_made, score, vis


def fixed_move(board):  # 按照顺序执行左上下右
    move_order = [move_left, move_up, move_down, move_right]
    score_add = 0
    for func in move_order:
        new_board, move_made, score, _ = func(board)
        if move_made and score_add > score:
            score_add = score
    return board, False


def random_move(board):
    move_made = False
    move_order = [move_right, move_up, move_down, move_left]
    while not move_made and len(move_order) > 0:  # 最多循环四次，若有成功的时候则跳出循环
        move_index = np.random.randint(0, len(move_order))
        move = move_order[move_index]
        board, move_made, score, vis = move(board)  # 向右上下左随机方向移动
        if move_made:
            return board, True, score, vis
        move_order.pop(move_index)  # 删除该方向
    return board, False, score, vis


def add_new_tile(board):  # 移动完随机放置2or4的方法
    tile_value = NEW_TILE_DISTRIBUTION[np.random.randint(0, len(NEW_TILE_DISTRIBUTION))]
    # 从该列表随机抽取一个数，个数为权重.2与4 的个数占权重为9：1
    tile_row_options, tile_col_options = np.nonzero(np.logical_not(board))
    # np.logical_not(board)对数字版取反，非零为False，零为True
    # np.nonzero(np.logical_not(board))返回True的行列索引，传递至tile_row_options, tile_col_options
    tile_loc = np.random.randint(0, len(tile_row_options))  # 随机找个位置放置tile_value（2or4）
    board[tile_row_options[tile_loc], tile_col_options[tile_loc]] = tile_value  # 放置
    return board


# def check_for_win(board):
# return 2048 in board


def smoothness(board):
    smooth_score = 0

    for row in board:
        for i in range(len(row) - 1):
            smooth_score -= abs(math.log2(row[i]) - math.log2(row[i + 1]))

    for col in board.T:
        for i in range(len(col) - 1):
            smooth_score -= abs(math.log2(col[i]) - math.log2(col[i + 1]))

    return smooth_score


def monotonicity(board):
    mono_score = 0

    for row in board:
        diff = np.diff(row)
        if all(d >= 0 for d in diff) or all(d <= 0 for d in diff):
            mono_score += np.sum(diff)

    for col in board.T:
        diff = np.diff(col)
        if all(d >= 0 for d in diff) or all(d <= 0 for d in diff):
            mono_score += np.sum(diff)

    return mono_score


def largest_tile_position(board):
    max_tile = np.max(board)
    max_tile_weight = np.array([[20, 8, 8, 20],
                                [8, 3, 3, 8],
                                [8, 3, 3, 8],
                                [20, 8, 8, 20]])
    max_tile_pos = np.unravel_index(np.argmax(board), (4, 4))
    max_tile_score = max_tile_weight[max_tile_pos]

    return max_tile_score


def evaluate(board):
    empty_tiles = len(np.where(board == 0)[0])
    smooth_score = smoothness(board)
    mono_score = monotonicity(board)
    max_tile_score = largest_tile_position(board)

    return abs(0.1 * (empty_tiles * 1000 + smooth_score * 25 + mono_score * 1 + max_tile_score * 1))
