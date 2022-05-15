# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function
import imp

import logging
from urllib import response
import os

import grpc
import observation_action_pb2
import observation_action_pb2_grpc

import torch
import gym
import numpy as np

from stable_baselines3 import DDPG, PPO, TD3
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.results_plotter import load_results, ts2xy
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.callbacks import BaseCallback


from CreeperEnv import CreeperEnv

# Save the best model callback class
class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq:
    :param log_dir: Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: Verbosity level.
    """
    def __init__(self, check_freq: int, log_dir: str, verbose: int = 1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), 'timesteps')
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-100:])
              if self.verbose > 0:
                print(f"Num timesteps: {self.num_timesteps}")
                print(f"Best mean reward: {self.best_mean_reward:.2f} - Last mean reward per episode: {mean_reward:.2f}")

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose > 0:
                    print(f"Saving new best model to {self.save_path}")
                  self.model.save(self.save_path)

        return True


# Globals
CHECKPOINT_DIR = "./checkpoints/ppo_creeper" # where to save the model at the end of training
LOG_DIR = "./ppo_creeper_tb" # tensorboard logger
N_ACTIONS = 3 # number of actions
N_OBSERVATIONS = 8 # number of observations

def run():
    # Open a grpc channel; change localhost to server IP when training in the cloud
    with grpc.insecure_channel('localhost:50051') as channel:
        # create the env
        env = CreeperEnv(channel, N_ACTIONS, N_OBSERVATIONS)
        
        # Instantiate the agent
        # action_noise = NormalActionNoise(mean=np.zeros(N_ACTIONS), sigma=1.0 * np.ones(N_ACTIONS))
        # model = TD3('MlpPolicy', env, verbose=1, tensorboard_log=LOG_DIR, action_noise=action_noise)
        model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=LOG_DIR)
        # Train the agent
        model.learn(total_timesteps=int(20_000)) #2e5

        # Save the agent and clear the memory
        model.save(CHECKPOINT_DIR)
        del model

        # Load and evaluate the model
        print("Loading the model")
        model = PPO.load(CHECKPOINT_DIR, env=env)
        mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)

        print("Mean reward: {}, Standard deviation reward: {}".format(mean_reward, std_reward))

        env.terminate()
        
        # To test the environment
        '''
        while True:
            obs, rew, done, _ = env.step(torch.tensor([3.0, 200.0, 0.5]))
            print(rew, obs, done)

            if done == 1:
                response_reset = env.reset()
                print(response_reset)
        '''

if __name__ == '__main__':
    logging.basicConfig()
    run()
