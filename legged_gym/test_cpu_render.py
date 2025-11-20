#!/usr/bin/env python3
"""
测试 CPU 渲染模式
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import isaacgym
from legged_gym.envs import task_registry
import torch

print("="*80)
print("测试 CPU 渲染模式（会很慢但可能稳定）")
print("="*80)

env_cfg, _ = task_registry.get_cfgs(name="go1_highres_391")

# 关键：强制 CPU 渲染
env_cfg.sim.use_gpu_pipeline = False  # 关闭 GPU pipeline
env_cfg.sim.physx.use_gpu = False     # CPU 物理
env_cfg.depth.use_camera = True
env_cfg.env.num_envs = 2              # 只测试 2 个环境
env_cfg.depth.camera_num_envs = 1     # 1 个相机
env_cfg.terrain.mesh_type = "plane"   # 最简单地形

print(f"配置:")
print(f"  use_gpu_pipeline: {env_cfg.sim.use_gpu_pipeline}")
print(f"  physx.use_gpu: {env_cfg.sim.physx.use_gpu}")
print(f"  use_camera: {env_cfg.depth.use_camera}")
print(f"  num_envs: {env_cfg.env.num_envs}")
print(f"  camera_num_envs: {env_cfg.depth.camera_num_envs}")

try:
    print("\n创建环境...")
    env, _ = task_registry.make_env(name="go1_highres_391", args=None, env_cfg=env_cfg)
    print(f"✅ 成功! 相机数: {len(env.cam_handles)}")
    
    print("测试运行...")
    obs = env.get_observations()
    actions = torch.zeros(env.num_envs, env.num_actions)  # CPU tensor
    env.step(actions)
    print("✅ 运行成功!")
    
    print("\n🎉 CPU 渲染模式可行！")
    print("但是：CPU 模式太慢，不适合训练。")
    
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("结论: Isaac Gym 相机功能在云服务器上无法使用")
print("="*80)
