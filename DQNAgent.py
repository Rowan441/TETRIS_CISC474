import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import random
from tqdm import tqdm
import time
import psutil


import tensorflow as tf
import numpy as np


import Tetris

### Environment
WIDTH = 10
HEIGHT = 18
tetris = Tetris.Tetris(WIDTH, HEIGHT)

### Training Hyperparameters
discount = 0.99
epsilon = 1
epsilon_min = 0.1
epsilon_interval = epsilon - epsilon_min
epsilon_decay_steps = 1000
max_episodes = 2000
max_steps_per_episode = 10000
random_play_steps = 2000
batch_size = 512
epochs = 1
max_memory_length = 300000

## Model
input_size = 4 #WIDTH * HEIGHT
model = tf.keras.Sequential()
model.add(tf.keras.layers.Input(shape=(input_size)))
model.add(tf.keras.layers.Dense(32, activation='relu'))
model.add(tf.keras.layers.Dense(32, activation='relu'))
model.add(tf.keras.layers.Dense(1, activation="linear"))
model.compile(optimizer='adam', loss='mse')

memory = []
episode_reward_history = []
average_reward = 0
total_episodes = 0
total_steps = 0

f = open("stats.txt", "w")
f.write("data\n")
f.close()

start = time.time()

with tqdm(total=100, desc='cpu%', position=1) as cpubar, tqdm(total=100, desc='ram%', position=0) as rambar, tqdm(total=2000, desc="episode#", position=2) as episode_number:
    while(True):
        # ram usage diagnostics
        rambar.n=psutil.virtual_memory().percent
        cpubar.n=psutil.cpu_percent()
        rambar.refresh()
        cpubar.refresh()
        episode_number.n = total_episodes
        episode_number.refresh()

        episode_reward = 0
        tetris.reset_state()
        try:
            for step in range(1, max_steps_per_episode):
                total_steps += 1

                current_state = tetris.get_state()
                possible_actions = tetris.get_actions()

                # Choose action via e-greedy
                if total_steps < random_play_steps or np.random.rand(1)[0] < epsilon:
                    action = random.choice(possible_actions)
                    next_state = tetris.state_after_action(action[0], action[1])
                else:
                    # Predict q-value for each possible action and choose the action that leads to highest q-value

                    next_states = np.array(list(map(lambda action: tetris.state_after_action(action[0], action[1]), possible_actions)))

                    estimated_q_values = model.predict(next_states, verbose=0) ## TODO: replace with predict?
            
                    best_action_index = tf.argmax(estimated_q_values).numpy()[0]

                    action = possible_actions[best_action_index]
                    next_state = next_states[best_action_index]

                # take action chosen in environment
                reward, done = tetris.take_action(action[0], action[1])
                # tetris.render()

                episode_reward += reward

                # Save actions and states in replay buffer
                memory.append((current_state, next_state, reward, done))

                if total_steps > random_play_steps and len(memory) > batch_size:

                    batch = random.sample(memory, batch_size)
                    
                    next_states = np.array([experience[1] for experience in batch])

                    future_rewards = model.predict(next_states, verbose=0)

                    states = []
                    computed_q_values = []

                    for i, (sample_state, _, sample_reward, sample_done) in enumerate(batch):
                        if sample_done:
                            q_value = sample_reward
                        else:
                            q_value = sample_reward + discount * future_rewards[i][0]

                        states.append(sample_state)
                        computed_q_values.append(q_value)
                    
                    states = np.array(states)
                    computed_q_values = np.array(computed_q_values)

                    model.fit(states, computed_q_values, batch_size=batch_size, epochs=epochs, verbose=0)
                    # tf.keras.backend.clear_session()

                if len(memory) > max_memory_length:
                    # remove oldest memory in the list
                    del memory[:1]

                if done:
                    break

            # update epsilon
            epsilon = epsilon - (epsilon_interval/epsilon_decay_steps)
            epsilon = max(epsilon, epsilon_min)

            episode_reward_history.append(episode_reward)
            if len(episode_reward_history) > 25:
                del episode_reward_history[:1]
            average_reward = np.mean(episode_reward_history)

            total_episodes += 1

            if total_episodes % 1 == 0:
                end = time.time()

                f = open("stats.txt", "a")
                output = ""
                output += f"Average Reward: {average_reward:.2f}, Total Episodes: {total_episodes}, Time: {end-start}, epsilon: {epsilon}, Episode Steps: {step}, RAM: {cpubar.n}\n"
                f.write(output)
                f.close()

                start = end

        except KeyboardInterrupt:
            print(f"memory buffer size: {len(memory)}")

            print("Keyboard Interrupt Detected. Stopping Training", end="\n\n")
            print(f"Total Episodes: {total_episodes}, Total Steps: {total_steps}, Average Reward (last 100 Episodes): {average_reward:.2f}")
            model.save(f'modeldata/{time.strftime("%Y%m%d-%H%M%S")}')
            exit(0)