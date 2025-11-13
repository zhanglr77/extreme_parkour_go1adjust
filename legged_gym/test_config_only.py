#!/usr/bin/env python3
"""
本地配置验证脚本（无需GPU）

用途：
1. 验证配置文件是否正确
2. 验证观测维度计算
3. 验证地形参数设置
4. 预估显存占用

不需要：
- Isaac Gym
- GPU
- 完整的训练环境
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """测试配置加载"""
    print("="*60)
    print("测试1: 配置文件加载")
    print("="*60)
    
    try:
        from legged_gym.envs.go1.go1_gap_highres_test_config import (
            Go1GapHighResTestCfg, 
            Go1GapHighResTestCfgPPO
        )
        
        cfg = Go1GapHighResTestCfg()
        cfg_ppo = Go1GapHighResTestCfgPPO()
        
        print("✅ 测试配置加载成功")
        return cfg, cfg_ppo
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_dimensions(cfg):
    """测试维度计算"""
    print("\n" + "="*60)
    print("测试2: 观测维度验证")
    print("="*60)
    
    # 手动计算维度
    n_proprio = cfg.env.n_proprio
    n_scan = cfg.env.n_scan
    history_len = cfg.env.history_len
    n_priv = cfg.env.n_priv
    
    expected_obs = n_proprio + n_scan + n_proprio * history_len + n_priv
    actual_obs = cfg.env.num_observations
    
    print(f"维度分解：")
    print(f"  本体感知 (n_proprio): {n_proprio}")
    print(f"  Scandots (n_scan): {n_scan}")
    print(f"  历史 (n_proprio × history_len): {n_proprio} × {history_len} = {n_proprio * history_len}")
    print(f"  特权信息 (n_priv): {n_priv}")
    print(f"  ---")
    print(f"  期望总维度: {expected_obs}")
    print(f"  配置总维度: {actual_obs}")
    
    if expected_obs == actual_obs:
        print("✅ 维度计算正确")
        return True
    else:
        print(f"❌ 维度不匹配！差异: {actual_obs - expected_obs}")
        return False


def test_terrain_params(cfg):
    """测试地形参数"""
    print("\n" + "="*60)
    print("测试3: 地形参数验证")
    print("="*60)
    
    # 计算地形网格
    terrain_length = cfg.terrain.terrain_length
    terrain_width = cfg.terrain.terrain_width
    horizontal_scale = cfg.terrain.horizontal_scale
    
    vertices_x = int(terrain_length / horizontal_scale)
    vertices_y = int(terrain_width / horizontal_scale)
    total_vertices = vertices_x * vertices_y
    
    print(f"地形配置：")
    print(f"  尺寸: {terrain_length}m × {terrain_width}m")
    print(f"  网格分辨率: {horizontal_scale}m ({horizontal_scale*100:.0f}cm)")
    print(f"  网格数: {vertices_x} × {vertices_y} = {total_vertices:,}")
    
    # 验证课程学习参数
    max_level = cfg.terrain.max_init_terrain_level
    num_rows = cfg.terrain.num_rows
    difficulty = max_level / (num_rows - 1)
    
    print(f"\n课程学习：")
    print(f"  起始难度级别: {max_level}/{num_rows-1} = {difficulty:.3f}")
    print(f"  起始间隙大小：")
    
    # 计算最小间隙
    min_gap_cm = (0.02 + 0.03 * difficulty) * 100
    grid_cm = horizontal_scale * 100
    grid_units = min_gap_cm / grid_cm
    
    print(f"    fixed_gap_5cm: {min_gap_cm:.2f}cm  ⬅️ 最小")
    print(f"\n关键验证：")
    print(f"  最小间隙: {min_gap_cm:.2f}cm")
    print(f"  网格大小: {grid_cm:.0f}cm")
    print(f"  表示精度: {grid_units:.2f}个网格单元")
    
    if grid_units >= 1.0:
        print(f"✅ {grid_cm:.0f}cm网格可以表示{min_gap_cm:.2f}cm间隙")
        return True
    else:
        print(f"❌ {grid_cm:.0f}cm网格无法精确表示{min_gap_cm:.2f}cm间隙")
        return False


def estimate_memory(cfg):
    """预估显存占用"""
    print("\n" + "="*60)
    print("测试4: 显存占用预估")
    print("="*60)
    
    # 地形顶点
    terrain_length = cfg.terrain.terrain_length
    terrain_width = cfg.terrain.terrain_width
    horizontal_scale = cfg.terrain.horizontal_scale
    vertices = (terrain_length / horizontal_scale) * (terrain_width / horizontal_scale)
    terrain_mb = vertices * 4 * 3 / 1024 / 1024  # xyz, float32
    
    # 环境状态
    num_envs = cfg.env.num_envs
    num_obs = cfg.env.num_observations
    env_state_mb = num_envs * (
        num_obs * 4 / 1024 / 1024 +  # 观测
        20  # 其他状态（估算）
    )
    
    # 网络参数（估算）
    network_mb = 50
    
    # 总计
    total_mb = terrain_mb + env_state_mb + network_mb
    
    print(f"显存占用估算：")
    print(f"  地形顶点: {int(vertices):,}个 → ~{terrain_mb:.1f}MB")
    print(f"  环境状态: {num_envs}环境 × {num_obs}观测 → ~{env_state_mb:.0f}MB")
    print(f"  网络参数: ~{network_mb}MB")
    print(f"  ---")
    print(f"  预估总计: ~{total_mb:.0f}MB = {total_mb/1024:.2f}GB")
    
    if total_mb < 6000:  # 6GB以下安全
        print(f"✅ 适合8GB显存（留{8 - total_mb/1024:.1f}GB给系统）")
        return True
    elif total_mb < 7500:
        print(f"⚠️  显存紧张，可能需要7.5GB+")
        return True
    else:
        print(f"❌ 显存不足，需要{total_mb/1024:.1f}GB")
        return False


def test_full_config():
    """测试完整配置（用于服务器）"""
    print("\n" + "="*60)
    print("附加信息: 完整配置（服务器用）")
    print("="*60)
    
    try:
        from legged_gym.envs.go1.go1_gap_highres_config import Go1GapHighResCfg
        
        cfg_full = Go1GapHighResCfg()
        
        # 计算完整配置的显存需求
        vertices_full = (cfg_full.terrain.terrain_length / cfg_full.terrain.horizontal_scale) * \
                       (cfg_full.terrain.terrain_width / cfg_full.terrain.horizontal_scale)
        terrain_mb_full = vertices_full * 4 * 3 / 1024 / 1024
        env_mb_full = cfg_full.env.num_envs * 30  # 更多环境
        network_mb = 50
        total_mb_full = terrain_mb_full + env_mb_full + network_mb
        
        print(f"完整配置参数：")
        print(f"  环境数: {cfg_full.env.num_envs}")
        print(f"  地形: {cfg_full.terrain.terrain_length}m × {cfg_full.terrain.terrain_width}m")
        print(f"  网格: {cfg_full.terrain.horizontal_scale*100:.0f}cm")
        print(f"  顶点数: {int(vertices_full):,}")
        print(f"  预估显存: ~{total_mb_full/1024:.1f}GB")
        
        if total_mb_full > 8000:
            print(f"⚠️  完整配置需要 {total_mb_full/1024:.0f}GB+ 显存")
            print(f"   推荐GPU: RTX 3090 (24GB) / A100 (40GB)")
        
    except Exception as e:
        print(f"⚠️  无法加载完整配置: {e}")


def main():
    """主测试流程"""
    print("\n" + "🧪 "*15)
    print("Go1 高分辨率配置 - 本地验证测试")
    print("🧪 "*15 + "\n")
    
    print("本测试不需要GPU或Isaac Gym")
    print("仅验证配置文件的正确性")
    print()
    
    # 测试1: 加载配置
    cfg, cfg_ppo = test_config_loading()
    if cfg is None:
        print("\n❌ 测试失败：无法加载配置文件")
        return False
    
    # 测试2: 验证维度
    dim_ok = test_dimensions(cfg)
    
    # 测试3: 验证地形参数
    terrain_ok = test_terrain_params(cfg)
    
    # 测试4: 预估显存
    memory_ok = estimate_memory(cfg)
    
    # 附加信息
    test_full_config()
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    all_ok = dim_ok and terrain_ok and memory_ok
    
    if all_ok:
        print("✅ 所有测试通过！")
        print("\n下一步：")
        print("  1. 在本地运行完整测试（需要Isaac Gym）：")
        print("     ./test_local.sh")
        print()
        print("  2. 或者直接在服务器上训练（推荐）：")
        print("     python scripts/train.py --task=go1_highres \\")
        print("         --exptid=go1_highres_3cmgrid \\")
        print("         --run_name=highres_$(date +%Y%m%d)")
        return True
    else:
        print("❌ 部分测试失败，请检查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
