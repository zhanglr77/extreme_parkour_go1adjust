# 深度相机显示脚本使用指南

## 概述

创建了两个新的评估脚本，用于观察相机深度图像：

1. **play2_showdepth.py** - 在5cm固定缝隙地形上运行，并显示深度图
2. **play3_showdepth.py** - 在15cm固定缝隙地形上运行，并显示深度图

## 关键特性

✅ **完整复制原有配置** - play2和play3的所有地形、环境设置保持一致
✅ **深度图实时显示** - 运行时会弹出"Depth Camera View"窗口
✅ **仅用于观察** - 深度图仅用于显示，不影响策略控制
✅ **原有功能完整** - 机器狗的行动仍由Scandots传感器控制

## 运行命令

### 5cm缝隙地形 + 深度图显示
```bash
cd /home/zhanglr/Downloads/extreme-parkour-server-training/legged_gym
python legged_gym/scripts/play2_showdepth.py \
    --task=go1_highres \
    --num_envs=4 \
    --proj_name=parkour_new \
    --exptid=go1_highres_697scan_2terrain \
    --checkpoint=12500
```

### 15cm缝隙地形 + 深度图显示
```bash
cd /home/zhanglr/Downloads/extreme-parkour-server-training/legged_gym
python legged_gym/scripts/play3_showdepth.py \
    --task=go1_highres \
    --num_envs=4 \
    --proj_name=parkour_new \
    --exptid=go1_highres_697scan_2terrain \
    --checkpoint=12500
```

## 深度图配置参数

当前深度相机配置（从go1_gap_highres_config.py）：

```python
位置: [0.355, 0, 0.065]
  - X: 355mm（前方）
  - Y: 0mm（中心）
  - Z: 65mm（高度）

角度: [25, 25]
  - Roll: 25°
  - Pitch: 25°（向下倾斜）

FOV: [86, 90] 水平视角
```

## 深度图显示说明

- **窗口名称**: "Depth Camera View (Robot 0)"
- **颜色映射**: TURBO（冷色=近，暖色=远）
- **更新频率**: 每帧更新
- **关闭方式**: 按Ctrl+C终止程序

## 原理

这两个脚本的工作流程：

1. **环境初始化** 
   - `env_cfg.depth.use_camera = True` 启用深度捕获
   - 环境内部自动捕获深度图到 `env.depth_buffer`

2. **策略推理**
   - 仅使用Scandots观测值推理动作
   - 不调用depth_encoder（模型未经vision distillation）
   - 深度图不影响控制

3. **深度图显示**
   - 每帧读取 `env.depth_buffer[0, -1]` 获取第一个机器人的深度图
   - 使用cv2显示，便于观察相机视角

## 什么时候使用这些脚本

✅ **使用时机**：
- 验证相机位置和角度是否合适
- 观察机器狗走路时能"看到"什么
- 检查深度图是否有黑影、遮挡等问题
- 为vision distillation（阶段2训练）做准备

❌ **不用这些脚本**：
- 与原play2.py/play3.py有相同的模型评估需求（用原版即可）
- 进行vision distillation训练（那时需要用--use_camera标志的train.py）

## 对比说明

| 特性 | play2.py | play2_showdepth.py |
|------|----------|-------------------|
| 地形 | 5cm缝隙 | 5cm缝隙 |
| 深度相机 | 关闭 | 启用（仅显示） |
| 策略控制 | Scandots | Scandots |
| 深度图显示 | ❌ | ✅ |
| 计算开销 | 低 | 中 |

## 故障排查

### 问题：深度图全黑
**原因**：相机配置在环境初始化时未正确应用
**解决**：检查go1_gap_highres_config.py中的depth配置是否正确

### 问题：运行缓慢
**原因**：深度图处理和显示增加了计算量
**解决**：降低环境数量 `--num_envs=2`，或在无GUI环境使用原play2.py

### 问题：窗口闪烁或不显示
**原因**：cv2显示在某些环境中有延迟
**解决**：这是正常的，继续运行程序，深度图应该会显示

## 下一步

视觉蒸馏训练（Vision Distillation - 阶段2）准备：

```bash
# 当确认相机位置合适后，运行vision distillation训练
python legged_gym/scripts/train.py \
    --task=go1_highres \
    --resume \
    --resumeid go1_highres_697scan_2terrain-xxx-xx \
    --use_camera \
    --delay
```

---

**创建日期**: November 15, 2025
**相机配置版本**: Go2标准配置
**脚本版本**: play2/play3派生版
