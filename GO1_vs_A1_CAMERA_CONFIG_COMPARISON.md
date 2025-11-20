# Go1 vs A1 相机配置对比

## 📋 概览

| 项目 | Go1 | A1 | 说明 |
|------|-----|-----|------|
| **有相机配置** | ✅ 是 | ❌ 否 | Go1针对视觉蒸馏进行了配置 |
| **配置位置** | `go1_gap_highres_config.py` | 无 | A1没有专门的相机配置 |
| **集成深度相机** | ✅ 是 | ❌ 否 | Go1专为视觉任务优化 |

---

## 🔍 详细对比

### Go1 相机配置 (legged_gym/envs/go1/go1_gap_highres_config.py)

```python
class depth( LeggedRobotCfg.depth ):
    """深度相机配置（用于后续视觉蒸馏）"""
    use_camera = False              # 初始训练关闭，蒸馏时启用
    camera_num_envs = 192           # 视觉蒸馏时使用192个环境
    camera_terrain_num_rows = 10    # 地形行数
    camera_terrain_num_cols = 40    # 地形列数
    
    # 相机安装位置（相对于base_link）
    position = [0.27, 0, 0.03]      # x=27cm前, y=0中心, z=3cm高
    angle = [0, -10]                # roll=0, pitch=-10度
    
    # 分辨率参数
    original = (106, 60)            # 原始分辨率
    resized = (87, 58)              # 缩放后分辨率
    horizontal_fov = 87             # 水平视场角87度
    
    # 深度传感范围
    near_clip = 0.01                # 近距离截断1cm
    far_clip = 5.0                  # 远距离截断5m
    dis_noise = 0.0                 # 深度噪声
    
    # 图像裁剪
    crop_top_bottom = [0, 10]       # 上下裁剪10像素
    crop_left_right = [0, 19]       # 左右裁剪19像素
```

### A1 相机配置

**A1没有专门的相机配置。** A1使用基类配置：

```python
# 来自 LeggedRobotCfg.depth（base_config中的默认配置）
class depth:
    use_camera = False
    camera_num_envs = 192
    camera_terrain_num_rows = 10
    camera_terrain_num_cols = 20    # ← A1用20列，Go1用40列
    
    position = [0.27, 0, 0.03]      # 相同
    angle = [-5, 5]                 # ← A1 pitch范围不同
    
    original = (106, 60)            # 相同
    resized = (87, 58)              # 相同
    horizontal_fov = 87             # 相同
    
    near_clip = 0                   # ← A1从0开始，Go1从0.01开始
    far_clip = 2                    # ← A1最远2m，Go1最远5m
    dis_noise = 0.0                 # 相同
    
    buffer_len = 2                  # ← A1有缓冲长度，Go1无
    scale = 1
    invert = True
    
    update_interval = 5
```

---

## 📊 参数对比详解

### 1. **地形配置 (camera_terrain)**

| 参数 | Go1 | A1 | 影响 |
|------|-----|-----|------|
| `camera_terrain_num_rows` | 10 | 10 | 相同 |
| `camera_terrain_num_cols` | 40 | 20 | **Go1的地形宽度是A1的2倍** |

**含义**: 
- Go1在视觉蒸馏中会训练更宽的地形（40列）
- A1只支持20列地形宽度
- 这反映了Go1针对缝隙跳跃的特殊优化

### 2. **相机位置 (position)**

| 参数 | Go1 | A1 | 说明 |
|------|-----|-----|------|
| x (前后) | 0.27 m | 0.27 m | 相同，都在机器人前方27cm |
| y (左右) | 0 m | 0 m | 相同，都在中心 |
| z (高度) | 0.03 m | 0.03 m | **相同高度** |

**含义**: Go1和A1的相机安装位置完全相同

### 3. **相机角度 (angle)**

| 参数 | Go1 | A1 | 说明 |
|------|-----|-----|------|
| roll (翻滚) | 0° | -5° | Go1更直，A1稍微左倾 |
| pitch (俯仰) | -10° | 5° | **差异最大！** |

**含义**:
- **Go1**: pitch = -10°（明显向下看）
- **A1**: pitch = 5°（向上看）
- Go1配置用于看缝隙（向下），A1配置用于看远处（向上）

### 4. **深度范围**

| 参数 | Go1 | A1 | 用途 |
|------|-----|-----|------|
| `near_clip` | 0.01 m | 0 m | 最近距离（1cm vs 0cm）|
| `far_clip` | 5.0 m | 2.0 m | **最远距离差2.5倍** |

**含义**:
- Go1能看更远（5m），适合高速运动的长距离规划
- A1看距离短（2m），适合近距离感知

### 5. **缓冲区**

| 参数 | Go1 | A1 | 说明 |
|------|-----|-----|------|
| `buffer_len` | ❌ 无 | 2 | A1有缓冲，Go1无 |
| `update_interval` | ❌ 无 | 5 | A1每5步更新一次 |

**含义**: A1的配置在base_config中定义更完整

---

## 🔧 物理和硬件差异

### Go1 相机配置的原因

Go1的相机配置专门针对以下特点优化：

1. **高速运动** 
   - far_clip = 5m（看得远）
   - 需要提前预判地形

2. **缝隙跳跃**
   - angle pitch = -10°（向下看）
   - 需要看清脚下的缝隙
   - camera_terrain_num_cols = 40（宽地形）

3. **高度灵活性**
   - 可动态启用/禁用相机（use_camera = False/True）
   - 支持两阶段训练（base policy + vision distillation）

### A1 相机配置的差异

A1的相机配置更通用：

1. **常规运动**
   - far_clip = 2m（足够）
   - 不需要极长的前瞻

2. **缓坡地形**
   - angle pitch = 5°（向上看）
   - 看远处地形
   - camera_terrain_num_cols = 20（标准宽度）

3. **简单视觉**
   - buffer_len = 2（有缓冲平滑）
   - update_interval = 5（定期更新）

---

## 📁 配置文件结构

```
legged_gym/envs/
├── base/
│   └── legged_robot_config.py       ← 基础配置（包含默认depth）
│
├── a1/
│   ├── a1_config.py                 ← A1基础，无depth重写
│   ├── a1_gap_config.py             ← A1缝隙，无depth重写
│   └── a1_parkour_config.py         ← A1parkour，无depth重写
│       （所有A1配置都继承base的depth）
│
└── go1/
    ├── go1_config.py                ← Go1基础，无depth重写
    ├── go1_gap_config.py            ← Go1缝隙，无depth重写
    └── go1_gap_highres_config.py    ← ✨ 新增depth自定义配置
        （专为高分辨率和视觉蒸馏优化）
```

---

## 🎯 为什么Go1有特殊的相机配置

### 原始设计目的

Go1 `go1_gap_highres_config.py` 是为了支持**两阶段训练**：

```
第一阶段 (Base Policy)
  ├─ 使用: Scandots (697点)
  ├─ 目标: 学习缝隙跳跃基础策略
  └─ 配置: use_camera = False
  
第二阶段 (Vision Distillation)
  ├─ 使用: Scandots + 深度相机
  ├─ 目标: 用视觉增强策略性能
  └─ 配置: use_camera = True
  │        --use_camera 命令行启用
  └─ 相机参数:
       • 向下看缝隙 (pitch = -10°)
       • 看得很远 (far_clip = 5m)
       • 宽地形支持 (40列)
```

### A1为什么没有

A1的设计目标：
- 学习通用越野能力
- 使用Scandots就足够
- 不专注于极限缝隙跳跃
- 因此不需要特殊的视觉配置

---

## 🔄 如果要给A1添加相机配置

如果想让A1也支持视觉蒸馏，可以创建 `a1_gap_vision_config.py`：

```python
from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

class A1GapVisionCfg(LeggedRobotCfg):
    class init_state(LeggedRobotCfg.init_state):
        # ... A1初始状态 ...
    
    class depth(LeggedRobotCfg.depth):
        # 针对A1的相机优化
        use_camera = False
        camera_num_envs = 192
        camera_terrain_num_rows = 10
        camera_terrain_num_cols = 40  # 增加到40以支持宽地形
        
        # 根据A1的尺寸调整
        position = [0.25, 0, 0.03]    # A1体型可能需要调整
        angle = [0, -15]              # 更向下看
        
        far_clip = 3.0                # A1用3m（折中）
        near_clip = 0.01
        # ... 其他参数 ...

class A1GapVisionCfgPPO(LeggedRobotCfgPPO):
    # ... PPO超参数 ...
```

---

## ✅ 总结

| 方面 | 说明 |
|------|------|
| **Go1有相机配置吗** | ✅ 是，在 `go1_gap_highres_config.py` 中 |
| **A1有相机配置吗** | ❌ 否，只用base的默认配置 |
| **为什么不同** | Go1针对视觉蒸馏优化，A1使用通用配置 |
| **关键差异** | pitch角度、深度范围、地形宽度 |
| **主要原因** | Go1用于高难度缝隙跳跃，需要向下看；A1用于通用越野，看远处 |
| **可以扩展吗** | ✅ 可以，为A1添加自定义相机配置 |

---

## 🔗 相关文件位置

1. **Go1深度相机配置**
   - 路径: `legged_gym/legged_gym/envs/go1/go1_gap_highres_config.py`
   - 行数: 212-233行

2. **Base深度相机配置**
   - 路径: `legged_gym/legged_gym/envs/base/legged_robot_config.py`
   - 行数: 89-111行

3. **A1配置文件（无相机配置）**
   - 路径: `legged_gym/legged_gym/envs/a1/a1_*.py`
   - 特点: 都继承base的depth类，无覆盖

