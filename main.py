from nes_py.wrappers import JoypadSpace
import gym_tetris
from gym_tetris.actions import SIMPLE_MOVEMENT

env = gym_tetris.make('TetrisA-v1')
env = JoypadSpace(env, SIMPLE_MOVEMENT)

done = True
for step in range(5000):
    if done:
        state = env.reset()

    random_action = env.action_space.sample()
    state, reward, done, info = env.step(random_action)
    
    env.render(mode = "human")

env.close()

