# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# 简化版play脚本 - 只创建单个5cm缝隙地形，避免显存溢出

from legged_gym import LEGGED_GYM_ROOT_DIR
import os
import code

import isaacgym
from legged_gym.envs import *
from legged_gym.utils import  get_args, export_policy_as_jit, task_registry, Logger
from isaacgym import gymtorch, gymapi, gymutil
import numpy as np
import torch
import cv2
from collections import deque
import statistics
import faulthandler
from copy import deepcopy
import matplotlib.pyplot as plt
from time import time, sleep
from legged_gym.utils import webviewer

def get_load_path(root, load_run=-1, checkpoint=-1, model_name_include="model"):
    if checkpoint==-1:
        models = [file for file in os.listdir(root) if model_name_include in file]
        models.sort(key=lambda m: '{0:0>15}'.format(m))
        model = models[-1]
        checkpoint = model.split("_")[-1].split(".")[0]
    return model, checkpoint

def play(args):
    if args.web:
        web_viewer = webviewer.WebViewer()
    faulthandler.enable()
    exptid = args.exptid
    log_pth = "logs/{}/".format(args.proj_name) + args.exptid

    env_cfg, train_cfg = task_registry.get_cfgs(name=args.task)
    
    # ⭐ 简化配置 - 创建2个环境（2×1地形布局）
    env_cfg.env.num_envs = 2  # 2个环境对应2×1地形
    env_cfg.env.episode_length_s = 60
    env_cfg.commands.resampling_time = 60
    
    # ⭐ 地形配置 - 创建2×1的5cm缝隙+25cm平台地形（避免除零错误）
    env_cfg.terrain.num_rows = 2  # 2行避免除零错误：row0(难度0), row1(难度1)
    env_cfg.terrain.num_cols = 1  # 只有1列
    env_cfg.terrain.terrain_length = 8.0  # 增加到8m（更长的地形）
    env_cfg.terrain.terrain_width = 4.0   # 增加到4m（标准宽度）
    env_cfg.terrain.horizontal_scale = 0.05  # 5cm网格与训练一致
    env_cfg.terrain.vertical_scale = 0.005   # 垂直分辨率
    env_cfg.terrain.border_size = 5
    env_cfg.terrain.max_init_terrain_level = 0  # 固定难度0
    env_cfg.terrain.height = [0.02, 0.02]
    
    # ⭐ 只使用fixed_gap_5cm地形类型
    env_cfg.terrain.terrain_dict = {
        "smooth slope": 0., 
        "rough slope up": 0.0,
        "rough slope down": 0.0,
        "rough stairs up": 0., 
        "rough stairs down": 0., 
        "discrete": 0., 
        "stepping stones": 0.0,
        "gaps": 0., 
        "smooth flat": 0,
        "pit": 0.0,
        "wall": 0.0,
        "platform": 0.,
        "large stairs up": 0.,
        "large stairs down": 0.,
        "parkour": 0.0,
        "parkour_hurdle": 0.0,
        "parkour_flat": 0.,
        "parkour_step": 0.0,
        "parkour_gap": 0.0,        
        "demo": 0.0,
        "fixed_gap_5cm": 1.0,      # 100%使用5cm固定缝隙
        "fixed_gap_15cm": 0.0      
    }
    
    env_cfg.terrain.terrain_proportions = list(env_cfg.terrain.terrain_dict.values())
    env_cfg.terrain.curriculum = False  # 不启用课程学习
    env_cfg.terrain.max_difficulty = False  # 不使用最高难度模式
    
    # ⭐ 确保机器人分布在不同地形块上
    env_cfg.terrain.max_init_terrain_level = 1  # 允许初始化到row 0和row 1
    
    # 其他配置保持与原play.py一致
    if args.nodelay:
        env_cfg.domain_rand.action_delay_view = 0
        
    env_cfg.depth.angle = [0, 1]
    env_cfg.noise.add_noise = True
    env_cfg.domain_rand.randomize_friction = True
    env_cfg.domain_rand.push_robots = False
    env_cfg.domain_rand.push_interval_s = 6
    env_cfg.domain_rand.randomize_base_mass = False
    env_cfg.domain_rand.randomize_base_com = False
    
    # ⭐ 禁用调试可视化避免足部绘制错误
    env_cfg.viewer.debug_viz = False

    depth_latent_buffer = []
    
    # prepare environment
    env, _ = task_registry.make_env(name=args.task, args=args, env_cfg=env_cfg)
    
    # ⭐ 手动设置机器人在不同地形块：env0→row0, env1→row1
    import torch
    env.terrain_levels[0] = 0  # 第一个机器人在row0（难度0，2cm间隙）
    env.terrain_levels[1] = 1  # 第二个机器人在row1（难度1，5cm间隙）
    env.terrain_types[:] = 0   # 所有机器人都用col0（fixed_gap_5cm）
    
    # 重新计算环境原点和目标
    env.env_origins[:] = env.terrain_origins[env.terrain_levels, env.terrain_types]
    env.env_class[:] = env.terrain_class[env.terrain_levels, env.terrain_types]
    temp = env.terrain_goals[env.terrain_levels, env.terrain_types]
    last_col = temp[:, -1].unsqueeze(1)
    env.env_goals[:] = torch.cat((temp, last_col.repeat(1, env.cfg.env.num_future_goal_obs, 1)), dim=1)[:]
    env.cur_goals = env._gather_cur_goals()
    env.next_goals = env._gather_cur_goals(future=1)
    
    # 重置机器人位置到正确的地形块
    env.reset_idx(torch.arange(env.num_envs, device=env.device))
    
    obs = env.get_observations()

    if args.web:
        web_viewer.setup(env)

    # load policy
    train_cfg.runner.resume = True
    ppo_runner, train_cfg, log_pth = task_registry.make_alg_runner(log_root = log_pth, env=env, name=args.task, args=args, train_cfg=train_cfg, return_log_dir=True)
    
    if args.use_jit:
        path = os.path.join(log_pth, "traced")
        model, checkpoint = get_load_path(root=path, checkpoint=args.checkpoint)
        path = os.path.join(path, model)
        print("Loading jit for policy: ", path)
        policy_jit = torch.jit.load(path, map_location=env.device)
    else:
        policy = ppo_runner.get_inference_policy(device=env.device)
    estimator = ppo_runner.get_estimator_inference_policy(device=env.device)
    if env.cfg.depth.use_camera:
        depth_encoder = ppo_runner.get_depth_encoder_inference_policy(device=env.device)

    actions = torch.zeros(env.num_envs, 12, device=env.device, requires_grad=False)
    infos = {}
    infos["depth"] = env.depth_buffer.clone().to(ppo_runner.device)[:, -1] if ppo_runner.if_depth else None

    print("🎯 开始可视化训练好的Go1模型...")
    print(f"📊 地形配置: 1×1单个5cm缝隙地形")
    print(f"🤖 环境数量: {env.num_envs}")
    print(f"🗺️  地形尺寸: {env_cfg.terrain.terrain_length}m × {env_cfg.terrain.terrain_width}m")
    print(f"📏 网格分辨率: {env_cfg.terrain.horizontal_scale*100:.0f}cm")
    
    for i in range(10*int(env.max_episode_length)):
        if args.use_jit:
            if env.cfg.depth.use_camera:
                if infos["depth"] is not None:
                    depth_latent = torch.ones((env_cfg.env.num_envs, 32), device=env.device)
                    actions, depth_latent = policy_jit(obs.detach(), True, infos["depth"], depth_latent)
                else:
                    depth_buffer = torch.ones((env_cfg.env.num_envs, 58, 87), device=env.device)
                    actions, depth_latent = policy_jit(obs.detach(), False, depth_buffer, depth_latent)
            else:
                obs_jit = torch.cat((obs.detach()[:, :env_cfg.env.n_proprio+env_cfg.env.n_priv], obs.detach()[:, -env_cfg.env.history_len*env_cfg.env.n_proprio:]), dim=1)
                actions = policy(obs_jit)
        else:
            if env.cfg.depth.use_camera:
                if infos["depth"] is not None:
                    obs_student = obs[:, :env.cfg.env.n_proprio].clone()
                    obs_student[:, 6:8] = 0
                    depth_latent_and_yaw = depth_encoder(infos["depth"], obs_student)
                    depth_latent = depth_latent_and_yaw[:, :-2]
                    yaw = depth_latent_and_yaw[:, -2:]
                obs[:, 6:8] = 1.5*yaw
                    
            else:
                depth_latent = None
            
            if hasattr(ppo_runner.alg, "depth_actor"):
                actions = ppo_runner.alg.depth_actor(obs.detach(), hist_encoding=True, scandots_latent=depth_latent)
            else:
                actions = policy(obs.detach(), hist_encoding=True, scandots_latent=depth_latent)
            
        obs, _, rews, dones, infos = env.step(actions.detach())
        if args.web:
            web_viewer.render(fetch_results=True,
                        step_graphics=True,
                        render_all_camera_sensors=True,
                        wait_for_page_load=True)
        
        # 显示两个机器人的状态
        if i % 50 == 0:  # 每50步输出一次状态
            print(f"⏱️  时间: {env.episode_length_buf[0].item() / 50:.1f}s")
            print(f"🤖 机器人0 (row0-2cm): 速度 {env.base_lin_vel[0, 0].item():.2f}m/s, 奖励 {rews[0].item():.2f}")
            print(f"🤖 机器人1 (row1-5cm): 速度 {env.base_lin_vel[1, 0].item():.2f}m/s, 奖励 {rews[1].item():.2f}")
            print("-" * 60)
        

if __name__ == '__main__':
    EXPORT_POLICY = False
    RECORD_FRAMES = False
    MOVE_CAMERA = False
    args = get_args()
    play(args)