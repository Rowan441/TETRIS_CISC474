from copy import deepcopy
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import random

from Point import Point
import Tetromino

TETRIS_COLORS = {
    -1: [0, 0, 0],
    0 : [255, 255, 255],
    1 : [164,182,221],
}

class Tetris:

    def __init__(self, width, height, seed=None) -> None:
        self.WIDTH = width
        self.HEIGHT = height
        

        if seed:
            self._random_seed = seed
        else:
             self._random_seed = random.Random()

        self.reset_state()

    def render(self, board=None, img_location="render.png") -> None:
        '''
        Draw board to screen
        '''
        if board is None:
            board = self.board

        pixel_data = []
        for y in range(len(board[0])-1, -1, -1):
            for x in range(len(board)):
                if (x, y) in self.latest_placement:
                    pixel_data.append([221,182,182])
                else:
                    pixel_data.append(TETRIS_COLORS[board[x][y]])


        pixel_data = np.array(pixel_data).reshape(self.HEIGHT, self.WIDTH, 3).astype(np.uint8)
        img = Image.fromarray(pixel_data) 
        img = img.resize((self.WIDTH*32, self.HEIGHT*32), resample=Image.Resampling.NEAREST)

        draw = ImageDraw.Draw(img)
        
        draw.text((20, 20), f"Next tile: {self.next_tile}", (0, 0, 0), font = ImageFont.truetype("arial.ttf", 18))

        img.save(img_location)

    def get_actions(self):
        tetromino = Tetromino.PIECES[self.next_tile]

        return self._bfs(tetromino, self._spawn_point(), "right")

    def take_action(self, point: Point, orientation: str):
        tetromino = Tetromino.PIECES[self.next_tile][orientation]

        # if this fails action is illegal
        assert self._is_legal_placement(tetromino, point) 

        highest_placement = self._place_tetronimo(tetromino, point)
        if highest_placement > self.highest_tile:
            self.highest_tile = highest_placement
        self.tiles_placed += 1

        cleared_rows = self._clear_lines()
        self.highest_tile -= cleared_rows
        self.total_lines_cleared += cleared_rows

        self._calc_next_tile()

        # Check if next tile can be spawned, if it cannot game is over
        if not self._is_legal_placement(Tetromino.PIECES[self.next_tile]["right"], self._spawn_point()):
            self.terminal_state = True

        reward = 2*cleared_rows*cleared_rows + (self.HEIGHT-self.highest_tile)
        if self.terminal_state:
            reward += -6

        return reward, self.terminal_state
        

    def state_after_action(self, point, orientation):
        '''
        Returns a copy of the state as a numpy array after taking action: (point, orientation)

        i.e. after placing the next tile at `point` with orientation `orientation`
        '''
        board = self.get_state_copy()
        tetromino = Tetromino.PIECES[self.next_tile][orientation]
        highest_placement = self._place_tetronimo(tetromino, point, board=board)
        highest_tile = max(self.highest_tile, highest_placement)
        
        lines_cleared = self._clear_lines(board=board)
        highest_tile -= lines_cleared
        total_lines_cleared = self.total_lines_cleared + lines_cleared

        # board = np.array(board).reshape(self.WIDTH*self.HEIGHT)

        return [highest_tile, total_lines_cleared, self._calc_bumpiness(board), self._calc_num_holes(board)]

    def get_state(self):
        # return np.array(self.board).reshape(self.WIDTH*self.HEIGHT) 
        return [self.highest_tile, self.total_lines_cleared, self._calc_bumpiness(), self._calc_num_holes()]

    def reset_state(self):
        self._random = random.Random()

        self.board = [[0 for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]
        self.terminal_state = False
        self.highest_tile = -1
        self.tiles_placed = 0
        self.total_lines_cleared = 0
        self._calc_next_tile()

    def get_state_copy(self):
        ## TODO: same as above
        return deepcopy(self.board)

    def _calc_num_holes(self, board=None):
        if board is None:
            board = self.board

        holes = 0

        for x in range(self.WIDTH):
            for y in range(self.HEIGHT-1, -1, -1):
                if board[x][y] != 0:
                    holes += sum([1 for x in board[x][:y] if x == 0])
                    break

        return holes

    def _calc_bumpiness(self, board=None):
        if board is None:
            board = self.board

        prev_col_height = None
        bumpiness = 0

        for x in range(self.WIDTH):
                for y in range(self.HEIGHT-1, -1, -1):
                    empty_col = True
                    if board[x][y] != 0:
                        if prev_col_height:
                            bumpiness += abs(prev_col_height - y)
                        prev_col_height = y
                        empty_col = False
                        break
                    # if there are no tiles in this column, don't compare bumpiness of next col
                if empty_col:
                    prev_col_height = None

        return bumpiness
                
    def _clear_lines(self, board = None) -> None:
        if board == None:
            board = self.board

        filled_rows = []

        for y in range(self.HEIGHT):
            isFilled = True
            for x in range(self.WIDTH):
                if board[x][y] == 0:
                    isFilled = False
                    break

            if isFilled:
                filled_rows.insert(0, y)


        for col in board:
            for y in filled_rows:
                del col[y]
                col.append(0)

        # Return number of lines cleared
        return len(filled_rows) 

    def _place_tetronimo(self, tetromino: Tetromino.RotatedTetromino, point: Point, COLOR=None, board=None):
        if board == None:
            board = self.board
        if COLOR == None:
            COLOR = random.randint(1, len(TETRIS_COLORS)-2) # -1 and 0 are black and white

        highest_tile = -1
        self.latest_placement = []

        for tile_offset in tetromino['points']:
            tile_pos = point + tile_offset
            board[tile_pos.x][tile_pos.y] = COLOR
            self.latest_placement.append((tile_pos.x, tile_pos.y))

            if tile_pos.y > highest_tile:
                highest_tile = tile_pos.y

        return highest_tile

    def _remove_tetronimo(self, tetromino: Tetromino.RotatedTetromino, point: Point, board=None):
        if board == None:
            board = self.board

        for tile_offest in tetromino['points']:
            tile_pos = point + tile_offest
            board[tile_pos.x][tile_pos.y] = 0

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


    def _bfs(self, tetromino: Tetromino.Tetrominos, point: Point, starting_orientation: str) -> list[tuple[Point, str]]:
        '''
        breadth-first search of all possible placements for a `tetromino`

        returns a list of tuples of shape: (tetromino_position: `Point`, tetromino_orientation: `str`)
        '''
        visited = []
        queue = []
        end_states: list[tuple[Point, str]] = []

        visited.append((point, starting_orientation))
        queue.append((point, starting_orientation))
        while len(queue) != 0:
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
