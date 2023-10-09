import pygame
import pygame_gui
from tetrisObjects import getGameObject, colours, sizes
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

width = 800
height = 600

pygame.init()

def pauseGame(display, gui_manager, score):
    # create pause screen visuals
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
                if event.ui_element == continue_button: # go back to game screen
                    for element in gui_elements:
                        element.hide()
                    pause_screen_active = False
                    return False
                if event.ui_element == quit_button: # quit to main menu
                    for element in gui_elements:
                        element.hide()
                    pause_screen_active = False
                    return True
                
            if event.type == pygame.QUIT: # quit to main menu by X button
                for element in gui_elements:
                    element.hide()
                pause_screen_active = False
                return True
            gui_manager.process_events(event)

        # display graphics
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
    game = getGameObject(new_width, new_height, is_extension, fps)
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
                        if pauseGame(display, gui_manager, game.score) == True: # user requested to end game
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
            if target_position == -1: # move-finding phase
                down_fast = False
                best_fitness = -1000000
                best_index = -1
                best_rotation = -1
                holding = False

                # find the best move among all rotations and positions of current and held blocks
                for i in range(game.board_width):
                    for new_rotation in range(len(sizes[game.block_Index])): # test all rotation for current block
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
                    for new_rotation in range(len(sizes[held_ID])): # test all rotations for held block (or next block if no held is found)
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
                if holding: # hold block if needed
                    game.holdBlock()
            else: # execution phase
                if game.block_position[0] < target_position: # move right
                    left = False
                    right = True
                elif game.block_position[0] > target_position: # move left
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

def fitnessRating(game, new_shape, i): # fitness algorithm
    # find lowest place to put the new shape
    highest_position = 0
    while not game.outOfBounds(new_shape, [i, highest_position + 1]):
        highest_position += 1
    # apply the move to a temp board
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
