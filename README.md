# GodotRPCGym

A Server Client Architecture for training reinforcement learning (RL) agents.
One can design a Simulation Environment in GODOT (game engine) and use Pytorch Baseline-3 RL library to train the agent.
Under the hood the Godot uses the libtorch and boost to write the simulation state and read the actions via a shared memory buffer (GymGodot: https://github.com/lupoglaz/GodotAIGym.git)
A RPC server (that bridges the Godot and Python RL agent) written in C++ reads the shared memory using the boost lib and communicates with a RPC client written in Python (the RL trainer).
The data is serialized using Protocol buffers.

Installation:
1. Compile the Godot Engine with the GodotSharedMemory module
    - place libtorch and boost library inside GodotSharedMemory folder and change the SCSub folder paths accordingly
3. CMake the RPC server
4. Spin up the RPC client
5. Test with the Existing Godot Environments

THIS PROJECT IS STILL UNDER DEVELOPMENT 

![](smart_creep.gif)

