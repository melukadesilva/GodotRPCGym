from stable_baselines3 import DDPG, PPO
import torch

model = DDPG.load("./checkpoints/ddpg_inv_pendulum_200k")
print(model.policy.actor)

model.policy.actor.eval()
inp = torch.rand(1, 3)

traced_script_module = torch.jit.trace(model.policy.actor, inp)
traced_script_module.save("ddpg_actor.jit")
