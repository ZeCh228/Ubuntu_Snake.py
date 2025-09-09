#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import random
from collections import deque

CHAR_HEAD = 'O'
CHAR_BODY = 'o'
CHAR_FOOD = '*'
CHAR_BORDER = None

UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

MIN_H, MIN_W = 12, 24 

def place_food(height, width, occupied):
    free_cells = [(y, x) for y in range(1, height - 1) for x in range(1, width - 1) if (y, x) not in occupied]
    if not free_cells:
        return None
    return random.choice(free_cells)

def draw_all(win, snake, food, score):
    h, w = win.getmaxyx()
    win.erase()
    win.box()
    status = f" Score: {score}  |  P: Pause  Q: Quit "
    try:
        win.addstr(0, max(2, (w - len(status)) // 2), status)
    except curses.error:
        pass 
    if food:
        try:
            win.addch(food[0], food[1], CHAR_FOOD)
        except curses.error:
            pass
    for i, (y, x) in enumerate(snake):
        ch = CHAR_HEAD if i == 0 else CHAR_BODY
        try:
            win.addch(y, x, ch)
        except curses.error:
            pass
    win.noutrefresh()
    curses.doupdate()

def game_loop(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    curses.noecho()

    while True:
        h, w = stdscr.getmaxyx()
        if h < MIN_H or w < MIN_W:
            stdscr.erase()
            msg = f"Окно слишком мелке ({w}x{h}). Увеличь терминал хотя бы до {MIN_W}x{MIN_H}"
            stdscr.addstr(0, 0, msg)
            stdscr.addstr(2, 0, "Нажми любую клавишу для повтора проверки размера")
            stdscr.refresh()
            stdscr.getch()
            continue

        win = stdscr
        win.nodelay(True)
        win.timeout(120) 
        speed_ms = 120

        start_y, start_x = h // 2, w // 2
        snake = deque([(start_y, start_x + i) for i in range(0, -3, -1)])  # длина 3, вправо
        direction = RIGHT
        next_dir = RIGHT
        score = 0
        occupied = set(snake)
        food = place_food(h, w, occupied)

        draw_all(win, snake, food, score)

        while True:
            try:
                key = win.getch()
            except KeyboardInterrupt:
                return

            if key != -1:
                if key in (curses.KEY_UP, ord('w'), ord('W')):
                    next_dir = UP
                elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
                    next_dir = DOWN
                elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
                    next_dir = LEFT
                elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
                    next_dir = RIGHT
                elif key in (ord('p'), ord('P')):
                    pause_msg = " ПАУЗА - нажми P для продолжения, Q для выхода "
                    try:
                        win.addstr(0, max(2, (w - len(pause_msg)) // 2), pause_msg)
                        win.noutrefresh()
                        curses.doupdate()
                    except curses.error:
                        pass
                    while True:
                        k2 = win.getch()
                        if k2 in (ord('p'), ord('P')):
                            break
                        if k2 in (ord('q'), ord('Q')):
                            return
                elif key in (ord('q'), ord('Q')):
                    return

            if next_dir != OPPOSITE.get(direction):
                direction = next_dir

            head_y, head_x = snake[0]
            dy, dx = direction
            ny, nx = head_y + dy, head_x + dx

            if ny <= 0 or ny >= h - 1 or nx <= 0 or nx >= w - 1:
                break
            if (ny, nx) in snake:
                break

            snake.appendleft((ny, nx))

            if food and (ny, nx) == food:
                score += 1
                occupied = set(snake)
                food = place_food(h, w, occupied)
                speed_ms = max(50, speed_ms - 3)
                win.timeout(speed_ms)
            else:
                snake.pop()

            draw_all(win, snake, food, score)

            if food is None:
                break

        win.nodelay(False)
        result = "ПОБЕДА!" if food is None else "Ты лох!"
        over = f" {result}  Счёт: {score} - Нажми R для рестарта или Q для выхода "
        try:
            win.addstr(h // 2, max(1, (w - len(over)) // 2), over)
        except curses.error:
            pass
        win.refresh()

        while True:
            k = win.getch()
            if k in (ord('r'), ord('R')):
                break
            if k in (ord('q'), ord('Q')):
                return

def main():
    curses.wrapper(game_loop)

if __name__ == "__main__":
    main()
