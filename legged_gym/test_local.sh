#!/bin/bash
# 本地8GB显存测试脚本
# 用途：在本地快速验证配置和训练流程

echo "=========================================="
echo "Go1高分辨率配置 - 本地测试脚本"
echo "=========================================="
echo ""
echo "⚠️  本测试使用极少的环境数（32个）"
echo "    仅用于验证配置文件和训练流程"
echo "    实际训练请在服务器上使用完整配置"
echo ""

# 检查是否在正确的目录
if [ ! -f "legged_gym/__init__.py" ]; then
    echo "❌ 错误：请在 legged_gym 目录下运行此脚本"
    echo "   cd /path/to/extreme-parkour/legged_gym"
    exit 1
fi

echo "1️⃣  检查配置文件..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from legged_gym.envs.go1.go1_gap_highres_test_config import Go1GapHighResTestCfg, Go1GapHighResTestCfgPPO
    cfg = Go1GapHighResTestCfg()
    cfg_ppo = Go1GapHighResTestCfgPPO()
    print('✅ 配置文件加载成功')
    print(f'   环境数: {cfg.env.num_envs}')
    print(f'   Scandots: {cfg.env.n_scan}')
    print(f'   观测维度: {cfg.env.num_observations}')
    print(f'   地形网格: {cfg.terrain.horizontal_scale*100:.0f}cm')
except Exception as e:
    print(f'❌ 配置文件加载失败: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "2️⃣  启动测试训练（100次迭代，约5-10分钟）..."
echo ""
echo "命令："
echo "  python scripts/train.py --task=go1_highres_test --headless"
echo ""
echo "监控指标："
echo "  - 每5次迭代输出日志"
echo "  - 检查 mean_reward 是否在合理范围"
echo "  - 检查是否有错误/警告"
echo ""
read -p "按回车键开始测试... " -n 1 -r
echo ""

# 运行训练（捕获输出）
python scripts/train.py --task=go1_highres_test --headless 2>&1 | tee /tmp/go1_test_output.log

# 检查训练结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 测试完成！"
    echo "=========================================="
    echo ""
    echo "测试结果："
    
    # 提取关键信息
    if grep -q "mean_reward" /tmp/go1_test_output.log; then
        echo "✅ 训练循环正常运行"
        echo ""
        echo "最后几行日志："
        tail -n 20 /tmp/go1_test_output.log
    else
        echo "⚠️  未找到训练日志，请检查输出"
    fi
    
    echo ""
    echo "下一步："
    echo "  1. 检查日志文件: /tmp/go1_test_output.log"
    echo "  2. 如果测试通过，在服务器上运行完整训练："
    echo "     python scripts/train.py --task=go1_highres \\"
    echo "         --exptid=go1_highres_3cmgrid \\"
    echo "         --run_name=highres_\$(date +%Y%m%d)"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ 测试失败"
    echo "=========================================="
    echo ""
    echo "可能的原因："
    echo "  1. 显存不足（需要约1-2GB）"
    echo "  2. Isaac Gym未正确安装"
    echo "  3. 配置文件有误"
    echo ""
    echo "检查日志: /tmp/go1_test_output.log"
    echo ""
    exit 1
fi
