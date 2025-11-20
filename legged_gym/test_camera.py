#!/usr/bin/env python3
"""
测试相机配置是否正确
"""
import sys
sys.path.append('.')

from legged_gym.envs import task_registry

# 加载391配置
env_cfg, train_cfg = task_registry.get_cfgs(name="go1_highres_391")

print("="*80)
print("配置信息:")
print(f"num_envs: {env_cfg.env.num_envs}")
print(f"use_camera: {env_cfg.depth.use_camera}")
print(f"camera_num_envs: {env_cfg.depth.camera_num_envs}")
print(f"camera_terrain_num_rows: {env_cfg.depth.camera_terrain_num_rows}")
print(f"camera_terrain_num_cols: {env_cfg.depth.camera_terrain_num_cols}")
print("="*80)

# 检查是否会创建过多相机
if env_cfg.depth.use_camera:
    print(f"\n⚠️ 启用相机模式")
    print(f"将为前 {env_cfg.depth.camera_num_envs} 个环境创建相机")
    print(f"总环境数: {env_cfg.env.num_envs}")
    
    if env_cfg.depth.camera_num_envs > env_cfg.env.num_envs:
        print(f"❌ 错误: camera_num_envs ({env_cfg.depth.camera_num_envs}) > num_envs ({env_cfg.env.num_envs})")
    else:
        print(f"✅ 正常: camera_num_envs <= num_envs")
else:
    print(f"\n✅ 相机未启用")

print("\n相机参数:")
print(f"位置: {env_cfg.depth.position}")
print(f"角度: {env_cfg.depth.angle}")
print(f"horizontal_fov: {env_cfg.depth.horizontal_fov}")
if hasattr(env_cfg.depth, 'vertical_fov'):
    print(f"vertical_fov: {env_cfg.depth.vertical_fov}")
