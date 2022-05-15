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

class InvPendulumEnv(gym.Env):
    """
    Description:
        Standard inverted pendulum environment but for the discrete action space
    Observation: 
        Type: Box(3)
        Num	Observation     
        0	Cos(theta)      
        1	Sin(theta)      
        2	Angular velocity
        
    Actions:
        Type: [Continuous(1)]
        Num	Action
        0	Torque
        
    Reward:
        var n_theta = fmod((theta + PI), (2*PI)) - PI
        reward = (n_theta*n_theta + .1*angular_velocity*angular_velocity)
    Starting State:
        Initialized with random angle
    Episode Termination:
        Terminated after 10s
    """

    def __init__(self, channel, num_actions=1, num_observations=3, render=True):

        #Example of agent action
        self.agent_action = torch.zeros(1, dtype=torch.float, device='cpu')

        self.max_torque = 8.0
        self.max_speed = 8

        self.action_space = spaces.Box(low=-self.max_torque, high=self.max_torque, shape=(num_actions,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(num_observations,), dtype=np.float32)

        self.stub = observation_action_pb2_grpc.RLCStub(channel)

    def seed(self, seed=None):
        pass

    def step(self, action):
        #action = torch.Tensor(action)
        #print(action)
        action = np.clip(action, min=-self.max_torque, max=self.max_torque) 
        # print(action.item())
        action_vector = action.numpy()
        #print(action_vector)
        response_step = self.stub.Step(observation_action_pb2.ActionData(action_index=action_vector, env_action=0))

        observation = response_step.observations
        reward = response_step.reward
        done = response_step.is_done

        clamp_speed = np.clip(observation[2], min=-self.max_speed, max=self.max_speed)
        observation[2] = clamp_speed

        infos = {
            "episode": None,
            "is_success": None,
        }

        return observation, reward, done, infos
        
    def reset(self, seed=42):
        
        response_reset = self.stub.Reset(observation_action_pb2.Empty())

        observation = response_reset.observations

        return observation
        
    def render(self, mode='human'):
        pass

    def terminate(self):
        self.stub.Terminate(observation_action_pb2.Empty())


'''
if __name__=='__main__':
    
    env_my = InvPendulumEnv(channel)
    for i in range(1000):
        obs_my, rew_my, done, _ = env_my.step(torch.tensor([8.0]))
        print(rew_my, obs_my, done)
    env_my.close()
    sys.exit()
    # env_my.reset()

    gym_obs = []
    gym_rew = []
    my_obs = []
    my_rew = []
    for i in range(1000):
        obs_my, rew_my, done, _ = env_my.step(torch.tensor([8.0]))
        obs, rew, done, _ = env.step(np.array([2.0]))
        env.render()
        gym_obs.append(obs)
        gym_rew.append(rew)
        my_obs.append(obs_my)
        my_rew.append(rew_my)
    
    env_my.close()
    
    gym_obs = np.array(gym_obs)
    gym_rew = np.array(gym_rew)
    my_obs = torch.stack(my_obs, dim=0).numpy()
    my_rew = np.array(my_rew)

    plt.subplot(1,4,1)
    plt.plot(gym_rew, label='Gym rewards')
    plt.plot(my_rew, label='My rewards')
    plt.subplot(1,4,2)
    plt.plot(gym_obs[:,0], label='gym obs0')
    plt.plot(my_obs[:,0], label='my obs0')
    plt.subplot(1,4,3)
    plt.plot(gym_obs[:,1], label='gym obs1')
    plt.plot(my_obs[:,1], label='my obs1')
    plt.subplot(1,4,4)
    plt.plot(gym_obs[:,2], label='gym obs2')
    plt.plot(my_obs[:,2], label='my obs2')
    plt.legend()
    plt.show()
'''