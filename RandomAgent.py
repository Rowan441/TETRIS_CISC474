import time
from Tetris import Tetris
import random


t = Tetris(10, 18)

while not t.terminal_state:
    actions = t.get_actions()

    actions.sort(key=lambda action: action[0].y)
    point, orientation = actions[0]

    t.take_action(point, orientation)

    t.render()

    time.sleep(0.1)