#!/bin/bash
# 有头模式训练脚本 - 用于可视化验证地形配置
# 减少并行环境数量以避免显存不足

# 推荐配置：
# - 512个环境：适合大部分GPU，可以看到地形分布
# - 256个环境：显存较少时使用
# - 128个环境：显存非常紧张时使用

# 使用方法：
# bash train_gap_headless.sh [num_envs] [exptid]
# 例如：bash train_gap_headless.sh 512 go1_gap_test

NUM_ENVS=${1:-512}  # 默认512个环境
EXPTID=${2:-go1_gap_headless_$(date +%Y%m%d_%H%M%S)}

echo "================================================"
echo "训练配置："
echo "  任务: go1_gap"
echo "  并行环境数: $NUM_ENVS"
echo "  实验ID: $EXPTID"
echo "  模式: 无头模式（headless）"
echo "  地形: parkour_gap(33%) + fixed_gap_5cm(33%) + fixed_gap_15cm(34%)"
echo "================================================"

cd /home/zhanglr/Downloads/extreme-parkour/legged_gym

python legged_gym/scripts/train.py \
    --task=go1_gap \
    --num_envs=$NUM_ENVS \
    --headless \
    --proj_name=parkour_new \
    --exptid=$EXPTID

echo "训练完成！日志位置: logs/parkour_new/$EXPTID"
