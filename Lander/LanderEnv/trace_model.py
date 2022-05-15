from stable_baselines3 import DDPG, PPO
import torch

model = DDPG.load("./ddpg_lunar")
print(model.policy.actor)

model.policy.actor.eval()
inp = torch.rand(1, 21)

traced_script_module = torch.jit.trace(model.policy.actor, inp)
traced_script_module.save("ddpg_actor.jit")
