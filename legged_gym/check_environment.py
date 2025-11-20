#!/usr/bin/env python3
"""
检查当前环境版本
"""
import sys
import torch
import platform

print("="*80)
print("环境诊断信息")
print("="*80)

print(f"\n【Python】")
print(f"  版本: {sys.version}")
print(f"  可执行文件: {sys.executable}")

print(f"\n【PyTorch】")
print(f"  版本: {torch.__version__}")
print(f"  CUDA 编译版本: {torch.version.cuda}")
print(f"  CUDA 可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  CUDA 设备数: {torch.cuda.device_count()}")
    print(f"  当前设备: {torch.cuda.current_device()}")
    print(f"  设备名称: {torch.cuda.get_device_name(0)}")
    print(f"  设备显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

print(f"\n【系统】")
print(f"  操作系统: {platform.system()} {platform.release()}")
print(f"  CPU架构: {platform.machine()}")

print(f"\n【Isaac Gym】")
try:
    import isaacgym
    print(f"  已安装 ✅")
    print(f"  路径: {isaacgym.__file__}")
except ImportError as e:
    print(f"  未安装 ❌: {e}")

print(f"\n【关键包版本】")
packages = ['numpy', 'opencv-python', 'tensorboard', 'wandb', 'setuptools']
for pkg in packages:
    try:
        module = __import__(pkg.replace('-', '_').split('_')[0])
        version = getattr(module, '__version__', 'unknown')
        print(f"  {pkg}: {version}")
    except ImportError:
        print(f"  {pkg}: 未安装")

print("\n" + "="*80)
print("【诊断结果】")
print("="*80)

torch_version = torch.__version__
cuda_version = torch.version.cuda

if torch_version.startswith('1.10') and cuda_version == '11.3':
    print("✅ 环境正确 - 使用原始推荐版本")
    print("   这是最稳定的配置，应该可以正常使用相机")
elif torch_version.startswith('1.13') and cuda_version == '11.6':
    print("⚠️  环境可接受 - 使用较新版本")
    print("   这个版本通常也能工作，相机功能应该正常")
elif torch_version.startswith('2.') or cuda_version.startswith('12'):
    print("❌ 环境不兼容 - 版本太新")
    print(f"   PyTorch {torch_version} + CUDA {cuda_version} 与 Isaac Gym 不兼容")
    print("   这会导致相机功能崩溃 (Segmentation fault)")
    print("\n   推荐修复方案:")
    print("   conda create -n parkour_fix python=3.8")
    print("   conda activate parkour_fix")
    print("   pip install torch==1.10.0+cu113 torchvision==0.11.1+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html")
    print("   cd ~/data/isaacgym/python && pip install -e .")
    print("   cd ~/data/extreme-parkour-server-training/legged_gym && pip install -e .")
    print("   cd ~/data/extreme-parkour-server-training/rsl_rl && pip install -e .")
else:
    print(f"⚠️  环境未知 - PyTorch {torch_version} + CUDA {cuda_version}")
    print("   建议使用原始推荐版本: PyTorch 1.10.0 + CUDA 11.3")

print("="*80)
