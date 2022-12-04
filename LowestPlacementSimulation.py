import time
from Tetris import Tetris

t = Tetris(10, 18)

step = 0
while not t.terminal_state:
    step += 1
    actions = t.get_actions()

    # pick action with placement location with lowest y value (height) 
    actions.sort(key=lambda action: action[0].y)

    point, orientation = actions[0]

    t.take_action(point, orientation)

    t.render(img_location = f"simulation/{step}.png")

    time.sleep(0.1)

print(f"Finished. Rendered {step} frames")