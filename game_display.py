import time
from tkinter import Frame, Label, CENTER
import tkinter as tk
import numpy as np

from game_ai import ai_move, move
from game_functions import CELL_COUNT, add_new_tile, initialize_game, \
    move_down, move_left, move_right, move_up
import game_ui as ui

EDGE_LENGTH = CELL_COUNT * 100  # 游戏界面长宽
CELL_COUNT = CELL_COUNT  # 几乘几
CELL_PAD = CELL_COUNT * 1  # 间距
SLEEP_TIME = 0.1


class Display(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.stop_detection = False
        self.add = 0
        self.g = []
        self.vis = np.zeros((CELL_COUNT, CELL_COUNT), dtype="int")
        self.grid()
        self.master.title('2048')
        self.master.bind("<Key>", self.key_press)
        self.bind('<Button>', self.key_press)
        self.commands = {ui.UP_KEY: move_up,
                         ui.DOWN_KEY: move_down,
                         ui.LEFT_KEY: move_left,
                         ui.RIGHT_KEY: move_right,
                         ui.AI_KEY: ai_move,
                         }
        self.grid_cells = []
        self.build_grid()
        self.init_matrix()
        self.draw_grid_cells(self.add)
        self.fix_font()
        self.mainloop()

    def build_grid(self):
        background = Frame(self, bg=ui.GAME_COLOR,
                           width=EDGE_LENGTH, height=EDGE_LENGTH)
        background.grid()
        text_var = str("score={}".format(self.add))
        text_score1 = Label(master=background, text=text_var,
                            bg=ui.GAME_COLOR, justify=CENTER,
                            font=ui.LABEL_FONT, width=10, height=1)
        text_score1.grid(row=4, column=1, columnspan=2)
        text_game = Label(master=background, text="",
                          bg=ui.GAME_COLOR, justify=CENTER,
                          font=ui.LABEL_FONT_B, width=10, height=1)
        text_game.grid(row=5, column=1, columnspan=2)
        self.g.append(text_score1)
        self.g.append(text_game)
        for row in range(CELL_COUNT):
            grid_row = []
            for col in range(CELL_COUNT):
                cell = Frame(background, bg=ui.EMPTY_COLOR,
                             width=EDGE_LENGTH / CELL_COUNT,
                             height=EDGE_LENGTH / CELL_COUNT)
                cell.grid(row=row, column=col, padx=CELL_PAD,
                          pady=CELL_PAD)
                self.update_idletasks()
                t = Label(master=cell, text="",
                          bg=ui.EMPTY_COLOR, justify=CENTER,
                          font=ui.LABEL_FONT_B, width=4, height=2,
                          borderwidth=5, relief="raised")
                t.grid(row=row, column=col)
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def init_matrix(self):  # 初始化矩阵
        self.matrix = initialize_game()

    def draw_grid_cells(self, add):
        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                tile_value = self.matrix[row][col]
                vis = self.vis[row][col]
                if not tile_value:
                    self.grid_cells[row][col].configure(
                        text="", bg=ui.EMPTY_COLOR)
                else:
                    self.grid_cells[row][col].configure(
                        text=str(tile_value),
                        bg=ui.TILE_COLORS[tile_value],
                        fg=ui.LABEL_COLORS[tile_value],
                        font=ui.LABEL_FONT_B)  # 修改数字
                if vis == 2:
                    self.grid_cells[row][col].configure(
                        bg=ui.SHIFT_COLOR)
        self.g[0].configure(text=str(
            "score={}".format(add // 2)), bg=ui.GAME_COLOR)  # 修改分数
        self.update_idletasks()  # 立即更新界面

    def fix_font(self):
        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                tile_value = self.matrix[row][col]
                vis = self.vis[row][col]
                if vis:
                    self.grid_cells[row][col].configure(
                        bg=ui.TILE_COLORS[tile_value])
        self.update_idletasks()

    def p_move(self):
        valid_game = True
        move_count = 0
        while valid_game:
            self.matrix, valid_game, score, self.vis = move(self.matrix, move_count)
            if valid_game:
                self.matrix = add_new_tile(self.matrix)
                self.add += score
                self.draw_grid_cells(self.add)
                time.sleep(SLEEP_TIME)
                self.fix_font()
            move_count += 1
            if not valid_game:
                self.g[1].configure(text=str(
                    "Game Over!"), bg=ui.GAME_COLOR)

    def q_move(self):
        move_count = 0
        self.matrix, move_made, score, self.vis = move(self.matrix, move_count)
        if move_made:
            self.matrix = add_new_tile(self.matrix)
            self.add += score
            self.draw_grid_cells(self.add)
            time.sleep(SLEEP_TIME)
            self.fix_font()
        if not move_made:
            self.g[1].configure(text=str(
                "Game Over!"), bg=ui.GAME_COLOR)
            move_count += 1

    def normal_move(self, event):
        self.matrix, move_made, score, self.vis = self.commands[repr(event.char)](self.matrix)
        if move_made:
            self.matrix = add_new_tile(self.matrix)
            self.add += score
            self.draw_grid_cells(self.add)
            time.sleep(SLEEP_TIME)
            self.fix_font()
        # if not move_made:
        #     self.g[1].configure(text=str(
        #         "Game Over!"), bg=ui.GAME_COLOR)

    def key_press(self, event):
        if self.stop_detection:
            return
        key = repr(event.char)
        # 当使用 repr() 函数时，它会尝试返回一个可以准确表示对象的字符串形式。这个字符串可以被 eval() 函数重新评估为原始对象。
        # 通常情况下，repr() 返回的字符串形式与对象的类型和内部状态有关，可以用于调试、日志记录或其他需要表示对象的字符串场景。
        # 为了确保事件对象中的按键字符可以以一种可显示的方式存储，并且可以在需要时进行后续处理。
        if key == ui.AI_PLAY_KEY:
            self.stop_detection = True
            self.p_move()
        if key == ui.AI_KEY:
            self.q_move()
        if key == ui.RESTART_KEY:
            self.stop_detection = False
            self.add = 0
            self.vis = np.zeros((CELL_COUNT, CELL_COUNT), dtype="int")
            self.init_matrix()
            self.draw_grid_cells(self.add)
            self.g[1].configure(text="", bg=ui.GAME_COLOR)
        elif key in self.commands:
            self.normal_move(event)


gamegrid = Display()
