import pygame_textinput
import pygame
import pygame.locals as pl
import logging
import threading
import time
import os
import sys
import random
import copy

##############################################
###             Global Variables           ###
##############################################

##############################################
###             Class Defintions           ###
##############################################
SHIFT_DIR_LEFT = 0
SHIFT_DIR_RIGHT = 1
SHIFT_DIR_UP = 2
SHIFT_DIR_DOWN = 3

##############################################
###          Functiion Defintions          ###
##############################################

'''
Examples:

4 4 4 4 (shift right) => 8 8 [] []

'''

def draw_game_array(game_array):
    for row in range(4):
        for col in range(4):
            if game_array[row][col] is None:
                sys.stdout.write("[ ]" + "\t")
            else:
                sys.stdout.write(str(game_array[row][col]) + "\t")
        print()

def get_open_idx(game_array):
    idx_list = []
    for row in range(4):
        for col in range(4):
            if game_array[row][col] is None:
                idx_list.append((row, col))
    
    open_idx_cnt = len(idx_list)
    if open_idx_cnt == 0:
        return (None, None)
    else:
        idx = random.randint(0, open_idx_cnt - 1)
        return idx_list[idx]


def shift_array_sub(array):
    if not None in array:
        print(f"No empty slots in row")
        return array
    if all(i == None for i in array):
        print(f"Row empty")
        return array

    i = 0
    while 1:
        sub_array = array[i:]
        
        if (len(sub_array) == 0):
            break
        if all(i == None for i in sub_array):
            break
        if (array[i] is not None):
            i += 1
            if (i >= 4):
                break
            continue

        # Shift row to left
        #print(f"i = {i}, Subrow = {sub_array}, subrow[1:] = {sub_array[1:]}")
        array = array[0:i] + sub_array[1:] + [None]
    return array
    
def shift_array(array, flip=False):
    if flip:
        array.reverse()
    array = shift_array_sub(array)
    if flip:
        array.reverse()
    return array

def shift_board(game_array, dir):
    if (dir == SHIFT_DIR_LEFT):
        for row in range(4):
            array = list(game_array[row])
            array = shift_array(array)
            game_array[row] = array
    elif (dir == SHIFT_DIR_RIGHT):
        for row in range(4):
            array = list(game_array[row])
            array = shift_array(array, flip=True)
            game_array[row] = array
    elif (dir == SHIFT_DIR_UP):
        for col in range(4):
            array = []
            for row in range(4):
                array.append(game_array[row][col])
            array = shift_array(array)
            for row in range(4):
                game_array[row][col] = array[row]
    elif (dir == SHIFT_DIR_DOWN):
        for col in range(4):
            array = []
            for row in range(4):
                array.append(game_array[row][col])
            array = shift_array(array, flip=True)
            for row in range(4):
                game_array[row][col] = array[row]

def merge_array_sub(array):
    score = 0
    for i in range(3):
        if (array[i] is not None) and (array[i] == array[i+1]):
            value = array[i] * 2
            array[i] = value
            array[i+1] = None
            score += value
    return array, score

def merge_array(array, flip=False):
    if flip:
        array.reverse()
    array, score = merge_array_sub(array)
    if flip:
        array.reverse()
    return array, score

def merge_board(game_array, dir):
    score_total = 0
    if (dir == SHIFT_DIR_LEFT):
        for row in range(4):
            array = list(game_array[row])
            array, score = merge_array(array)
            score_total += score
            game_array[row] = array
    elif (dir == SHIFT_DIR_RIGHT):
        for row in range(4):
            array = list(game_array[row])
            array, score = merge_array(array, flip=True)
            score_total += score
            game_array[row] = array
    elif (dir == SHIFT_DIR_UP):
        for col in range(4):
            array = []
            for row in range(4):
                array.append(game_array[row][col])
            array, score = merge_array(array)
            score_total += score
            for row in range(4):
                game_array[row][col] = array[row]
    elif (dir == SHIFT_DIR_DOWN):
        for col in range(4):
            array = []
            for row in range(4):
                array.append(game_array[row][col])
            array, score = merge_array(array, flip=True)
            score_total += score
            for row in range(4):
                game_array[row][col] = array[row]
    print("Score Change:", score_total)
    return score_total

def compare_game_array(curr, prev):
    for row in range(4):
        for col in range(4):
            if (curr[row][col] != prev[row][col]):
                return False
    return True

def reset_board():
    game_array_start = [[None, None, None, None], [None, None, None, None], [None, None, None, None], [None, None, None, None]]   
    return copy.deepcopy(game_array_start)

if __name__ == "__main__":
    pygame.init()

    # Pygame now allows natively to enable key repeat:
    # pygame.key.set_repeat(200, 25)

    # Setup display window and clock
    size = width, height = 600, 480
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    # No arguments needed to get started
    #textinput = pygame_textinput.TextInputVisualizer()

    # But more customization possible: Pass your own font object
    #font = pygame.font.SysFont("Consolas", 24)


    #FONT = pygame.font.Font(None, 24)
    #user_prompt = font.render("Input:", True, pygame.Color("black"))

    # Background objects

    score = 0
    game_array_start = [[None, None, None, None], [None, None, None, None], [None, None, None, None], [None, None, None, None]]
    game_array = copy.deepcopy(game_array_start)

    for i in range(2):
        row, col = get_open_idx(game_array)
        if row is None:
            print("Could not find open idx")
            break
        game_array[row][col] = 2
        print((row, col))

    draw_game_array(game_array)

    block_input = False
    score = 0
    cnt = 0
    while True:
        # Draw background
        screen.fill((225, 225, 225))
        
        # Process Events
        events = pygame.event.get()        
        # Check if user is exiting or pressed return
        board_shifted = False
        debug = False
        prev_game_array = copy.deepcopy(game_array)
        for event in events:
            if event.type == pygame.QUIT:
                exit()

            if not block_input:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    print(f"User pressed UP!")
                    shift_board(game_array, SHIFT_DIR_UP)
                    score += merge_board(game_array, SHIFT_DIR_UP)
                    shift_board(game_array, SHIFT_DIR_UP)
                    draw_game_array(game_array)
                    board_shifted = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    print(f"User pressed RIGHT!")
                    shift_board(game_array, SHIFT_DIR_RIGHT)
                    score += merge_board(game_array, SHIFT_DIR_RIGHT)
                    shift_board(game_array, SHIFT_DIR_RIGHT)
                    draw_game_array(game_array)
                    board_shifted = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    print(f"User pressed DOWN!")
                    shift_board(game_array, SHIFT_DIR_DOWN)
                    score += merge_board(game_array, SHIFT_DIR_DOWN)
                    shift_board(game_array, SHIFT_DIR_DOWN)
                    draw_game_array(game_array)
                    board_shifted = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    cnt += 1
                    print(f"User pressed LEFT!", cnt)
                    shift_board(game_array, SHIFT_DIR_LEFT)
                    score += merge_board(game_array, SHIFT_DIR_LEFT)
                    shift_board(game_array, SHIFT_DIR_LEFT)
                    draw_game_array(game_array)
                    board_shifted = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    debug = True
                
                

        if board_shifted or debug:
            if (compare_game_array(game_array, prev_game_array) == False):
                row, col = get_open_idx(game_array)
                if row is None:
                    print("Could not find open idx")
                    print("Game Over!")
                    score = 0
                    game_array = reset_board()

                    for i in range(2):
                        row, col = get_open_idx(game_array)
                        if row is None:
                            print("Error: Could not find open idx")
                            break
                        game_array[row][col] = 2
                        print((row, col))
                    print(f"Score = {score}")
                    draw_game_array(game_array)
                else:
                    print((row, col))
                    game_array[row][col] = 2
                    print(f"Score = {score}")
                    draw_game_array(game_array)
            


        pygame.display.update()
            
        clock.tick(30)