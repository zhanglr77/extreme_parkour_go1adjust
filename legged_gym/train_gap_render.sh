#!/bin/bash
# 有头模式训练脚本 - 可视化地形配置
# 大幅减少并行环境数量以避免显存不足

# 推荐配置（有头模式）：
# - 64个环境：可以看到地形，训练速度适中
# - 32个环境：显存较少时使用
# - 16个环境：最小配置，仅用于验证

# 使用方法：
# bash train_gap_render.sh [num_envs] [exptid]
# 例如：bash train_gap_render.sh 64 go1_gap_visual

NUM_ENVS=${1:-64}  # 默认64个环境（有头模式）
EXPTID=${2:-go1_gap_render_$(date +%Y%m%d_%H%M%S)}

echo "================================================"
echo "训练配置："
echo "  任务: go1_gap"
echo "  并行环境数: $NUM_ENVS"
echo "  实验ID: $EXPTID"
echo "  模式: 🎥 有头模式（可视化渲染）"
echo "  地形: parkour_gap(33%) + fixed_gap_5cm(33%) + fixed_gap_15cm(34%)"
echo "================================================"
echo "⚠️  注意：有头模式会打开渲染窗口，显存占用较高"
echo "================================================"

cd /home/zhanglr/Downloads/extreme-parkour/legged_gym

python legged_gym/scripts/train.py \
    --task=go1_gap \
    --num_envs=$NUM_ENVS \
    --proj_name=parkour_new \
    --exptid=$EXPTID

echo "训练完成！日志位置: logs/parkour_new/$EXPTID"
