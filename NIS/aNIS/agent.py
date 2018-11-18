import collections
import random
import numpy



class Agent(object):

    def __init__(self, map_shape, gamma=0.8):
        self.map_shape = map_shape
        self.q_table = []
        self.action_space = { 'left' : [-1, 0], 'up' : [0, 1], 'right' : [1, 0], 'down' : [0, -1]}
        self.gamma = gamma

    def reset(self):
        # reinitialize q_table with zeros
        self.q_table = [{'left' : 0, 'up' : 0, 'right' : 0, 'down' : 0} for i in range(self.map_shape[0] * self.map_shape[1])]

    def act(self, observation):
        action = random.choice(observation[0])
        return action

    def update_memory(self, observation, action, reward, next_observation):
        cur_point = observation[1]
        new_point = next_observation[1]

        next_point_variants = [self.q_table[new_point[0] * self.map_shape[0] + new_point[1]][act] for act in next_observation[0]]

        self.q_table[cur_point[0] * self.map_shape[0] + cur_point[1]][action] = reward + self.gamma * max(next_point_variants)

    def go_best_way(self, observation):
        cur_point = observation[1]

        best_q, best_way = 0, random.choice(observation[0])
        for i in self.action_space.keys():
            cur_q = self.q_table[cur_point[0] * self.map_shape[0] + cur_point[1]][i]
            if cur_q > best_q:
                best_q = cur_q
                best_way = i

        return best_way
