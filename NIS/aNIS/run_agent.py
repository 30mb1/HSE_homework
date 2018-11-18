import gym
from agent import Agent
import pickle
import numpy as np
import time

episodes_number = 300
max_steps = 500

if __name__ == '__main__':

    # load map from compressed file
    map_array = np.load('1.npz')

    print (map_array['arr_0'])

    env = gym.make('labirint-v0')
    env._configure(map_array['arr_0'])
    env.render("human")

    agent = Agent(map_shape=map_array['arr_0'].shape, gamma=0.8)
    agent.reset()

    for episode_i in range(episodes_number):
        done = False
        observation = env.reset()

        for step_i in range(max_steps):
            action = agent.act(observation)
            next_observation, reward, done, _ = env.step(action)
            agent.update_memory(observation, action, reward, next_observation)
            observation = next_observation
            if done:
                done = True
                break

        if episode_i % 100 == 0:
            print ('Episode {} ended.'.format(episode_i))


    print ('Learning phase ended, trying to find the way using memory.')

    observation = env.reset(learning=False)
    env.render('human')
    time.sleep(0.3)
    steps = 0

    while True:
        steps += 1
        action = agent.go_best_way(observation)
        next_observation, _, done, _ = env.step(action)
        env.render("human")
        observation = next_observation
        time.sleep(0.1)
        if done:
            break

    print ('Found way from {} to {} in {} steps.'.format(env.start_point, env.finish_point, steps))
    time.sleep(5)
