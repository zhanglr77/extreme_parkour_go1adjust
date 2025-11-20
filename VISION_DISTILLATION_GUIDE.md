# 视觉蒸馏指南 - 摄像头调整与深度画面预览

## 📋 概述

本指南说明如何在进行视觉蒸馏（Vision Distillation）训练前，通过预览摄像头深度画面来调整摄像头角度，确保摄像头能看到缝隙但看不到机器人本体。

---

## 🎥 当前摄像头配置

### 配置位置
- **文件**: `legged_gym/legged_gym/envs/go1/go1_gap_highres_config.py`
- **基类**: `legged_gym/legged_gym/envs/base/legged_robot_config.py`

### 当前参数 (go1_gap_highres_config.py)

```python
class depth(LeggedRobotCfg.depth):
    """深度相机配置（用于后续视觉蒸馏）"""
    use_camera = False          # ⚠️ 当前关闭，需要改为True来启用
    camera_num_envs = 192       # 摄像头环境数量
    camera_terrain_num_rows = 10  # 地形行数
    camera_terrain_num_cols = 40  # 地形列数
    
    # 相对于base_link的位置 [x, y, z]
    position = [0.27, 0, 0.03]  # x=27cm前, y=0(中心), z=3cm上
    
    # 相机角度 [roll, pitch]
    angle = [0, -10]             # roll=0, pitch=-10度（向下看）
    
    # 分辨率
    original = (106, 60)          # 原始分辨率
    resized = (87, 58)            # 缩放后分辨率
    horizontal_fov = 87           # 水平视场角（度）
    
    # 深度范围
    near_clip = 0.01              # 近距离截断（1cm）
    far_clip = 5.0                # 远距离截断（5m）
    dis_noise = 0.0               # 深度噪声
    crop_top_bottom = [0, 10]     # 上下裁剪像素
    crop_left_right = [0, 19]     # 左右裁剪像素
```

---

## ✅ 预览摄像头深度画面的方法

### 方法1: 用play脚本实时预览（推荐）

#### 步骤1: 启用摄像头并运行play脚本

在go1_gap_highres_config.py中启用摄像头：

```python
class depth(LeggedRobotCfg.depth):
    use_camera = True  # ✅ 改为True
    # ... 其他配置保持不变
```

#### 步骤2: 运行play脚本预览

```bash
cd legged_gym
# 使用训练好的模型进行可视化
python legged_gym/scripts/play.py \
    --task=go1_highres \
    --proj_name=parkour_new \
    --exptid=go1_highres_697scan_2terrain \
    --checkpoint=12500 \
    --use_camera
```

#### 步骤3: 观察深度画面

- Isaac Gym窗口会显示深度图像
- 图像显示：黑色=远距离，白色=近距离
- 观察缝隙是否清晰可见，机器人本体是否过度占据画面

---

### 方法2: 创建专用的深度预览脚本（推荐用于调试）

创建文件 `legged_gym/legged_gym/scripts/preview_depth.py`：

```python
"""
深度相机预览脚本 - 用于调整摄像头角度
"""

from legged_gym import LEGGED_GYM_ROOT_DIR
import os
import isaacgym
from legged_gym.envs import *
from legged_gym.utils import get_args, task_registry
import torch
import cv2
import numpy as np
from time import time

def preview_depth(args):
    """实时预览摄像头深度画面"""
    
    # 获取配置
    env_cfg, train_cfg = task_registry.get_cfgs(name=args.task)
    
    # 启用摄像头
    env_cfg.depth.use_camera = True
    env_cfg.depth.camera_num_envs = 4  # 只用4个环境来加快速度
    
    # 创建环境
    env, _ = task_registry.make_env(
        name=args.task, 
        args=args, 
        env_cfg=env_cfg
    )
    
    print("🎥 开始深度相机预览")
    print(f"相机位置: {env_cfg.depth.position}")
    print(f"相机角度: {env_cfg.depth.angle}")
    print(f"分辨率: {env_cfg.depth.resized}")
    print(f"视场角: {env_cfg.depth.horizontal_fov}°")
    print("\n按 'q' 退出, 'a' 增大pitch角, 'd' 减小pitch角")
    print("按 'w' 增大position[2](Z), 's' 减小position[2]")
    print("按 'e' 增大position[0](X), 'c' 减小position[0]\n")
    
    # 加载策略（可选，可以直接观看随机行为）
    policy = None
    try:
        train_cfg.runner.resume = True
        ppo_runner, train_cfg, log_pth = task_registry.make_alg_runner(
            log_root=f"logs/{args.proj_name}/{args.exptid}",
            env=env,
            name=args.task,
            args=args,
            train_cfg=train_cfg,
            return_log_dir=True
        )
        policy = ppo_runner.get_inference_policy(device=env.device)
        print("✅ 已加载训练策略\n")
    except:
        print("⚠️  未找到训练策略，显示随机动作\n")
    
    obs = env.get_observations()
    actions = torch.zeros(env.num_envs, 12, device=env.device)
    
    # 预览循环
    for i in range(1000):
        if policy is not None:
            actions = policy(obs.detach())
        else:
            actions = torch.randn(env.num_envs, 12, device=env.device) * 0.2
        
        obs, _, rews, dones, infos = env.step(actions.detach())
        
        # 每10步显示一次深度图像
        if i % 10 == 0 and hasattr(env, 'depth_buffer'):
            depth_images = env.depth_buffer[:4, -1]  # 最后一帧，前4个环境
            
            for env_idx, depth_img in enumerate(depth_images):
                # 转换为numpy并归一化
                depth_np = depth_img.cpu().numpy().astype(np.float32)
                depth_norm = 255 * (1 - np.clip(depth_np / 5.0, 0, 1))  # 归一化到0-255
                depth_rgb = cv2.applyColorMap(depth_norm.astype(np.uint8), cv2.COLORMAP_JET)
                
                cv2.imshow(f'Depth Camera - Env {env_idx}', depth_rgb)
        
        # 处理键盘输入来动态调整
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('a'):
            env_cfg.depth.angle[1] += 1  # 增大pitch角
            print(f"Pitch角: {env_cfg.depth.angle[1]}°")
        elif key == ord('d'):
            env_cfg.depth.angle[1] -= 1  # 减小pitch角
            print(f"Pitch角: {env_cfg.depth.angle[1]}°")
        elif key == ord('w'):
            env_cfg.depth.position[2] += 0.01  # 增大Z
            print(f"高度(Z): {env_cfg.depth.position[2]:.2f}m")
        elif key == ord('s'):
            env_cfg.depth.position[2] -= 0.01  # 减小Z
            print(f"高度(Z): {env_cfg.depth.position[2]:.2f}m")
        elif key == ord('e'):
            env_cfg.depth.position[0] += 0.01  # 增大X
            print(f"前后(X): {env_cfg.depth.position[0]:.2f}m")
        elif key == ord('c'):
            env_cfg.depth.position[0] -= 0.01  # 减小X
            print(f"前后(X): {env_cfg.depth.position[0]:.2f}m")
    
    cv2.destroyAllWindows()
    print("\n✅ 深度相机预览已关闭")
    print(f"\n最终摄像头配置:")
    print(f"  位置: {env_cfg.depth.position}")
    print(f"  角度: {env_cfg.depth.angle}")
    print(f"\n将以上配置复制到 go1_gap_highres_config.py")


if __name__ == '__main__':
    args = get_args()
    preview_depth(args)
```

运行预览脚本：

```bash
cd legged_gym
python legged_gym/scripts/preview_depth.py \
    --task=go1_highres \
    --proj_name=parkour_new \
    --exptid=go1_highres_697scan_2terrain \
    --checkpoint=12500
```

---

## 🎯 摄像头调整目标

### 理想的摄像头配置应该:

✅ **能看到的**:
- 缝隙前方和缝隙本身（关键！）
- 机器人前方 0.5-2.0m 的地面
- 地形的高低变化
- 前方障碍物

❌ **不应该看到**:
- 机器人本体（腿部、身体）
- 机器人的脚（会遮挡缝隙）
- 摄像头看不到的死角（背后）

---

## 📊 摄像头参数说明

### position [x, y, z]
- **x (0.27)**: 沿机器人前进方向距离 (单位: m)
  - 增加 → 摄像头向前
  - 减少 → 摄像头向后
  - 范围: 0.1-0.4m 比较合理

- **y (0)**: 左右位移 (单位: m)  
  - 0 = 中心
  - 正值 = 向右, 负值 = 向左

- **z (0.03)**: 高度 (单位: m)
  - 增加 → 摄像头向上
  - 减少 → 摄像头向下
  - 范围: 0-0.1m 比较合理

### angle [roll, pitch]
- **roll (0)**: 左右翻滚 (单位: 度)
  - 通常保持0

- **pitch (-10)**: 上下俯仰 (单位: 度)
  - 负值 = 向下看（通常需要）
  - 范围: -30 ~ 0度 比较合理
  - -10 是折中值

### 视场角 (horizontal_fov = 87°)
- 越大 → 看得更宽
- 越小 → 看得更窄但更清晰

---

## 🚀 视觉蒸馏训练流程

### 步骤1: 确认摄像头配置

确保 `go1_gap_highres_config.py` 中:

```python
class depth(LeggedRobotCfg.depth):
    use_camera = False  # ← 保持False用于base policy
    # 但确保其他参数(position, angle等)已设置好
```

### 步骤2: 训练base policy（已完成✅）

```bash
cd legged_gym
python legged_gym/scripts/train.py \
    --exptid=go1_highres_697scan_2terrain \
    --device cuda:0
```

> 现在已完成，获得了model_7500/10000/12500.pt

### 步骤3: 预览摄像头深度画面（调整摄像头）

```bash
# 临时启用摄像头
# 在 go1_gap_highres_config.py 改: use_camera = True

cd legged_gym
python legged_gym/scripts/play.py \
    --task=go1_highres \
    --proj_name=parkour_new \
    --exptid=go1_highres_697scan_2terrain \
    --checkpoint=12500 \
    --use_camera
```

> 观察深度图像，确认能看到缝隙，看不到本体
> 记下最终的position和angle值

### 步骤4: 更新配置

将最佳的摄像头参数更新到 `go1_gap_highres_config.py`:

```python
class depth(LeggedRobotCfg.depth):
    position = [0.27, 0, 0.03]  # 更新为最佳值
    angle = [0, -10]             # 更新为最佳值
    use_camera = False            # 保持False，在蒸馏时由--use_camera启用
```

### 步骤5: 启动视觉蒸馏训练

```bash
cd legged_gym
python legged_gym/scripts/train.py \
    --exptid=go1_highres_697scan_2terrain_distill \
    --device cuda:0 \
    --resume \
    --resumeid=go1_highres_697scan_2terrain \
    --delay \
    --use_camera
```

**参数说明**:
- `--exptid`: 新的实验ID（蒸馏版本）
- `--resume`: 从已有模型恢复
- `--resumeid`: 要恢复的base policy的ID（需要前缀匹配）
- `--delay`: 添加动作延迟
- `--use_camera`: 启用摄像头

### 步骤6: 玩耍蒸馏后的模型

```bash
python legged_gym/scripts/play.py \
    --exptid=go1_highres_697scan_2terrain_distill \
    --delay \
    --use_camera
```

---

## 🔧 常见问题调整

### 问题1: 摄像头看到了机器人本体

**原因**: position[2]（高度）太低，或position[0]（前后）位置不对

**解决**:
```python
# 尝试增加高度
position = [0.27, 0, 0.05]  # 从0.03改为0.05

# 或调整前后位置
position = [0.35, 0, 0.03]  # 从0.27改为0.35，摄像头更靠前
```

### 问题2: 看不到缝隙或看得不清楚

**原因**: pitch角不对，或position[0]过近/过远

**解决**:
```python
# 增大向下看的角度
angle = [0, -15]  # 从-10改为-15，更俯视

# 或调整前后距离
position = [0.25, 0, 0.03]  # 更靠近缝隙
```

### 问题3: 视野太窄或太宽

**原因**: horizontal_fov 不合适

**解决**:
```python
# 增大视野
horizontal_fov = 100  # 从87改为100

# 或减小视野
horizontal_fov = 70   # 从87改为70，更集中
```

---

## 📝 推荐的调整工作流

1. **第一次预览**: 用现有参数运行play，查看深度画面
2. **记录观察**: 注意机器人本体、缝隙的相对位置
3. **微调参数**: 每次改一个参数，间隔30秒观察变化
4. **找到最佳值**: 能清楚看到缝隙，看不到本体
5. **验证**: 运行较长时间（5-10分钟）确保稳定
6. **更新配置**: 将最佳值写入config文件
7. **开始蒸馏**: 使用最终配置进行视觉蒸馏训练

---

## ✨ 总结

**你现在可以**:
- ✅ 查看摄像头深度画面：使用play脚本加`--use_camera`
- ✅ 调整摄像头角度：修改position和angle参数
- ✅ 实时优化：边看边调，找到最佳配置
- ✅ 进行视觉蒸馏：在最优配置下启动蒸馏训练

**关键要点**:
1. base policy (已完成) → 用Scandots训练
2. 预览摄像头 → 调整position和angle
3. 视觉蒸馏 → 用摄像头作为额外输入重新训练
4. 最终模型 → 结合Scandots和摄像头输入

---

**下一步**: 准备好调整摄像头参数后，就可以启动视觉蒸馏训练了！

