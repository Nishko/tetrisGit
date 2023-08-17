import pygame
import random
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
width = 700
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
    BoardWidth = 10
    BoardHeight = 20
    Score = 0
    Extension = False
    CanSwapBlock = True

    def __init__(self, newWidth, newHeight, isExtension):
        # assign needed variables
        self.BoardWidth, self.BoardHeight = newWidth, newHeight
        self.Extension = isExtension
        self.BlockPos[0] = newWidth//2
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

    def CheckForRows(self, board, addScore):  # check each row if it's completed and if so remove it
        rowsRemoved = 0
        for j in range(self.BoardHeight):
            full = True
            for i in range(self.BoardWidth):
                if board[i][j] == -1:
                    full = False
                    break

            if full:  # remove row if it's completed
                rowsRemoved += 1
                for v in range(j,0,-1):
                    for u in range(self.BoardWidth):
                        board[u][v] = board[u][v-1]
        if addScore:
            self.Score += RowValues[rowsRemoved]

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


def endGame(score):  # called at the end of the game
    endScreenActive = True

    while endScreenActive:  # a temp end screen to be replaced by Matt
        screen.fill((50, 90, 10))
        font = pygame.font.SysFont("Calibri", 70, bold=True)
        label1 = font.render("Game Over.", True, '#FFFFFF')
        label2 = font.render(str(score), True, "#FFFFFF")
        label1Size = label1.get_size()
        label2Size = label2.get_size()

        screen.blit(label1, ((width - label1Size[0]) / 2, (height - label1Size[1]) / 2))
        screen.blit(label2, ((width - label2Size[0]) / 2, (height - label2Size[1]) / 2 + label1Size[1]))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                endScreenActive = False


def startGame(newWidth, newHeight, isExtension, newLevel, isAI):  # called at the start of the game
    clock = pygame.time.Clock()
    playing = True
    fps = 25
    pos = [250,175]
    game = GameClass(newWidth, newHeight, isExtension)
    game.__init__(newWidth, newHeight, isExtension)  # restart game

    level = newLevel
    BlockWidth = 20  # pixel width of each block
    DownFast, left, right = False, False, False  # movement bools so you can hold down to move
    movementCooldown = 0
    counter = 0

    # Ai values
    AIPlaying = isAI
    targetPos = -1
    targetRot = 0

    while playing:
        screen.fill("#FFFFFF")  # set screen background

        # increase the tick timers
        counter += 1
        movementCooldown += 1

        # move block down
        if counter > (fps//level) or (DownFast and counter > (fps//level)/10):
            returnVal = game.MoveDown()
            if not returnVal[0]:  # game is over
                playing = False
                endGame(game.Score)
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
                pygame.draw.rect(screen, "#121E15", [i*BlockWidth + pos[0], j*BlockWidth + pos[1],
                                                     BlockWidth, BlockWidth], 1)
                # draw A square if there is one
                if game.Board[i][j] != -1:
                    pygame.draw.rect(screen, Colours[game.Board[i][j]], [i * BlockWidth + pos[0] + 1,
                                                                         j * BlockWidth + pos[1] + 1,
                                                                         BlockWidth - 2, BlockWidth - 2])

        # Render Block
        for i in range(len(Sizes[game.BlockInd][0])):
            BlockCords = Sizes[game.BlockInd][game.BlockRot][i]
            BlockColour = Colours[game.BlockInd]
            BlockPos = game.BlockPos
            pygame.draw.rect(screen, BlockColour, [(BlockCords[0] + BlockPos[0]) * BlockWidth + pos[0] + 1,
                                                   (BlockCords[1] + BlockPos[1]) * BlockWidth + pos[1] + 1,
                                                   BlockWidth-2, BlockWidth-2])

        # Render Next Block
        NBXPos = game.BoardWidth * BlockWidth + 300
        NBFont = pygame.font.SysFont("Calibri", 30)
        NBLabel = NBFont.render("Next Block", 1, (128, 128, 128))
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
        HBFont = pygame.font.SysFont("Calibri", 30)
        HBLabel = HBFont.render("Held Block", 1, (128, 128, 128))
        screen.blit(HBLabel, (100, 200))
        HBx, HBy = 150, 250
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


screen = pygame.display.set_mode((width,height))  # create the screen
pygame.display.set_caption("Tetris")  # name screen window
running = True

while running:  # This is a temp intro screen and will be replaced by Matt
    screen.fill((16, 57, 34))
    font = pygame.font.SysFont("Calibri", 70, bold=True)
    label = font.render("Press any key to begin!", True, '#FFFFFF')
    labelSize = label.get_size()

    screen.blit(label, ((width-labelSize[0])/2, (height-labelSize[1])/2))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            startGame(15, 20, True, 10, True)  # (board width, board height, run extension, level)
pygame.quit()