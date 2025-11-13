# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause

"""
Go1 高分辨率配置 - 本地测试版本（8GB显存）

这是一个轻量级配置，用于在本地验证：
1. 配置文件是否正确
2. 训练脚本是否能运行
3. 地形生成是否正常
4. 网络架构是否匹配

⚠️ 注意：这只是测试配置，不用于实际训练！
真正训练请在服务器上使用 go1_gap_highres_config.py
"""

from legged_gym.envs.go1.go1_gap_highres_config import Go1GapHighResCfg, Go1GapHighResCfgPPO

class Go1GapHighResTestCfg(Go1GapHighResCfg):
    """
    Go1高分辨率测试配置
    
    修改要点：
    1. 极少的环境数（16-32个）
    2. 缩小的地形尺寸
    3. 保持相同的scandots和观测维度
    4. 保持相同的网格分辨率（验证精度）
    """
    
    class env(Go1GapHighResCfg.env):
        # ⭐ 关键：极少的环境数（适合8GB显存）
        num_envs = 4  # 从32降到16（更安全）
        
        # ⚠️ 保持与完整版完全相同的观测配置（从Go1GapHighResCfg继承）
        # 已自动继承：
        # - n_scan = 391
        # - n_proprio = 47
        # - history_len = 50
        # - n_priv = 18
        # - n_priv_latent = 50
        # - num_observations = 2856
        
        # 不需要重新定义，直接继承完整配置的所有观测参数
    
    class terrain(Go1GapHighResCfg.terrain):
        # ⭐ 缩小地形尺寸（减少内存）
        terrain_length = 6.0   # 从8m降到6m（进一步减少）
        terrain_width = 2.0    # 从3m降到2m（进一步减少）
        
        # ⚠️ 保持相同的网格分辨率（这是关键验证点）
        horizontal_scale = 0.03  # 3cm网格（与完整版一致）
        vertical_scale = 0.005
        
        # 减少地形复杂度
        num_rows = 5   # 从10降到5（减少难度级别）
        num_cols = 20  # 从40降到20（减少地形类型）
        
        # 课程学习配置（保持一致）
        curriculum = True
        max_init_terrain_level = 2  # 从更简单的难度开始测试
        
        # 地形分布（保持一致，验证地形生成）
        terrain_dict = {
            "smooth slope": 0.,
            "rough slope up": 0.0,
            "rough slope down": 0.0,
            "rough stairs up": 0.,
            "rough stairs down": 0.,
            "discrete": 0.,
            "stepping stones": 0.0,
            "gaps": 0.,
            "smooth flat": 0.0,
            "pit": 0.0,
            "wall": 0.0,
            "platform": 0.0,
            "large stairs up": 0.,
            "large stairs down": 0.,
            "parkour": 0.0,
            "parkour_hurdle": 0.0,
            "parkour_flat": 0.0,
            "parkour_step": 0.0,
            "parkour_gap": 0.33,
            "demo": 0.0,
            "fixed_gap_5cm": 0.33,
            "fixed_gap_15cm": 0.34,
        }
        terrain_proportions = list(terrain_dict.values())
        
        border_size = 5
        gap_size = [0.03, 0.18]
        height = [0.02, 0.06]
    
    class depth(Go1GapHighResCfg.depth):
        """深度相机配置（测试时不使用）"""
        use_camera = False
        camera_num_envs = 0  # 测试时不使用相机


class Go1GapHighResTestCfgPPO(Go1GapHighResCfgPPO):
    """
    PPO训练参数 - 测试版本
    
    修改要点：
    1. 更短的训练步数（验证流程）
    2. 更频繁的日志输出
    3. 保持网络架构不变（验证维度）
    """
    
    class algorithm(Go1GapHighResCfgPPO.algorithm):
        # 保持网络架构（验证观测维度）
        value_loss_coef = 1.0
        use_clipped_value_loss = True
        clip_param = 0.2
        entropy_coef = 0.01
        num_learning_epochs = 5
        num_mini_batches = 4  # mini_batches = 32 envs / 4 = 8 envs per batch
        learning_rate = 1.e-3
        schedule = 'adaptive'
        gamma = 0.99
        lam = 0.95
        desired_kl = 0.01
        max_grad_norm = 1.
    
    class runner(Go1GapHighResCfgPPO.runner):
        # ⭐ 测试用的训练参数
        policy_class_name = 'ActorCritic'
        algorithm_class_name = 'PPO'
        num_steps_per_env = 24  # 每环境步数
        max_iterations = 100  # ⭐ 只训练100次（测试流程，约5分钟）
        save_interval = 50    # 每50次保存一次
        
        # 实验配置
        experiment_name = 'parkour_test'
        run_name = 'go1_highres_local_test'
        
        # 日志配置（更频繁）
        log_interval = 5  # 每5次迭代输出一次
        
        # 评估配置
        record_video = False
        record_interval = -1


# 打印配置信息
if __name__ == "__main__":
    import sys
    cfg = Go1GapHighResTestCfg()
    cfg_ppo = Go1GapHighResTestCfgPPO()
    
    print("\n" + "="*60)
    print("Go1 高分辨率测试配置 - 本地8GB显存验证")
    print("="*60 + "\n")
    
    print("📊 环境配置：")
    print(f"  环境数: {cfg.env.num_envs} （vs 完整版3072）")
    print(f"  Scandots: {cfg.env.n_scan}点 （与完整版一致）")
    print(f"  观测维度: {cfg.env.num_observations} （与完整版一致）")
    print()
    
    print("🗺️ 地形配置：")
    print(f"  地形尺寸: {cfg.terrain.terrain_length}m × {cfg.terrain.terrain_width}m （测试版缩小）")
    print(f"  网格分辨率: {cfg.terrain.horizontal_scale}m ({cfg.terrain.horizontal_scale*100:.0f}cm) ⭐ 与完整版一致")
    vertices = (cfg.terrain.terrain_length / cfg.terrain.horizontal_scale) * \
               (cfg.terrain.terrain_width / cfg.terrain.horizontal_scale)
    print(f"  地形顶点: {int(vertices):,}")
    print()
    
    print("💾 显存预估：")
    terrain_mb = vertices * 4 * 3 / 1024 / 1024
    env_mb = cfg.env.num_envs * 10  # 每环境约10MB
    network_mb = 50  # 网络参数约50MB
    total_mb = terrain_mb + env_mb + network_mb
    print(f"  地形数据: ~{terrain_mb:.1f}MB")
    print(f"  环境状态: ~{env_mb:.0f}MB ({cfg.env.num_envs}环境)")
    print(f"  网络参数: ~{network_mb}MB")
    print(f"  总计: ~{total_mb:.0f}MB = {total_mb/1024:.2f}GB")
    print(f"  {'✅ 适合8GB显存' if total_mb < 6000 else '❌ 可能显存不足'}")
    print()
    
    print("⚡ 训练配置：")
    print(f"  最大迭代: {cfg_ppo.runner.max_iterations} （测试用，实际需25000+）")
    print(f"  每环境步数: {cfg_ppo.runner.num_steps_per_env}")
    print(f"  日志间隔: {cfg_ppo.runner.log_interval}")
    print(f"  预估测试时长: ~5-10分钟")
    print()
    
    print("🎯 测试目标：")
    print("  ✓ 验证配置文件加载正确")
    print("  ✓ 验证地形生成（3cm网格）")
    print("  ✓ 验证观测维度（2856维）")
    print("  ✓ 验证训练流程可运行")
    print("  ✓ 验证网络架构匹配")
    print()
    
    print("⚠️ 重要提示：")
    print("  这只是测试配置，不用于实际训练！")
    print("  确认测试通过后，使用完整配置在服务器上训练：")
    print("    python train.py --task=go1_highres")
    print()
    
    print("="*60)
