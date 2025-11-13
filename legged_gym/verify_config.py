#!/usr/bin/env python3
"""
配置文件语法检查（无依赖版本）

仅检查Python语法和基本参数，不导入任何库
"""

import ast
import os

def check_file_syntax(filepath):
    """检查文件语法"""
    print(f"检查文件: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ❌ 文件不存在")
        return False
    
    try:
        with open(filepath, 'r') as f:
            code = f.read()
            ast.parse(code)
        print(f"  ✅ 语法正确")
        return True
    except SyntaxError as e:
        print(f"  ❌ 语法错误: {e}")
        return False


def extract_config_values(filepath):
    """提取配置值（简单文本解析）"""
    values = {}
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # 提取关键参数
        if 'num_envs =' in line and not line.startswith('#'):
            try:
                val = line.split('=')[1].split('#')[0].strip()
                values['num_envs'] = int(val)
            except:
                pass
        
        if 'n_scan =' in line and not line.startswith('#'):
            try:
                val = line.split('=')[1].split('#')[0].strip()
                values['n_scan'] = int(val)
            except:
                pass
        
        if 'horizontal_scale =' in line and not line.startswith('#'):
            try:
                val = line.split('=')[1].split('#')[0].strip()
                values['horizontal_scale'] = float(val)
            except:
                pass
        
        if 'terrain_length =' in line and not line.startswith('#'):
            try:
                val = line.split('=')[1].split('#')[0].strip()
                values['terrain_length'] = float(val)
            except:
                pass
        
        if 'terrain_width =' in line and not line.startswith('#'):
            try:
                val = line.split('=')[1].split('#')[0].strip()
                values['terrain_width'] = float(val)
            except:
                pass
        
        if 'max_init_terrain_level =' in line and not line.startswith('#'):
            try:
                val = line.split('=')[1].split('#')[0].strip()
                values['max_init_terrain_level'] = int(val)
            except:
                pass
    
    return values


def main():
    print("\n" + "="*60)
    print("Go1配置文件验证 - 无依赖版本")
    print("="*60 + "\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查测试配置
    test_config = os.path.join(base_dir, 'legged_gym/envs/go1/go1_gap_highres_test_config.py')
    print("1️⃣  测试配置（本地8GB）")
    print("-" * 60)
    
    if check_file_syntax(test_config):
        values = extract_config_values(test_config)
        print("\n  关键参数:")
        for k, v in sorted(values.items()):
            print(f"    {k}: {v}")
        
        # 计算预估值
        if all(k in values for k in ['terrain_length', 'terrain_width', 'horizontal_scale']):
            vertices = int((values['terrain_length'] / values['horizontal_scale']) * \
                          (values['terrain_width'] / values['horizontal_scale']))
            memory_mb = vertices * 12 / 1024 / 1024 + values.get('num_envs', 32) * 25
            
            print(f"\n  预估:")
            print(f"    地形顶点: {vertices:,}")
            print(f"    显存需求: ~{memory_mb/1024:.1f}GB")
            
            if memory_mb < 6000:
                print(f"    ✅ 适合8GB显存")
            else:
                print(f"    ⚠️  可能需要更多显存")
    
    print()
    
    # 检查完整配置
    full_config = os.path.join(base_dir, 'legged_gym/envs/go1/go1_gap_highres_config.py')
    print("2️⃣  完整配置（服务器）")
    print("-" * 60)
    
    if check_file_syntax(full_config):
        values = extract_config_values(full_config)
        print("\n  关键参数:")
        for k, v in sorted(values.items()):
            print(f"    {k}: {v}")
        
        # 计算预估值
        if all(k in values for k in ['terrain_length', 'terrain_width', 'horizontal_scale']):
            vertices = int((values['terrain_length'] / values['horizontal_scale']) * \
                          (values['terrain_width'] / values['horizontal_scale']))
            memory_mb = vertices * 12 / 1024 / 1024 + values.get('num_envs', 3072) * 25
            
            # 课程学习分析
            if 'max_init_terrain_level' in values:
                difficulty = values['max_init_terrain_level'] / 9  # num_rows=10
                min_gap_cm = (0.02 + 0.03 * difficulty) * 100
                grid_cm = values['horizontal_scale'] * 100
                
                print(f"\n  预估:")
                print(f"    地形顶点: {vertices:,}")
                print(f"    显存需求: ~{memory_mb/1024:.1f}GB")
                print(f"    最小间隙: {min_gap_cm:.2f}cm")
                print(f"    网格大小: {grid_cm:.0f}cm")
                
                if grid_cm <= min_gap_cm:
                    print(f"    ✅ {grid_cm:.0f}cm网格可表示{min_gap_cm:.2f}cm间隙")
                else:
                    print(f"    ⚠️  网格可能太粗")
    
    print()
    print("="*60)
    print("总结")
    print("="*60)
    print("✅ 配置文件语法检查完成")
    print()
    print("如果想完整测试（需要Isaac Gym）：")
    print("  1. 本地简单测试: ./test_local.sh")
    print("  2. 服务器完整训练:")
    print("     python scripts/train.py --task=go1_highres")
    print()


if __name__ == "__main__":
    main()
