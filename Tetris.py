from copy import deepcopy
import time
import numpy as np
from PIL import Image
import cv2
import random

from Point import Point
import Tetromino

TETRIS_COLORS = {
    -1: [0, 0, 0],
    0 : [255, 255, 255],
    1 : [164,182,221],
    2 : [208,146,146],
    3 : [192,148,204],
    4 : [162,208,192],
    5 : [195,120,146],
}

class Tetris:

    def __init__(self, width, height, seed=None) -> None:
        self.WIDTH = width
        self.HEIGHT = height

        if not seed:
            self._random = random.Random()
        else:
            self._random = random.Random(seed)

        ### STATE:
        self.board = [[0 for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]
        self.terminal_state = False
        self.highest_tile = -1
        self.tiles_placed = 0
        self._calc_next_tile()

    def render(self) -> None:
        '''
        Draw board to screen
        '''
        pixel_data = []
        for y in range(len(self.board[0])-1, -1, -1):
            for x in range(len(self.board)):
                pixel_data.append(TETRIS_COLORS[self.board[x][y]])


        pixel_data = np.array(pixel_data).reshape(self.HEIGHT, self.WIDTH, 3).astype(np.uint8)
        img = Image.fromarray(pixel_data) 
        img = img.resize((self.WIDTH*32, self.HEIGHT*32), resample=Image.Resampling.NEAREST)
        data = np.array(img)

        cv2.imshow('a', data)
        cv2.waitKey(1) # use waitKey(1) when rending multiple times

    def get_actions(self):
        tetromino = Tetromino.PIECES[self.next_tile]

        return self._bfs(tetromino, self._spawn_point(), "right")

    def take_action(self, point: Point, orientation: str):
        tetromino = Tetromino.PIECES[self.next_tile][orientation]

        # if this fails action is illegal
        assert self._is_legal_placement(tetromino, point) 

        self._place_tetronimo(tetromino, point)
        self.tiles_placed += 1

        self._clear_lines()

        self._calc_next_tile()

        # Check if next tile can be spawned, if it cannot game is over
        if not self._is_legal_placement(Tetromino.PIECES[self.next_tile]["right"], self._spawn_point()):
            self.terminal_state = True

        ## TODO: return reward?

    def get_state(self):
        ## TODO: return value that represent the state of the game (board, next_tile, score, e.t.c)
        ## This might be used by the DQN algorithm
        pass

    def get_state_copy(self):
        ## TODO: same as above
        return deepcopy(self.board)

    def _clear_lines(self) -> None:
        filled_rows = []

        for y in range(self.HEIGHT):
            isFilled = True
            for x in range(self.WIDTH):
                if self.board[x][y] == 0:
                    isFilled = False
                    break

            if isFilled:
                filled_rows.insert(0, y)


        for col in self.board:
            for y in filled_rows:
                del col[y]
                col.append(0)

        self.highest_tile -= len(filled_rows)

    def _place_tetronimo(self, tetromino: Tetromino.RotatedTetromino, point: Point, COLOR=None):
        if COLOR == None:
            COLOR = random.randint(1, len(TETRIS_COLORS)-2) # -1 and 0 are black and white

        for tile_offset in tetromino['points']:
            tile_pos = point + tile_offset
            self.board[tile_pos.x][tile_pos.y] = COLOR

            if tile_pos.y > self.highest_tile:
                self.highest_tile = tile_pos.y

    def _remove_tetronimo(self, tetromino: Tetromino.RotatedTetromino, point: Point):
        for tile_offest in tetromino['points']:
            tile_pos = point + tile_offest
            self.board[tile_pos.x][tile_pos.y] = 0

    def _is_legal_placement(self, tetromino: Tetromino.RotatedTetromino, point: Point):
        """
        Checks that placing a tetronimo exactly at `point` doesn't either go out-of-bounds
        or intersect with a tile on the board 
        """
        for tile_offset in tetromino['points']:
            tile_pos = point + tile_offset
            if self._is_out_of_bounds(tile_pos) or self.board[tile_pos.x][tile_pos.y] != 0:
                return False
        return True

    def _is_out_of_bounds(self, point: Point):
        if 0 <= point.x < self.WIDTH:
            if 0 <= point.y < self.HEIGHT:
                return False
        return True


    def _bfs(self, tetromino: Tetromino.Tetrominos, point: Point, starting_orientation) -> list[tuple[int, str]]:
        '''
        breadth-first search of all possible placements for a `tetromino`

        returns a list of tuples of shape: (tetromino_position: `int`, tetromino_orientation: `str`)
        '''
        visited = []
        queue = []
        end_states: list[tuple[int, str]] = []

        visited.append((point, starting_orientation))
        queue.append((point, starting_orientation))
        while len(queue) != 0:
            pass
            curr_point, curr_orientation = queue.pop()

            # If we cannot legally move down, then there must be something below us
            # i.e we are at an end state
            if not self._is_legal_placement(tetromino[curr_orientation], curr_point + Point(0, -1)):
                end_states.append((curr_point, curr_orientation))

            next_orientations = self._get_rotations(curr_orientation, tetromino)

            # Iterate over all possible next moves for tetronimo, e.g: (move left, move right, move down, rotate)
            for next_point, next_orientation in [
                (curr_point+Point(1, 0), curr_orientation),
                (curr_point+Point(-1, 0), curr_orientation),
                (curr_point+Point(0, -1), curr_orientation),
            ] + [(curr_point, next_orientation) for next_orientation in next_orientations]:
                if self._is_legal_placement(tetromino[next_orientation], next_point):
                    if (next_point, next_orientation) not in visited:
                        visited.append((next_point, next_orientation))
                        queue.append((next_point, next_orientation))

        return end_states
            

    def _get_rotations(self, current_orientation, tetromino: Tetromino.Tetrominos):
        if tetromino["num_rotations"] == 1:
            return [current_orientation]

        if tetromino["num_rotations"] == 2:
            if current_orientation == "up":
                return ["right"]
            if current_orientation == "right":
                return ["up"]

        if tetromino["num_rotations"] == 4:
            if current_orientation == "up":
                return ["right", "left"]
            if current_orientation == "right":
                return ["up", "down"]
            if current_orientation == "down":
                return ["right", "left"]
            if current_orientation == "left":
                return ["up", "down"]
        
    def _calc_next_tile(self):
        self.next_tile = self._random.choice(Tetromino.PIECES_NAMES)

    def _spawn_point(self):
        '''
        Where all the tetrominoes spawn from at the top of the board
        '''
        return Point(self.WIDTH//2-1, min(self.HEIGHT-2, self.highest_tile+1))



# t = Tetris(10, 8)

# t._place_tetronimo(Tetromino.PIECES["T"]["up"], Point(0, 0))
# t._place_tetronimo(Tetromino.PIECES["T"]["up"], Point(3, 0))
# t._place_tetronimo(Tetromino.PIECES["T"]["up"], Point(6, 0))
# t._place_tetronimo(Tetromino.PIECES["I"]["up"], Point(7, 0))
# # t._place_tetronimo(Tetromino.PIECES["T"]["up"], Point(4, 2))
# # t._place_tetronimo(Tetromino.PIECES["T"]["left"], Point(0, 2))
# t.render()
# time.sleep(1)

# t._clear_lines()

# t.render()

# time.sleep(1)

# end_s = t.get_actions()

# print(len(end_s))

# for s in end_s:
#     print(t.next_tile)
#     t._place_tetronimo(Tetromino.PIECES[t.next_tile][s[1]], s[0], COLOR=-1)
#     t.render()
#     print(s)
#     time.sleep(0.2)
#     t._remove_tetronimo(Tetromino.PIECES[t.next_tile][s[1]], s[0])


# t.render()
# # time.sleep(10)
