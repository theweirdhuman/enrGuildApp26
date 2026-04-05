import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque

class qLearningNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(4,80),
            nn.ReLU(),
            nn.Linear(80,2)
        )
        
    def forward(self, x):
        return self.net(x)
    
    
    
def training():
        
    env = gym.make('CartPole-v1')
    state = env.reset()[0]

    model = qLearningNet()
    optimizer = optim.Adam(model.parameters(),lr=0.0008)
    
    gamma = 0.99
    eps = 1
    epsDecay = 0.995
    
    
    for i in range(2500):
        eps = episodeTrain(env,model,optimizer,gamma,eps,i)
        eps = max(0.05, eps * epsDecay)

    env.close()
    torch.save(model.state_dict(),"cartpole_model.pth")
    
    
def episodeTrain(env,model,optimizer,gamma,eps,i):
    state = env.reset()[0]
    epsReward=0
    for j in range(500):
        stateTensor = torch.tensor(state, dtype = torch.float32)
        
        qVal = model(stateTensor)
        if random.random() < eps:
            action = env.action_space.sample()
        else:
            action = torch.argmax(qVal).item()
        
        nextState, reward, terminated, truncated, _ = env.step(action)
        epsReward+=reward
        with torch.no_grad():
            nextQ = model(torch.tensor(nextState, dtype = torch.float32))
            
        state = nextState
        
        done = terminated or truncated
        
        if done:
            target = reward            
        else:
            target = reward + gamma*torch.max(nextQ)
            
        loss = (qVal[action] - target)**2
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if done:
            print(f"episode {i}",epsReward)
            return eps
        
    return eps

def eval():
    env = gym.make('CartPole-v1',render_mode = 'human')
    
    model = qLearningNet()
    model.load_state_dict(torch.load("cartpole_model.pth"))
    model.eval()
    
    for i in range(10):
        epReward = 0
        state=env.reset()[0]
        while True:
            stateTensor = torch.tensor(state,dtype=torch.float32)
            
            with torch.no_grad():
                qVals = model(stateTensor)
                action = torch.argmax(qVals).item()
                
            state, reward, terminated, truncated, _ = env.step(action)
            epReward += reward
            if terminated or truncated:
                print(f"episode {i} reward",epReward)
                epReward = 0
                state=env.reset()[0]
                break
    
training()
eval()