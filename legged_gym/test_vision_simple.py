#!/usr/bin/env python3
"""
测试视觉蒸馏 - 使用简化地形
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

# ⭐ 必须先导入isaacgym，再导入torch
import isaacgym
from legged_gym.envs import task_registry
from legged_gym import LEGGED_GYM_ROOT_DIR
import torch

def test_vision():
    # 加载391配置
    env_cfg, train_cfg = task_registry.get_cfgs(name="go1_highres_391")
    
    # ⭐ 临时修改为平面地形测试
    print("原始地形类型:", env_cfg.terrain.mesh_type)
    env_cfg.terrain.mesh_type = 'plane'
    print("修改后地形类型:", env_cfg.terrain.mesh_type)
    
    # 启用相机
    env_cfg.depth.use_camera = True
    env_cfg.env.num_envs = 4
    
    print(f"\n配置:")
    print(f"  num_envs: {env_cfg.env.num_envs}")
    print(f"  use_camera: {env_cfg.depth.use_camera}")
    print(f"  camera_num_envs: {env_cfg.depth.camera_num_envs}")
    print(f"  mesh_type: {env_cfg.terrain.mesh_type}")
    
    try:
        print("\n开始创建环境...")
        env, _ = task_registry.make_env(name="go1_highres_391", args=None, env_cfg=env_cfg)
        print("✅ 环境创建成功!")
        
        print(f"实际创建的相机数量: {len(env.cam_handles)}")
        print(f"depth_buffer shape: {env.depth_buffer.shape}")
        
        # 测试几步
        print("\n测试运行几步...")
        obs = env.get_observations()
        for i in range(5):
            actions = torch.zeros(env.num_envs, env.num_actions, device=env.device)
            obs, _, _, _, _ = env.step(actions)
            print(f"  Step {i+1}: obs shape = {obs.shape}")
        
        print("\n✅ 测试完全成功!")
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vision()
    sys.exit(0 if success else 1)
