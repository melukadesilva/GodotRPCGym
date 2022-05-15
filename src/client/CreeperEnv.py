"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""

import torch
import numpy as np

import gym
from gym import spaces

import observation_action_pb2
import observation_action_pb2_grpc

class CreeperEnv(gym.Env):
    """
    Description:
        Creeper that follows the player, a continuous environment
    Observation: 
        Type: Box(8)
        Num	Observation     
        0	Creeper x position      
        1	Creeper y position
        2	Creeper x velocity
        3	Creeper y velocity
        4	Player x position      
        5	Player y position
        6	Player x velocity
        7	Player y velocity
        
    Actions:
        Type: Box(3)
        Num	Action
        0	Creeper x velocity
        1	Creeper y velocity
        2   Creeper angle
        
    Reward:
        reward: hit_reward + distance_reward
        hit_reward      : +100 when creeper hit the player
        hit_reward      : -100 when episode ends without a hit
        distance_reward : sqrt([player_x_position - creeper_x_position]^2 + [player_y_position - creeper_y_position]^2)
    Starting State:
        Initialized with player and creeper position. Player start with a random velocity that is constant throughout the episode
    Episode Termination:
        Terminated after 400 timeouts
    """

    def __init__(self, channel, num_actions=1, num_observations=3, render=True):

        #Example of agent action
        self.agent_action = torch.zeros(1, dtype=torch.float, device='cpu')

        # Normalised action range
        action_low = np.array([-1.0, -1.0, -1.0])
        action_high = np.array([1.0, 1.0, 1.0])

        # Normalised observation range
        observation_low = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        observation_high = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

        # Gym Boxes for continuous spaces
        self.action_space = spaces.Box(low=action_low, high=action_high, shape=(num_actions,), dtype=np.float32)
        self.observation_space = spaces.Box(low=observation_low, high=observation_high, shape=(num_observations,), dtype=np.float32)

        # GRPC stub for client
        self.stub = observation_action_pb2_grpc.RLCStub(channel)

    def seed(self, seed=None):
        pass

    # Step on the environment
    def step(self, action):
        # Denormalize the actions
        action_vector = action
        action_vector[0] = action_vector[0] * 250.0
        action_vector[1] = action_vector[1] * 250.0
        action_vector[2] = action_vector[2] * np.pi
        # Request the server with the computed actions and get the observations, reward and is_done as a response (sync)
        response_step = self.stub.Step(observation_action_pb2.ActionData(action_index=action_vector, env_action=0))

        observation = response_step.observations
        reward = response_step.reward
        done = response_step.is_done

        # Dummy meta info for the baseline-3
        infos = {
            "episode": None,
            "is_success": None,
        }

        return observation, reward, done, infos

    # Reset the environment 
    def reset(self, seed=42):
        # submit a reset request with empty protoc message and get the initial observation
        response_reset = self.stub.Reset(observation_action_pb2.Empty())

        observation = response_reset.observations

        return observation
        
    def render(self, mode='human'):
        pass

    # Once the training is done terminate the game
    def terminate(self):
        # Request a game termination with an empty protoc
        self.stub.Terminate(observation_action_pb2.Empty())
