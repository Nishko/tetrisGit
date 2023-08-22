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
Colours = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255),
           (0,255,255), (128,0,128), (128,128,0), (128,0,128)]
# all the rotations of each block on a cartesian plane
Sizes = [
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
RowValues = [0,100,300,600,1000]
width = 800
height = 600
pygame.init()


class GameClass:
    # the block ID's
    BlockInd = 0
    NextBlock = 0
    HeldBlock = -1

    BlockRot = 0  # rotation of current block
    BlockPos = [0,0]  # position of current block
    Board = []  # array of the board
    ClearedRows = []
    BoardWidth = 10
    BoardHeight = 20
    Score = 0
    Speed = 1
    fps = 0
    Extension = False
    CanSwapBlock = True

    def __init__(self, newWidth, newHeight, isExtension, newFps):
        # assign needed variables
        self.BoardWidth, self.BoardHeight = newWidth, newHeight
        self.Extension = isExtension
        self.BlockPos[0] = newWidth//2
        self.fps = newFps
        self.Board.clear()  # wipe the board

        # set random blocks for the current and next block
        self.BlockInd = self.RandomBlock()
        self.NextBlock = self.RandomBlock()

        # fill the board with empty spaces (-1)
        for i in range(self.BoardWidth):
            newRow = []
            for j in range(self.BoardHeight):
                newRow.append(-1)
            self.Board.append(newRow)
        for i in range(self.BoardHeight):
            self.ClearedRows.append(-1)

    def CheckForRows(self, board, addScore):  # check each row if it's completed and if so remove it
        rowsRemoved = 0
        for j in range(self.BoardHeight):
            full = True
            for i in range(self.BoardWidth):
                if board[i][j] == -1:
                    full = False
                    break

            if full:  # remove row if it's completed
                if addScore:
                    self.ClearedRows[j] = self.fps / 3
                rowsRemoved += 1
                for v in range(j,0,-1):
                    for u in range(self.BoardWidth):
                        board[u][v] = board[u][v-1]
        if addScore:
            self.Score += RowValues[rowsRemoved]
            if self.Speed < 5:
                self.Speed += rowsRemoved / 20.0

    def OutOfBounds(self, Shape, Pos):  # check if a given shape and position is an invalid space
        for i in range(len(Shape)):
            x,y = Pos[0] + Shape[i][0], Pos[1] + Shape[i][1]
            if x < 0 or y < 0 or x >= self.BoardWidth or y >= self.BoardHeight:  # A space is out of bounds
                return True
            elif self.Board[x][y] != -1:  # A space intersects with an already filled spot on the board
                return True
        return False

    def Rotate(self):  # rotate the current block
        newRot = (self.BlockRot + 1) % len(Sizes[self.BlockInd])
        newPos = self.BlockPos.copy()
        # try just rotating
        if not self.OutOfBounds(Sizes[self.BlockInd][newRot], newPos):
            self.BlockPos = newPos
            self.BlockRot = newRot
            return
        # try shifting left once and rotating
        newPos[0] -= 1
        if not self.OutOfBounds(Sizes[self.BlockInd][newRot], newPos):
            self.BlockPos = newPos
            self.BlockRot = newRot
            return
        # try shifting left twice and rotating if it's a line piece
        newPos[0] -= 1
        if (not self.OutOfBounds(Sizes[self.BlockInd][newRot], newPos)) and self.BlockInd == 1:
            self.BlockPos = newPos
            self.BlockRot = newRot
            return
        # try shifting right and rotating
        newPos[0] += 3
        if not self.OutOfBounds(Sizes[self.BlockInd][newRot], newPos):
            self.BlockPos = newPos
            self.BlockRot = newRot
            return

    def MoveHorizontal(self, Direction):  # try shift the block horizontally by the given value
        newPos = [self.BlockPos[0] + Direction, self.BlockPos[1]]
        if not self.OutOfBounds(Sizes[self.BlockInd][self.BlockRot], newPos):
            self.BlockPos = newPos

    def MoveDown(self):  # try moving down otherwise place the block in its current position
        newPos = [self.BlockPos[0], self.BlockPos[1] + 1]
        if not self.OutOfBounds(Sizes[self.BlockInd][self.BlockRot], newPos):
            self.BlockPos = newPos
        else:  # place the block
            # update board
            Pos = self.BlockPos
            Shape = Sizes[self.BlockInd][self.BlockRot]
            for i in range(len(Shape)):
                x, y = Pos[0] + Shape[i][0], Pos[1] + Shape[i][1]
                self.Board[x][y] = self.BlockInd

            # update the board and create a new block
            self.CheckForRows(self.Board, True)
            self.BlockPos = [self.BoardWidth//2,0]
            self.BlockRot = 0
            self.CanSwapBlock = True
            self.BlockInd = self.NextBlock
            self.NextBlock = self.RandomBlock()

            # the new block is also invalid so the game is over
            if self.OutOfBounds(Sizes[self.BlockInd][self.BlockRot], self.BlockPos):
                return [False, 1]
            else:
                return [True, 1]

        return [True, 0]

    def RandomBlock(self):  # generate a random block ID depending on if the extension is active or not
        if not self.Extension:
            return random.randint(0, 6)
        else:
            return random.randint(0, 8)

    def HoldBlock(self):  # hold the current block
        if self.HeldBlock == -1:
            self.CanSwapBlock = False
            self.BlockPos = [self.BoardWidth // 2, 0]
            self.BlockRot = 0

            self.HeldBlock = self.BlockInd
            self.BlockInd = self.NextBlock
            self.NextBlock = self.RandomBlock()
        else:
            if self.CanSwapBlock:
                self.CanSwapBlock = False
                self.BlockPos = [self.BoardWidth // 2, 0]
                self.BlockRot = 0

                temp = self.HeldBlock
                self.HeldBlock = self.BlockInd
                self.BlockInd = temp

def pauseGame(screen, manager, score):
    gui_elements = []
    continue_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((150, 400), (200, 50)), 
            text="Continue", manager=manager)
    gui_elements.append(continue_button)
    quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((450, 400), (200, 50)), 
            text="Quit", manager=manager)
    gui_elements.append(quit_button)
    Pause_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((0, 100), (800, 100)), 
            html_text=f"<font size={7}>{'Game Paused'}</font>", manager=manager)
    gui_elements.append(Pause_text)
    Pause_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((0, 200), (800, 100)), 
            html_text=f"<font size={5}>{'Current Score: ' + str(score)}</font>", manager=manager)
    gui_elements.append(Pause_text)

    for element in gui_elements:
        element.visible = False
    clock = pygame.time.Clock()

    pauseScreenActive = True
    while pauseScreenActive:
        for event in pygame.event.get():
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == continue_button:
                    for element in gui_elements:
                        element.hide()
                    pauseScreenActive = False
                    return False
                if event.ui_element == quit_button:
                    for element in gui_elements:
                        element.hide()
                    pauseScreenActive = False
                    return True
                
            if event.type == pygame.QUIT:
                for element in gui_elements:
                    element.hide()
                pauseScreenActive = False
                return True
            manager.process_events(event)

        manager.update(clock.tick(60) / 1000.0)
        screen.fill((0, 0, 0))
        manager.draw_ui(screen)
        for element in gui_elements:
            element.show()
        pygame.display.flip()

def startGame(newWidth, newHeight, isExtension, newLevel, isAI, screen, manager, music, font):  # called at the start of the game
    clock = pygame.time.Clock()
    playing = True
    fps = 25
    pos = [250,175]
    game = GameClass(newWidth, newHeight, isExtension, fps)
    game.__init__(newWidth, newHeight, isExtension, fps)  # restart game

    level = newLevel
    BlockWidth = 20  # pixel width of each block
    DownFast, left, right = False, False, False  # movement bools so you can hold down to move
    movementCooldown = 0
    counter = 0

    # calculate game board position
    pos[0] = (width - newWidth * BlockWidth) / 2
    pos[1] = (height - newHeight * BlockWidth) / 4 * 3

    # Ai values
    AIPlaying = isAI
    targetPos = -1
    targetRot = 0

    # Play Music
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)

    # Font Colour
    colour = pygame.Color("#ED9008")

    while playing:
        screen.fill((0, 0, 0))  # set screen background

        # increase the tick timers
        counter += 1
        movementCooldown += 1

        # move block down
        if counter > (fps//(level * game.Speed)) or (DownFast and counter > (fps//(level * game.Speed))/10):
            returnVal = game.MoveDown()
            if not returnVal[0]:  # game is over
                playing = False
                pygame.mixer.music.stop()
                return game.Score
            if returnVal[1] == 1:
                targetPos = -1
            counter = 0

        # move block sideways
        if left and movementCooldown > fps/10:
            game.MoveHorizontal(-1)
            movementCooldown = 0
        if right and movementCooldown > fps/10:
            game.MoveHorizontal(1)
            movementCooldown = 0

        # get inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # quit game
                playing = False
            if event.type == pygame.KEYDOWN:  # pause game
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        if pauseGame(screen, manager, game.Score) == True:
                            pygame.mixer.music.stop()
                            return game.Score
            if not AIPlaying:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game.Rotate()
                    if event.key == pygame.K_DOWN:
                        DownFast = True
                    if event.key == pygame.K_LEFT:
                        left = True
                    if event.key == pygame.K_RIGHT:
                        right = True
                    if event.key == pygame.K_SPACE:
                        game.HoldBlock()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        DownFast = False
                    if event.key == pygame.K_LEFT:
                        left = False
                    if event.key == pygame.K_RIGHT:
                        right = False
        if AIPlaying:  # AI logic
            if targetPos == -1:
                DownFast = False
                bestFitness = -1000000
                bestInd = -1
                bestRot = -1
                holding = False

                for i in range(game.BoardWidth):
                    for newRot in range(len(Sizes[game.BlockInd])):
                        newShape = Sizes[game.BlockInd][newRot]
                        if game.OutOfBounds(newShape, [i,0]):
                            continue

                        newFitness = fitnessRating(game, newShape, i)

                        if newFitness > bestFitness:
                            bestFitness = newFitness
                            bestInd = i
                            bestRot = newRot
                            holding = False
                    heldID = game.NextBlock
                    if game.HeldBlock != -1:
                        heldID = game.HeldBlock
                    for newRot in range(len(Sizes[heldID])):
                        newShape = Sizes[heldID][newRot]
                        if game.OutOfBounds(newShape, [i, 0]):
                            continue

                        newFitness = fitnessRating(game, newShape, i)

                        if newFitness > bestFitness:
                            bestFitness = newFitness
                            bestInd = i
                            bestRot = newRot
                            holding = True

                targetPos = bestInd
                targetRot = bestRot
                if holding:
                    game.HoldBlock()
            else:
                if game.BlockPos[0] < targetPos:
                    left = False
                    right = True
                elif game.BlockPos[0] > targetPos:
                    left = True
                    right = False
                else:
                    left = False
                    right = False
                if game.BlockRot != targetRot:
                    game.Rotate()
                elif game.BlockPos[0] == targetPos:
                    DownFast = True

        # Render Grid
        for i in range(game.BoardWidth):
            for j in range(game.BoardHeight):
                # draw Grid
                pygame.draw.rect(screen, "#222E25", [i*BlockWidth + pos[0], j*BlockWidth + pos[1],
                                                     BlockWidth, BlockWidth], 1)
                
                # draw A square if there is one
                if game.ClearedRows[j] >= 0 and game.Board[i][j] != -1:
                    W = 1 - game.ClearedRows[j]/fps
                    OC = Colours[game.Board[i][j]]
                    newColour = (255-(255 - OC[0]) * W, 255-(255 - OC[1]) * W, 255-(255 - OC[2]) * W)
                    pygame.draw.rect(screen, newColour, 
                                    [i * BlockWidth + pos[0] + 1, j * BlockWidth + pos[1] + 1, BlockWidth - 2, BlockWidth - 2])
                elif game.ClearedRows[j] >= 0 and game.Board[i][j] == -1:
                    W = game.ClearedRows[j]/fps
                    pygame.draw.rect(screen, (255 * W, 255 * W, 255 * W), 
                                    [i * BlockWidth + pos[0] + 1, j * BlockWidth + pos[1] + 1, BlockWidth - 2, BlockWidth - 2])
                elif game.Board[i][j] != -1:
                    pygame.draw.rect(screen, Colours[game.Board[i][j]], [i * BlockWidth + pos[0] + 1,
                                                                        j * BlockWidth + pos[1] + 1,
                                                                        BlockWidth - 2, BlockWidth - 2])

        #process animation
        for i in range(len(game.ClearedRows)):
            if game.ClearedRows[i] >= 0:
                game.ClearedRows[i] -= 1

        # Render Block
        for i in range(len(Sizes[game.BlockInd][0])):
            BlockCords = Sizes[game.BlockInd][game.BlockRot][i]
            BlockColour = Colours[game.BlockInd]
            BlockPos = game.BlockPos
            pygame.draw.rect(screen, BlockColour, [(BlockCords[0] + BlockPos[0]) * BlockWidth + pos[0] + 1,
                                                   (BlockCords[1] + BlockPos[1]) * BlockWidth + pos[1] + 1,
                                                   BlockWidth-2, BlockWidth-2])

        # Render Next Block
        NBXPos = pos[0] + BlockWidth * newWidth + 50
        NBFont = pygame.font.Font(font, 30)
        NBLabel = NBFont.render("Next Block", 1, colour)
        screen.blit(NBLabel, (NBXPos,200))
        NBx, NBy = NBXPos + 50, 250
        for i in range(len(Sizes[game.NextBlock][0])):
            BlockCords = Sizes[game.NextBlock][0][i]
            BlockColour = Colours[game.NextBlock]
            # draw outline
            pygame.draw.rect(screen, "#121E15", [BlockCords[0] * BlockWidth + NBx,
                                                 BlockCords[1] * BlockWidth + NBy,
                                                 BlockWidth, BlockWidth], 1)
            # draw colour
            pygame.draw.rect(screen, BlockColour, [BlockCords[0] * BlockWidth + NBx + 1,
                                                   BlockCords[1] * BlockWidth + NBy + 1,
                                                   BlockWidth-2, BlockWidth-2])

        # Render Held Block
        HBXPos = pos[0] - 215
        HBFont = pygame.font.Font(font, 30)
        HBLabel = HBFont.render("Held Block", 1, colour)
        screen.blit(HBLabel, (HBXPos, 200))
        HBx, HBy = HBXPos + 50, 250
        if game.HeldBlock != -1:
            for i in range(len(Sizes[game.HeldBlock][0])):
                BlockCords = Sizes[game.HeldBlock][0][i]
                BlockColour = Colours[game.HeldBlock]
                # draw outline
                pygame.draw.rect(screen, "#121E15", [BlockCords[0] * BlockWidth + HBx,
                                                     BlockCords[1] * BlockWidth + HBy,
                                                     BlockWidth, BlockWidth], 1)
                # draw colour
                pygame.draw.rect(screen, BlockColour, [BlockCords[0] * BlockWidth + HBx + 1,
                                                       BlockCords[1] * BlockWidth + HBy + 1,
                                                       BlockWidth - 2, BlockWidth - 2])

        clock.tick(fps)
        pygame.display.flip()
    pygame.mixer.music.stop()

def fitnessRating(game, newShape, i):
    highestPos = 0
    while not game.OutOfBounds(newShape, [i, highestPos + 1]):
        highestPos += 1
    # temp apply changes
    tempBoard = deepcopy(game.Board)
    for u in range(len(newShape)):
        tempBoard[i + newShape[u][0]][highestPos + newShape[u][1]] = 1
    game.CheckForRows(tempBoard, False)
    # calculate fitness
    newFitness = 0
    lowestBlock = game.BoardHeight
    for u in range(game.BoardWidth):
        heightAdded = False
        for v in range(game.BoardHeight):
            if not heightAdded:
                if tempBoard[u][v] != -1 or v == game.BoardHeight - 1:
                    newFitness += v
                    heightAdded = True
                    if v < lowestBlock:
                        lowestBlock = v
            else:
                if tempBoard[u][v] == -1 and tempBoard[u][v - 1] != -1:
                    newFitness -= 5
    newFitness += lowestBlock * 2.5
    return newFitness
