#!/bin/bash
# 为 NVIDIA H20 GPU 安装兼容的 PyTorch 版本

echo "======================================================================"
echo "为 NVIDIA H20 (sm_90) 安装 PyTorch 2.0.1 + CUDA 11.8"
echo "======================================================================"

# 清理缓存
rm -rf ~/.cache/torch_extensions

# 安装 PyTorch 2.0.1 (最早支持较新GPU的稳定版)
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118

# 重新编译 Isaac Gym
echo ""
echo "重新编译 Isaac Gym..."
cd /root/data/isaacgym/python
pip install -e . --force-reinstall --no-deps

# 重新安装项目
echo ""
echo "重新安装项目..."
cd /root/data/extreme_parkour_go1adjust/legged_gym
pip install -e . --no-deps

cd /root/data/extreme_parkour_go1adjust/rsl_rl
pip install -e . --no-deps

echo ""
echo "======================================================================"
echo "✅ 安装完成！测试环境..."
echo "======================================================================"

cd /root/data/extreme_parkour_go1adjust/legged_gym
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Compute capability: {torch.cuda.get_device_capability(0)}')
"

echo ""
echo "现在测试相机..."
python test_vision_gradual.py
