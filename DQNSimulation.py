import tensorflow as tf
import Tetris
import numpy as np

MODEL_NAME = "20221204-163738"
model = tf.keras.models.load_model(f'modeldata/{MODEL_NAME}')

WIDTH = 10
HEIGHT = 18
tetris = Tetris.Tetris(WIDTH, HEIGHT)

step = 0
while(step < 90):
    step = 0
    tetris.reset_state()
    while(not tetris.terminal_state):
        step += 1

        possible_actions = tetris.get_actions()

        # get actions and transform for input into model
        next_states = np.array(list(map(lambda action: tetris.state_after_action(action[0], action[1]), possible_actions)))

        # estimate q value of each action
        estimated_q_values = model(next_states, training=False) ## TODO: replace with predict?

        # pick best action
        best_action_index = tf.argmax(estimated_q_values).numpy()[0]
        action = possible_actions[best_action_index]
        
        _, done = tetris.take_action(action[0], action[1])

        tetris.render(img_location = f"simulation/{step}.png")

    print(f"Finished. Rendered {step} frames")
