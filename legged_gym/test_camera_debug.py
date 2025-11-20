#!/usr/bin/env python3
"""
调试相机崩溃问题 - 尝试不同渲染模式
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import isaacgym
from isaacgym import gymapi
import torch

print("="*80)
print("Isaac Gym 相机调试")
print("="*80)

# 创建 gym 实例
gym = gymapi.acquire_gym()

# 测试不同的 sim_params
test_configs = [
    ("Headless + CPU", {"use_gpu": False, "headless": True}),
    ("Headless + GPU", {"use_gpu": True, "headless": True}),
    ("非Headless + GPU", {"use_gpu": True, "headless": False}),
]

for name, config in test_configs:
    print(f"\n{'='*80}")
    print(f"测试: {name}")
    print(f"{'='*80}")
    
    try:
        # 创建 sim_params
        sim_params = gymapi.SimParams()
        sim_params.physx.use_gpu = config["use_gpu"]
        sim_params.use_gpu_pipeline = config["use_gpu"]
        
        # 创建 sim
        if config["use_gpu"]:
            compute_device = 0
            graphics_device = 0 if not config["headless"] else -1
        else:
            compute_device = -1
            graphics_device = -1
        
        print(f"  compute_device: {compute_device}")
        print(f"  graphics_device: {graphics_device}")
        
        sim = gym.create_sim(compute_device, graphics_device, gymapi.SIM_PHYSX, sim_params)
        
        if sim is None:
            print(f"  ❌ 无法创建 sim")
            continue
        
        print(f"  ✅ Sim 创建成功")
        
        # 创建地面
        plane_params = gymapi.PlaneParams()
        gym.add_ground(sim, plane_params)
        
        # 创建环境
        env = gym.create_env(sim, gymapi.Vec3(-1, -1, 0), gymapi.Vec3(1, 1, 1), 1)
        print(f"  ✅ 环境创建成功")
        
        # 尝试创建相机
        camera_props = gymapi.CameraProperties()
        camera_props.width = 106
        camera_props.height = 60
        camera_props.horizontal_fov = 70.0
        
        camera_handle = gym.create_camera_sensor(env, camera_props)
        
        if camera_handle is None:
            print(f"  ❌ 相机创建失败")
            gym.destroy_sim(sim)
            continue
            
        print(f"  ✅ 相机创建成功")
        
        # 设置相机位置
        cam_pos = gymapi.Vec3(0.5, 0, 0.5)
        cam_target = gymapi.Vec3(0, 0, 0)
        gym.set_camera_location(camera_handle, env, cam_pos, cam_target)
        
        # 尝试运行模拟
        gym.prepare_sim(sim)
        gym.simulate(sim)
        gym.fetch_results(sim, True)
        
        print(f"  ✅ 模拟运行成功")
        
        # 尝试获取图像
        if not config["headless"]:
            gym.render_all_camera_sensors(sim)
            gym.start_access_image_tensors(sim)
            
            color_image = gym.get_camera_image(sim, env, camera_handle, gymapi.IMAGE_COLOR)
            depth_image = gym.get_camera_image(sim, env, camera_handle, gymapi.IMAGE_DEPTH)
            
            gym.end_access_image_tensors(sim)
            
            print(f"  ✅ 图像获取成功")
            print(f"     Color: {color_image.shape if hasattr(color_image, 'shape') else 'N/A'}")
            print(f"     Depth: {depth_image.shape if hasattr(depth_image, 'shape') else 'N/A'}")
        
        print(f"  🎉 {name} - 全部成功!")
        
        gym.destroy_sim(sim)
        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("结论:")
print("="*80)
print("如果只有 '非Headless + GPU' 成功，说明 Isaac Gym 在 headless 模式下")
print("相机功能有严重 bug，视觉蒸馏无法在云服务器上使用。")
print("="*80)
