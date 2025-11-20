#!/bin/bash
# 修复 Isaac Gym 环境以匹配 PyTorch 1.10.0

echo "======================================================================"
echo "步骤 1: 清理旧的编译缓存"
echo "======================================================================"
rm -rf ~/.cache/torch_extensions/py38_cu121
rm -rf ~/.cache/torch_extensions/py38_cu113
echo "✅ 清理完成"

echo ""
echo "======================================================================"
echo "步骤 2: 重新编译 Isaac Gym"
echo "======================================================================"
cd ~/data/isaacgym/python
pip install -e . --force-reinstall --no-deps
echo "✅ Isaac Gym 重新编译完成"

echo ""
echo "======================================================================"
echo "步骤 3: 重新安装项目"
echo "======================================================================"
cd ~/data/extreme_parkour-server-training/legged_gym
pip install -e . --no-deps
cd ~/data/extreme_parkour-server-training/rsl_rl
pip install -e . --no-deps
echo "✅ 项目重新安装完成"

echo ""
echo "======================================================================"
echo "步骤 4: 验证环境"
echo "======================================================================"
cd ~/data/extreme_parkour-server-training/legged_gym
python check_environment.py

echo ""
echo "======================================================================"
echo "步骤 5: 测试相机功能"
echo "======================================================================"
python test_vision_gradual.py

echo ""
echo "======================================================================"
echo "✅ 修复完成！"
echo "======================================================================"
