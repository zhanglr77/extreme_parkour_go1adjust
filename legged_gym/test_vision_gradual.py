#!/usr/bin/env python3
"""
逐步测试视觉蒸馏配置 - 找到不崩溃的参数组合
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import isaacgym
from legged_gym.envs import task_registry
import torch

def test_config(test_name, modifications):
    """测试特定配置"""
    print("\n" + "="*80)
    print(f"测试: {test_name}")
    print("="*80)
    
    env_cfg, _ = task_registry.get_cfgs(name="go1_highres_391")
    
    # 应用修改
    for key, value in modifications.items():
        parts = key.split('.')
        obj = env_cfg
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)
        print(f"  {key} = {value}")
    
    try:
        env, _ = task_registry.make_env(name="go1_highres_391", args=None, env_cfg=env_cfg)
        print(f"✅ 成功! 相机数: {len(env.cam_handles)}, depth_buffer: {env.depth_buffer.shape}")
        
        # 测试运行
        obs = env.get_observations()
        actions = torch.zeros(env.num_envs, env.num_actions, device=env.device)
        env.step(actions)
        print("✅ 运行测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

if __name__ == "__main__":
    configs = [
        # 测试1: heightfield地形 + 极少相机
        ("Heightfield + 2相机", {
            "terrain.mesh_type": "heightfield",
            "terrain.horizontal_scale": 0.05,  # 降低分辨率
            "depth.use_camera": True,
            "env.num_envs": 4,
            "depth.camera_num_envs": 2,  # 只创建2个相机
        }),
        
        # 测试2: heightfield + 降低相机分辨率
        ("Heightfield + 低分辨率相机", {
            "terrain.mesh_type": "heightfield",
            "terrain.horizontal_scale": 0.05,
            "depth.use_camera": True,
            "depth.original": (53, 30),  # 降低一半
            "depth.resized": (44, 29),
            "env.num_envs": 4,
            "depth.camera_num_envs": 4,
        }),
        
        # 测试3: trimesh + 极少相机
        ("Trimesh低分辨率 + 2相机", {
            "terrain.mesh_type": "trimesh",
            "terrain.horizontal_scale": 0.1,  # 10cm网格，降低很多
            "terrain.terrain_length": 10.0,   # 缩短
            "depth.use_camera": True,
            "env.num_envs": 4,
            "depth.camera_num_envs": 2,
        }),
        
        # 测试4: 平面 + 单个相机（最简单）
        ("平面 + 1相机", {
            "terrain.mesh_type": "plane",
            "depth.use_camera": True,
            "env.num_envs": 2,
            "depth.camera_num_envs": 1,
        }),
    ]
    
    results = []
    for name, mods in configs:
        success = test_config(name, mods)
        results.append((name, success))
        if success:
            print(f"\n🎉 找到可行配置: {name}")
            break  # 找到第一个成功的就停止
    
    print("\n" + "="*80)
    print("测试总结:")
    print("="*80)
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status}: {name}")
