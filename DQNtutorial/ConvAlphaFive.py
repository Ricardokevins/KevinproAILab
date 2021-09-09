import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from Env import Environment
from Env import WIN_REWARD,SUCCESS_REWARD,FAILED_REWARD,LOSE_REWARD
from checkerboard import Checkerboard, BLACK_CHESSMAN, WHITE_CHESSMAN, offset, Point
from config import *
env = Environment()

# 超参数
BATCH_SIZE = 64
LR = 0.02                   # learning rate
EPSILON = 0.9               # 最优选择动作百分比
GAMMA = 0.9                 # 奖励递减参数
TARGET_REPLACE_ITER = 100   # Q 现实网络的更新频率
MEMORY_CAPACITY = 2000      # 记忆库大小

N_ACTIONS = env.action_space  # 杆子能做的动作
N_STATES = env.observation_space  # 杆子能获取的环境信息数

class Net(nn.Module):
    def __init__(self, ):
        super(Net, self).__init__()
        self.conv1=nn.Conv2d(1,3,5)
        #self.conv2=nn.Conv2d(3,1,3)
        self.out = nn.Linear(147, N_ACTIONS)
        self.out.weight.data.normal_(0, 0.1)   # initialization

    def forward(self, x):
        x = x.reshape( -1,1,Line_Points,Line_Points)
        x=F.max_pool2d(F.relu(self.conv1(x)),(2,2))
        #x=F.max_pool2d(F.relu(self.conv2(x)),(2,2))

        x = x.reshape(-1,147)
        actions_value = self.out(x)
        return actions_value



class DQN(object):
    def __init__(self):
        self.eval_net, self.target_net = Net(), Net()

        self.learn_step_counter = 0     # 用于 target 更新计时
        self.memory_counter = 0         # 记忆库记数
        self.memory = np.zeros((MEMORY_CAPACITY, N_STATES * 2 + 2))     # 初始化记忆库
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=LR)    # torch 的优化器
        self.loss_func = nn.MSELoss()   # 误差公式

    def choose_action(self, x):
        x = torch.unsqueeze(torch.FloatTensor(x), 0)
        # 这里只输入一个 sample
        if np.random.uniform() < EPSILON:   # 选最优动作
            actions_value = self.eval_net.forward(x)
            action = torch.max(actions_value, 1)[1].data.numpy()[0]     # return the argmax
        else:   # 选随机动作
            action = np.random.randint(0, N_ACTIONS)

        return action

    def store_transition(self, s, a, r, s_):
        transition = np.hstack((s, [a, r], s_))
        # 如果记忆库满了, 就覆盖老数据
        index = self.memory_counter % MEMORY_CAPACITY
        self.memory[index, :] = transition
        self.memory_counter += 1

    def learn(self):
        # target net 参数更新
        if self.learn_step_counter % TARGET_REPLACE_ITER == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())
        self.learn_step_counter += 1

        # 抽取记忆库中的批数据
        sample_index = np.random.choice(MEMORY_CAPACITY, BATCH_SIZE)
        b_memory = self.memory[sample_index, :]
        b_s = torch.FloatTensor(b_memory[:, :N_STATES])
        b_a = torch.LongTensor(b_memory[:, N_STATES:N_STATES+1].astype(int))
        b_r = torch.FloatTensor(b_memory[:, N_STATES+1:N_STATES+2])
        b_s_ = torch.FloatTensor(b_memory[:, -N_STATES:])

        # 针对做过的动作b_a, 来选 q_eval 的值, (q_eval 原本有所有动作的值)
        q_eval = self.eval_net(b_s).gather(1, b_a)  # shape (batch, 1)
        q_next = self.target_net(b_s_).detach()     # q_next 不进行反向传递误差, 所以 detach
        q_target = b_r + GAMMA * q_next.max(1)[0].reshape(b_r.shape[0],-1)   # shape (batch, 1)
        #print(q_target.shape)
        loss = self.loss_func(q_eval, q_target)

        # 计算, 更新 eval net
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss

dqn = DQN() # 定义 DQN 系统
smooth_life = 0

def print_state(state):
    index = 0
    print("=================================")
    for i in range(31):
        for j in range(31):
            print(state[index],end = "|")
            index += 1
        print('\n')
    print("=================================")

loss_sum = 0
for i_episode in range(40000):
    life = 0
    #print("Game: {}".format(i_episode))
    s = env.reset()
    if i_episode % 10 == 0:
        env.render()    # 显示实验动画
        print(loss_sum/(i_episode+1))
        print(round(smooth_life,4))
    while True:
        a = dqn.choose_action(s)
        # 选动作, 得到环境反馈
        s_, r, done = env.step(a)

        #print_state(s_)
        # 修改 reward, 使 DQN 快速学习
        # x, x_dot, theta, theta_dot = s_
        # r1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8
        # r2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5
        # r = r1 + r2

        # 存记忆
        dqn.store_transition(s, a, r, s_)

        if dqn.memory_counter > MEMORY_CAPACITY:
            loss = dqn.learn() # 记忆库满了就进行学习
            loss_sum += loss
        if done:    # 如果回合结束, 进入下回合
            smooth_life = smooth_life * 0.99 + life * 0.01
            
            #print("Ending")

            break
        
        life += 1
        s = s_
