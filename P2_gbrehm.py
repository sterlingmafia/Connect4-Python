
import numpy as np
import pygame
import sys
import math
import random
import time

# DONE: On win, show the name of the winner
# DONE: On win, show how long (in time) the game lasted
# DONE: Display number of moves (player 1 + player 2) performed in the game
# DONE: Show a palette with 16 shades of yellow to pick from for the color of the board
# TODO: Make it so that the player can enter their name
# DONE: Make it so that who plays first can be selected by the human
# DONE: Make it so that the human can select the bot difficulty
# DONE: Implement the cat's game terminal state properly - right now if it's found in the minimax there's a termination, but it should be reached on the actual board.


BLUE = (55, 129, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW1 = (255, 255, 0)
LIGHTGREY = (175, 175, 175)
GRAY = (200, 200, 200)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY_SPACE = 0

board_color = BLUE
board_lookup = 1
text_box_active = False
player_name = ""
starting_player = PLAYER
game_difficulty = 1

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
myfont_large = pygame.font.SysFont("monospace", 75)
myfont_mid = pygame.font.SysFont("monospace", 45)

def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def is_square(board, r, c, piece):
    if  board[r][c] == piece and board[r + 1][c] == piece and board[r][c + 1] == piece and board[r + 1][c + 1] == piece:
        return True
    return False

def winning_move(board, piece):
    for r in range(ROW_COUNT-1):
        for c in range(COLUMN_COUNT-1):
            if is_square(board, r, c, piece):
                return True
    return False

def is_cat_game(board):
    return len(get_valid_locations(board)) == 0

def check_good_subarray(board, r, c, piece, length):
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    for i in range(length):
        if board[r][c + i] == opp_piece:
            return False
    return True

def score_position(board, piece):            
    score = 0

    ## Penalize play on the edge
    outside_left = [int(i) for i in list(board[:, 0])]
    outside_right = [int(i) for i in list(board[:, COLUMN_COUNT-1])]
    left_count = outside_left.count(piece)
    right_count = outside_right.count(piece)
    score -= 2*(left_count + right_count)

    ## Check for winning board; make sure this has best score if true
    # Not necessary as this is already checked at a higher level
    # if winning_move(board, piece):
    #     return 10000
    
    ## check for a victory line: does this give us a line of 3 with 3 empty spaces above? are we putting a piece in the center of a victory line?
    # for r in range(ROW_COUNT):
    #     row_array = [int(i) for i in list(board[r,:])]
    #     for c in range(COLUMN_COUNT-2):
    #         window = row_array[c:c+3]
    #         score += evaluate_window(window, piece)

    ## Examine squares of 4 for empty spaces, and prioritize those with more of our pieces IF there are no opposing pieces in the square
    for c in range(COLUMN_COUNT-1):
        for r in range(ROW_COUNT-1):
            if check_good_subarray(board, r, c, piece, 2):
                    if check_good_subarray(board, r+1, c, piece, 2):
                        upper_count = 0
                        lower_count = 0
                        for i in range(2):
                            if board[r][c + i] == piece:
                                lower_count += 1
                        for i in range(2):
                            if board[r+1][c + i] == piece:
                                upper_count += 1
                        score += (7^lower_count + 3*(upper_count+lower_count))  
    return score

def is_terminal_node(board):
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or is_cat_game(board)

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
                valid_locations.append(col)
    return valid_locations

def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)

    best_col = random.choice(valid_locations)
    best_score = 0

    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        print(col)
        print(score)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col

      

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, board_color, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, LIGHTGREY, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, WHITE, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

def play_game(player_name, starting_player, difficulty):

    game_over = False
    
    board = create_board()
    #print_board(board)
    draw_board(board)
    pygame.display.update()

    turn_number = 1
    turn = starting_player
    print(turn)

    start_time = time.time()
    while not game_over:

        if is_cat_game(board):
            label = myfont_large.render("Cat's Game!", 1, RED)
            screen.blit(label, (40,10))
            print("--- %s seconds ---" % (time.time() - start_time))
            print("turn # " + str(turn_number - 1))
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, LIGHTGREY, (0,0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen, BLACK, (posx, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, LIGHTGREY, (0,0, width, SQUARESIZE))
                #print(event.pos)
                # Ask for Player 1 Input
                if turn == PLAYER:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)

                        if winning_move(board, PLAYER_PIECE):
                            label = myfont_large.render(player_name + " wins!!", 1, RED)
                            screen.blit(label, (40,10))
                            print("--- %s seconds ---" % (time.time() - start_time))
                            print("turn # " + str(turn_number))
                            game_over = True

                        turn_number += 1
                        turn += 1
                        turn = turn % 2

                        #print_board(board)
                        draw_board(board)
                            
        # # AI turn
        if turn == AI and not game_over:	

            col, minimax_score = minimax(board, difficulty, -math.inf, math.inf, True)

            if is_valid_location(board, col):
                #pygame.time.wait(500)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = myfont_large.render("The AI wins!!", 1, YELLOW1)
                    screen.blit(label, (40,10))
                    print("--- %s seconds ---" % (time.time() - start_time))
                    print("turn # " + str(turn_number))
                    game_over = True

                print_board(board)
                draw_board(board)

                turn_number += 1
                turn += 1
                turn = turn % 2			
            
            # col = pick_best_move(board, AI_PIECE)

            # if is_valid_location(board, col):
            #     pygame.time.wait(500)
            #     row = get_next_open_row(board, col)
            #     drop_piece(board, row, col, AI_PIECE)

            #     if winning_move(board, AI_PIECE):
            #         label = myfont.render("Player 2 wins!!", 1, YELLOW)
            #         screen.blit(label, (40,10))
            #         game_over = True

            #     #print_board(board)
            #     draw_board(board)

            #     turn += 1
            #     turn = turn % 2

        if game_over:
            pygame.time.wait(3000)

def get_board_color(lookup_val):
    match lookup_val:
        case 1:
            return (230, 219, 172)
        case 2:
            return (238, 220, 154)
        case 3:
            return (249, 224, 118)
        case 4:
            return (201, 187, 142)
        case 5:
            return (214, 184, 90)
        case 6:
            return (223, 201, 138)
        case 7:
            return (250, 226, 156)
        case 8:
            return (200, 169, 81)
        case 9:
            return (243, 234, 175)
        case 10:
            return (216, 184, 99)
        case 11:
            return (227, 183, 120)
        case 12:
            return (231, 194, 125)
        case 13:
            return (220, 215, 160)
        case 14:
            return (227, 197, 101)
        case 15:
            return (237, 232, 186)
        case 16:
            return (251, 231, 144)
         
def draw_menu(board_color, player_name):
    global starting_player
    global text_box_active
    global game_difficulty

    screen.fill(WHITE)

    option_spacing = 40  # Vertical spacing between options

    # Option 1: Board color
    board_color_text = myfont_mid.render("Board Color", True, BLACK)
    screen.blit(board_color_text, (50, 50))
    pygame.draw.rect(screen, board_color, (50, 60 + option_spacing, 50, 50))

    # Option 2: Player name
    player_name_text = myfont_mid.render("Player Name: ", True, BLACK)
    screen.blit(player_name_text, (50, 150))
    text_box_rect = pygame.Rect(50, 160 + option_spacing, 300, 40)
    pygame.draw.rect(screen, LIGHTGREY if text_box_active else GRAY, text_box_rect)

    text_surface = myfont_mid.render(player_name, True, BLACK)
    # render at position stated in arguments
    screen.blit(text_surface, (text_box_rect.x, text_box_rect.y))
      
    # set width of textfield so that text cannot get
    # outside of user's text input
    text_box_rect.w = max(100, text_surface.get_width()+10)

    # Option 3: Starting player
    starting_player_text = myfont_mid.render("Starting Player: " + ("Human" if starting_player == PLAYER else "AI"), True, BLACK)
    screen.blit(starting_player_text, (50, 250))
    pygame.draw.rect(screen, BLACK, (50, 300, 50, 50))

    # Option 4: Difficulty
    difficulty_text = myfont_mid.render("Difficulty: " + str(game_difficulty), True, BLACK)
    screen.blit(difficulty_text, (50, 350))
    pygame.draw.rect(screen, BLACK, (50, 400, 50, 50))

    # Start game button
    pygame.draw.rect(screen, BLUE, (50, 550, 315, 75))
    start_button_text = myfont_mid.render("Start Game", True, WHITE)
    screen.blit(start_button_text, (75, 563))

    pygame.display.update()

def handle_menu_events():
    global board_lookup
    global board_color
    global text_box_active
    global player_name
    global starting_player
    global game_difficulty

    text_box_rect = pygame.Rect(50, 200, 300, 40)

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if the user clicked on the board color option
                if 50 <= mouse_x <= 100 and 110 <= mouse_y <= 160:
                    if board_lookup == 16:
                        board_lookup = 1
                    else:
                        board_lookup += 1
                    
                    board_color = get_board_color(board_lookup)

                # check if user is changing starting player
                if 50 <= mouse_x <= 100 and 300 <= mouse_y <= 350:
                    if starting_player == PLAYER:
                        starting_player = AI
                    else:
                        starting_player = PLAYER

                # Check if user is trying to enter name
                if text_box_rect.collidepoint(mouse_x, mouse_y):
                    text_box_active = True
                else:
                    text_box_active = False

                # Check if user is trying to change difficulty
                if 50 <= mouse_x <= 100 and 400 <= mouse_y <= 450:
                    if game_difficulty < 5:
                        game_difficulty += 1
                    else:
                        game_difficulty = 1
                        
                        
                
                # Check if user wants to start game
                if 50 <= mouse_x <= 365 and 550 <= mouse_y <= 625:
                    difficulty = game_difficulty
                    play_game(player_name, starting_player, difficulty)

            if event.type == pygame.KEYDOWN and text_box_active:
                if event.key == pygame.K_BACKSPACE:

                    # get text input from 0 to -1 i.e. end.
                    player_name = player_name[:-1]

                # Unicode standard is used for string
                # formation
                else:
                    player_name += event.unicode

def menu():

    global board_lookup
    global board_color

    board_color = get_board_color(board_lookup)  # Default board color


    pygame.display.set_caption("Game Menu")

    while True:
        handle_menu_events()
        draw_menu(board_color, player_name)
    
menu()