import random

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
row_values = [0,100,300,600,1000] # score earned per rows removed
width = 800
height = 600
game_object = None

class _GameClass:
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
        for j in range(self.board_height): # check each row if its full and remove it
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

def getGameObject(new_width, new_height, is_extension, fps):
    if game_object == None:
        return _GameClass(new_width, new_height, is_extension, fps)
    return game_object