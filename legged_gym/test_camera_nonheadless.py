#!/usr/bin/env python3
"""
测试非headless模式下的相机
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import isaacgym
from legged_gym.envs import task_registry
import torch

env_cfg, _ = task_registry.get_cfgs(name="go1_highres_391")

# 最小配置
env_cfg.terrain.mesh_type = "plane"
env_cfg.depth.use_camera = True
env_cfg.env.num_envs = 2
env_cfg.depth.camera_num_envs = 1

print("尝试非headless模式...")
print("⚠️ 需要显示器支持!")

try:
    # 尝试不使用headless
    from legged_gym import LEGGED_GYM_ROOT_DIR
    from legged_gym.envs.go1.go1_gap_highres_391_config import Go1GapHighRes391Cfg
    from legged_gym.envs import LeggedRobot
    
    env = LeggedRobot(
        cfg=env_cfg,
        sim_params=None,
        physics_engine=isaacgym.gymapi.SIM_PHYSX,
        sim_device='cuda:0',
        headless=False  # 关键！
    )
    
    print("✅ 成功创建环境!")
    print(f"相机数: {len(env.cam_handles)}")
    
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()
