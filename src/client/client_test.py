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

import logging
from tkinter.tix import Tree
from urllib import response

import grpc
import observation_action_pb2
import observation_action_pb2_grpc

import numpy as np
import math

# No gym testing
def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = observation_action_pb2_grpc.RLCStub(channel)
        
        while True:
            # action_vector = np.random.uniform(0, 5, 6)
            action_1 = np.random.uniform(-250.0, 250.0, 1)
            action_2 = np.random.uniform(-250.0, 250.0, 1)
            action_3 = np.random.uniform(-math.pi, math.pi, 1)
            
            action_vector = [action_1, action_2, action_3]
            #print(action_vector)
            response_step = stub.Step(observation_action_pb2.ActionData(action_index=action_vector, env_action=0))

            observation = response_step.observations
            print(observation)
            reward = response_step.reward
            done = response_step.is_done

            if done == 1:
                print(done)
                response_reset = stub.Reset(observation_action_pb2.Empty())
                print(response_reset)


        

if __name__ == '__main__':
    logging.basicConfig()
    run()
