# GodotRPCGym
rl grpc

A Server Client Architecture for training reinforcement learning (RL) agents.
One can design a Simulation Environment in GODOT (game engine) and use Pytorch Baseline-3 RL library to train the agent.
Under the hood the Godot uses the libtorch and boost to write the simulation state and read action via a shared memory (GymGodot: https://github.com/lupoglaz/GodotAIGym.git)
A RPC server (that bridges the Godot and Python RL agent) written in C++ reads this shared memory using boost lib and communicate with a RPC client written in Python (the RL trainer).
The data is serialized using Protocol buffers.

Installation:
1. Compile the Godot Engine with the GodotSharedMemory module
2. CMake the RPC server
3. Spin up the RPC client
4. Test with the Existing Godot Environments

THIS PROJECT IS STILL UNDER DEVELOPMENT 
