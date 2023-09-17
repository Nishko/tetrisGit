import pygame
import random
import pygame_gui
from copy import copy, deepcopy

"""
Block ID's Guide:
0: Square
1: Line
2: T Shape
3: L Shape
4: Backwards L Shape
5: Zig Zag Pointing Right
6: Zig Zag Pointing Left
7: Short Line
8: Corner Shape
"""

# the colours of the blocks
colours = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255),
           (0,255,255), (128,0,128), (128,128,0), (128,0,128)]
# all the rotations of each block on a cartesian plane
sizes = [
    [[(0,0),(1,0),(1,1),(0,1)]],  # square
    [[(-1,1),(0,1),(1,1),(2,1)],[(0,0),(0,1),(0,2),(0,3)]],  # line
    [[(0,0),(0,1),(-1,1),(1,1)],[(0,0),(0,1),(0,2),(1,1)],
     [(-1,1),(0,1),(1,1),(0,2)],[(0,0),(0,1),(0,2),(-1,1)]],  # T shape
    [[(0,0),(0,1),(0,2),(1,2)],[(0,1),(-1,1),(1,1),(-1,2)],
     [(0,0),(-1,0),(0,1),(0,2)],[(0,1),(-1,1),(1,1),(1,0)]],  # L shape
    [[(0,0),(0,1),(0,2),(-1,2)],[(-1,0),(-1,1),(0,1),(1,1)],
     [(0,0),(1,0),(0,1),(0,2)],[(0,1),(-1,1),(1,1),(1,2)]],  # backwards L shape
    [[(0,0),(1,0),(-1,1),(0,1)],[(0,0),(0,1),(1,1),(1,2)]],  # zig zag right
    [[(0,0),(-1,0),(0,1),(1,1)],[(0,0),(0,1),(-1,1),(-1,2)]],  # zig zag left
    [[(-1,1),(0,1),(1,1)],[(0,0),(0,1),(0,2)]],  # short line
    [[(0,0),(0,1),(1,1)],[(0,0),(0,1),(-1,1)],
     [(0,1),(0,2),(-1,1)],[(0,1),(0,2),(1,1)]]  # corner shape
]
row_values = [0,100,300,600,1000]
width = 800
height = 600
pygame.init()


class GameClass:
    # the block ID's
    block_Index = 0
    next_block = 0
    held_block = -1

    block_rotation = 0  # rotation of current block
    block_position = [0,0]  # position of current block
    board = []  # array of the board
    cleared_rows = []
    board_width = 10
    board_height = 20
    score = 0
    lines_cleared = 0
    speed = 1.0
    fps = 0
    extension = False
    can_swap_block = True

    def __init__(self, new_width, new_height, is_extension, new_fps):
        # assign needed variables
        self.board_width, self.board_height = new_width, new_height
        self.extension = is_extension
        self.block_position[0] = new_width//2
        self.fps = new_fps
        self.board.clear()  # wipe the board

        # set random blocks for the current and next block
        self.block_Index = self.randomBlock()
        self.next_block = self.randomBlock()

        # fill the board with empty spaces (-1)
        for i in range(self.board_width):
            new_row = []
            for j in range(self.board_height):
                new_row.append(-1)
            self.board.append(new_row)
        for i in range(self.board_height):
            self.cleared_rows.append(-1)

    def checkForRows(self, board, add_score):  # check each row if it's completed and if so remove it
        rows_removed = 0
        for j in range(self.board_height):
            full = True
            for i in range(self.board_width):
                if board[i][j] == -1:
                    full = False
                    break

            if full:  # remove row if it's completed
                if add_score:
                    self.cleared_rows[j] = self.fps / 3
                    self.lines_cleared += 1
                rows_removed += 1
                for v in range(j,0,-1):
                    for u in range(self.board_width):
                        board[u][v] = board[u][v-1]
        if add_score:
            self.score += row_values[rows_removed]
            if self.speed < 5:
                self.speed += rows_removed / 50.0
        else:
            return rows_removed

    def outOfBounds(self, shape, pos):  # check if a given shape and position is an invalid space
        for i in range(len(shape)):
            x,y = pos[0] + shape[i][0], pos[1] + shape[i][1]
            if x < 0 or y < 0 or x >= self.board_width or y >= self.board_height:  # A space is out of bounds
                return True
            elif self.board[x][y] != -1:  # A space intersects with an already filled spot on the board
                return True
        return False

    def rotate(self):  # rotate the current block
        new_rotation = (self.block_rotation + 1) % len(sizes[self.block_Index])
        new_position = self.block_position.copy()
        # try just rotating
        if not self.outOfBounds(sizes[self.block_Index][new_rotation], new_position):
            self.block_position = new_position
            self.block_rotation = new_rotation
            return
        # try shifting left once and rotating
        new_position[0] -= 1
        if not self.outOfBounds(sizes[self.block_Index][new_rotation], new_position):
            self.block_position = new_position
            self.block_rotation = new_rotation
            return
        # try shifting left twice and rotating if it's a line piece
        new_position[0] -= 1
        if (not self.outOfBounds(sizes[self.block_Index][new_rotation], new_position)) and self.block_Index == 1:
            self.block_position = new_position
            self.block_rotation = new_rotation
            return
        # try shifting right and rotating
        new_position[0] += 3
        if not self.outOfBounds(sizes[self.block_Index][new_rotation], new_position):
            self.block_position = new_position
            self.block_rotation = new_rotation
            return

    def moveHorizontal(self, direction):  # try shift the block horizontally by the given value
        new_position = [self.block_position[0] + direction, self.block_position[1]]
        if not self.outOfBounds(sizes[self.block_Index][self.block_rotation], new_position):
            self.block_position = new_position

    def moveDown(self):  # try moving down otherwise place the block in its current position
        new_position = [self.block_position[0], self.block_position[1] + 1]
        if not self.outOfBounds(sizes[self.block_Index][self.block_rotation], new_position):
            self.block_position = new_position
        else:  # place the block
            # update board
            pos = self.block_position
            shape = sizes[self.block_Index][self.block_rotation]
            for i in range(len(shape)):
                x, y = pos[0] + shape[i][0], pos[1] + shape[i][1]
                self.board[x][y] = self.block_Index

            # update the board and create a new block
            self.checkForRows(self.board, True)
            self.block_position = [self.board_width//2,0]
            self.block_rotation = 0
            self.can_swap_block = True
            self.block_Index = self.next_block
            self.next_block = self.randomBlock()

            # the new block is also invalid so the game is over
            if self.outOfBounds(sizes[self.block_Index][self.block_rotation], self.block_position):
                return [False, 1]
            else:
                return [True, 1]

        return [True, 0]

    def randomBlock(self):  # generate a random block ID depending on if the extension is active or not
        if not self.extension:
            return random.randint(0, 6)
        else:
            return random.randint(0, 8)

    def holdBlock(self):  # hold the current block
        if self.held_block == -1:
            self.can_swap_block = False
            self.block_position = [self.board_width // 2, 0]
            self.block_rotation = 0

            self.held_block = self.block_Index
            self.block_Index = self.next_block
            self.next_block = self.randomBlock()
        else:
            if self.can_swap_block:
                self.can_swap_block = False
                self.block_position = [self.board_width // 2, 0]
                self.block_rotation = 0

                temp = self.held_block
                self.held_block = self.block_Index
                self.block_Index = temp

def pauseGame(display, gui_manager, score):
    gui_elements = []
    continue_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((150, 400), (200, 50)), 
            text="Continue", manager=gui_manager)
    gui_elements.append(continue_button)
    quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((450, 400), (200, 50)), 
            text="Quit", manager=gui_manager)
    gui_elements.append(quit_button)
    pause_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((0, 100), (800, 100)), 
            html_text=f"<font size={7}>{'Game Paused'}</font>", manager=gui_manager)
    gui_elements.append(pause_text)
    score_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((0, 200), (800, 100)), 
            html_text=f"<font size={5}>{'Current Score: ' + str(score)}</font>", manager=gui_manager)
    gui_elements.append(score_text)

    for element in gui_elements:
        element.visible = False
    clock = pygame.time.Clock()

    pause_screen_active = True
    while pause_screen_active:
        for event in pygame.event.get():
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == continue_button:
                    for element in gui_elements:
                        element.hide()
                    pause_screen_active = False
                    return False
                if event.ui_element == quit_button:
                    for element in gui_elements:
                        element.hide()
                    pause_screen_active = False
                    return True
                
            if event.type == pygame.QUIT:
                for element in gui_elements:
                    element.hide()
                pause_screen_active = False
                return True
            gui_manager.process_events(event)

        gui_manager.update(clock.tick(60) / 1000.0)
        display.fill((0, 0, 0))
        gui_manager.draw_ui(display)
        for element in gui_elements:
            element.show()
        pygame.display.flip()

def startGame(new_width, new_height, is_extension, new_level, AI_mode, display, gui_manager, game_music, font_path):  # called at the start of the game
    clock = pygame.time.Clock()
    playing = True
    fps = 25
    pos = [250,175]
    game = GameClass(new_width, new_height, is_extension, fps)
    game.__init__(new_width, new_height, is_extension, fps)  # restart game

    level = new_level
    block_width = 20  # pixel width of each block
    down_fast, left, right = False, False, False  # movement bools so you can hold down to move
    movement_cooldown = 0
    counter = 0

    # calculate game board position
    pos[0] = (width - new_width * block_width) / 2
    pos[1] = (height - new_height * block_width) / 4 * 3

    # Ai values
    AI_playing = AI_mode
    target_position = -1
    target_rotation = 0

    # Play Music
    pygame.mixer.music.load(game_music)
    pygame.mixer.music.play(-1)
    mute_music = False

    # Font Colour
    colour = pygame.Color("#ED9008")

    while playing:
        display.fill((0, 0, 0))  # set screen background

        # increase the tick timers
        counter += 1
        movement_cooldown += 1

        # move block down
        if counter > (fps//(level * game.speed)) or (down_fast and counter > (fps//(level * game.speed))/10):
            return_Value = game.moveDown()
            if not return_Value[0]:  # game is over
                playing = False
                pygame.mixer.music.stop()
                return game.score
            if return_Value[1] == 1:
                target_position = -1
            counter = 0

        # move block sideways
        if left and movement_cooldown > fps/10:
            game.moveHorizontal(-1)
            movement_cooldown = 0
        if right and movement_cooldown > fps/10:
            game.moveHorizontal(1)
            movement_cooldown = 0

        # get inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # quit game
                playing = False
            if event.type == pygame.KEYDOWN:  # pause game
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        if pauseGame(display, gui_manager, game.score) == True:
                            pygame.mixer.music.stop()
                            return game.score
            if not AI_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game.rotate()
                    if event.key == pygame.K_DOWN:
                        down_fast = True
                    if event.key == pygame.K_LEFT:
                        left = True
                    if event.key == pygame.K_RIGHT:
                        right = True
                    if event.key == pygame.K_SPACE:
                        game.holdBlock()
                    if event.key == pygame.K_m:
                        mute_music = not mute_music
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        down_fast = False
                    if event.key == pygame.K_LEFT:
                        left = False
                    if event.key == pygame.K_RIGHT:
                        right = False
        if AI_playing:  # AI logic
            if target_position == -1:
                down_fast = False
                best_fitness = -1000000
                best_index = -1
                best_rotation = -1
                holding = False

                for i in range(game.board_width):
                    for new_rotation in range(len(sizes[game.block_Index])):
                        new_shape = sizes[game.block_Index][new_rotation]
                        if game.outOfBounds(new_shape, [i,0]):
                            continue

                        new_fitness = fitnessRating(game, new_shape, i)

                        if new_fitness > best_fitness:
                            best_fitness = new_fitness
                            best_index = i
                            best_rotation = new_rotation
                            holding = False
                    held_ID = game.next_block
                    if game.held_block != -1:
                        held_ID = game.held_block
                    for new_rotation in range(len(sizes[held_ID])):
                        new_shape = sizes[held_ID][new_rotation]
                        if game.outOfBounds(new_shape, [i, 0]):
                            continue

                        new_fitness = fitnessRating(game, new_shape, i)

                        if new_fitness > best_fitness:
                            best_fitness = new_fitness
                            best_index = i
                            best_rotation = new_rotation
                            holding = True

                target_position = best_index
                target_rotation = best_rotation
                if holding:
                    game.holdBlock()
            else:
                if game.block_position[0] < target_position:
                    left = False
                    right = True
                elif game.block_position[0] > target_position:
                    left = True
                    right = False
                else:
                    left = False
                    right = False
                if game.block_rotation != target_rotation:
                    game.rotate()
                elif game.block_position[0] == target_position:
                    down_fast = True

        # Render Grid
        for i in range(game.board_width):
            for j in range(game.board_height):
                # draw Grid
                pygame.draw.rect(display, "#222E25", [i*block_width + pos[0], j*block_width + pos[1],
                                                     block_width, block_width], 1)
                
                # draw A square if there is one
                if game.cleared_rows[j] >= 0 and game.board[i][j] != -1:
                    W = 1 - game.cleared_rows[j]/fps
                    OC = colours[game.board[i][j]]
                    newColour = (255-(255 - OC[0]) * W, 255-(255 - OC[1]) * W, 255-(255 - OC[2]) * W)
                    pygame.draw.rect(display, newColour, 
                                    [i * block_width + pos[0] + 1, j * block_width + pos[1] + 1, block_width - 2, block_width - 2])
                elif game.cleared_rows[j] >= 0 and game.board[i][j] == -1:
                    W = game.cleared_rows[j]/fps
                    pygame.draw.rect(display, (255 * W, 255 * W, 255 * W), 
                                    [i * block_width + pos[0] + 1, j * block_width + pos[1] + 1, block_width - 2, block_width - 2])
                elif game.board[i][j] != -1:
                    pygame.draw.rect(display, colours[game.board[i][j]], [i * block_width + pos[0] + 1,
                                                                        j * block_width + pos[1] + 1,
                                                                        block_width - 2, block_width - 2])

        #process animation
        for i in range(len(game.cleared_rows)):
            if game.cleared_rows[i] >= 0:
                game.cleared_rows[i] -= 1

        # Render Block
        for i in range(len(sizes[game.block_Index][0])):
            block_cords = sizes[game.block_Index][game.block_rotation][i]
            block_colour = colours[game.block_Index]
            block_position = game.block_position
            pygame.draw.rect(display, block_colour, [(block_cords[0] + block_position[0]) * block_width + pos[0] + 1,
                                                   (block_cords[1] + block_position[1]) * block_width + pos[1] + 1,
                                                   block_width-2, block_width-2])

        # Render Next Block
        NBX_pos = pos[0] + block_width * new_width + 50
        NB_font = pygame.font.Font(font_path, 30)
        NB_label = NB_font.render("Next Block", 1, colour)
        display.blit(NB_label, (NBX_pos,200))
        NB_x, NB_y = NBX_pos + 50, 250
        for i in range(len(sizes[game.next_block][0])):
            block_cords = sizes[game.next_block][0][i]
            block_colour = colours[game.next_block]
            # draw outline
            pygame.draw.rect(display, "#121E15", [block_cords[0] * block_width + NB_x,
                                                 block_cords[1] * block_width + NB_y,
                                                 block_width, block_width], 1)
            # draw colour
            pygame.draw.rect(display, block_colour, [block_cords[0] * block_width + NB_x + 1,
                                                   block_cords[1] * block_width + NB_y + 1,
                                                   block_width-2, block_width-2])

        # Render Held Block
        HBX_pos = pos[0] - 215
        HB_font = pygame.font.Font(font_path, 30)
        HB_label = HB_font.render("Held Block", 1, colour)
        display.blit(HB_label, (HBX_pos, 200))
        HB_x, HB_y = HBX_pos + 50, 250
        if game.held_block != -1:
            for i in range(len(sizes[game.held_block][0])):
                block_cords = sizes[game.held_block][0][i]
                block_colour = colours[game.held_block]
                # draw outline
                pygame.draw.rect(display, "#121E15", [block_cords[0] * block_width + HB_x,
                                                     block_cords[1] * block_width + HB_y,
                                                     block_width, block_width], 1)
                # draw colour
                pygame.draw.rect(display, block_colour, [block_cords[0] * block_width + HB_x + 1,
                                                       block_cords[1] * block_width + HB_y + 1,
                                                       block_width - 2, block_width - 2])

        # Render Corner Text
        CT_font = pygame.font.Font(font_path, 15)
        CT_label = CT_font.render("Group 50", 1, colour)
        display.blit(CT_label, (width - CT_label.get_size()[0], 0))
        CT_label = CT_font.render("Score: " + str(game.score), 1, colour)
        display.blit(CT_label, (0, 0))
        CT_label = CT_font.render("Lines Cleared: " + str(game.lines_cleared), 1, colour)
        display.blit(CT_label, (0, 15))
        CT_label = CT_font.render("Speed: " + str(round(game.speed * level,2)), 1, colour)
        display.blit(CT_label, (0, 30))
        if AI_playing:
            CT_label = CT_font.render("Play mode: AI", 1, colour)
            display.blit(CT_label, (0, 45))
        else:
            CT_label = CT_font.render("Play mode: Human", 1, colour)
            display.blit(CT_label, (0, 45))
        if is_extension:
            CT_label = CT_font.render("Game mode: Extension", 1, colour)
            display.blit(CT_label, (0, 60))
        else:
            CT_label = CT_font.render("Game mode: Normal", 1, colour)
            display.blit(CT_label, (0, 60))

        # Mute music
        if mute_music:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(1)
        
        clock.tick(fps)
        pygame.display.flip()
    pygame.mixer.music.stop()

def fitnessRating(game, new_shape, i):
    highest_position = 0
    while not game.outOfBounds(new_shape, [i, highest_position + 1]):
        highest_position += 1
    # temp apply changes
    temp_board = deepcopy(game.board)
    for u in range(len(new_shape)):
        temp_board[i + new_shape[u][0]][highest_position + new_shape[u][1]] = 1
    cleared = game.checkForRows(temp_board, False)
    # calculate fitness
    new_fitness = 0
    lowest_block = game.board_height
    for u in range(game.board_width):
        height_added = False
        for v in range(game.board_height):
            if not height_added:
                if temp_board[u][v] != -1 or v == game.board_height - 1:
                    new_fitness += v
                    height_added = True
                    if v < lowest_block:
                        lowest_block = v
            else:
                if temp_board[u][v] == -1 and temp_board[u][v - 1] != -1:
                    new_fitness -= 5
    new_fitness += lowest_block * 2.5
    return new_fitness
