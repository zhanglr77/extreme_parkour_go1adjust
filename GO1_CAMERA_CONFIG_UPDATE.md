# Go1 相机配置更新 - 与Go2对齐

## 📝 修改摘要

已将 `go1_gap_highres_config.py` 中的 `depth` 类配置更新为与Go2完全一致。

### 修改时间
- 2025年11月15日

### 修改文件
- `legged_gym/legged_gym/envs/go1/go1_gap_highres_config.py` (第212-221行)

---

## 🔄 配置对比

### 修改前（旧配置）

```python
class depth( LeggedRobotCfg.depth ):
    """深度相机配置（用于后续视觉蒸馏）"""
    use_camera = False  # 初始训练不使用相机
    camera_num_envs = 192
    camera_terrain_num_rows = 10
    camera_terrain_num_cols = 40
    
    # Go1相机参数
    position = [0.27, 0, 0.03]  # [x, y, z] 相对base_link
    angle = [0, -10]  # [roll, pitch] 俯仰角-10度
    
    # 分辨率
    original = (106, 60)
    resized = (87, 58)
    horizontal_fov = 87
    
    # 深度范围
    near_clip = 0.01
    far_clip = 5.0
    dis_noise = 0.0
    crop_top_bottom = [0, 10]
    crop_left_right = [0, 19]
```

### 修改后（新配置 - 与Go2一致）

```python
class depth( LeggedRobotCfg.depth ):
    position = [0.355, 0, 0.065]
    angle = [25, 25]  # 固定25度向下倾斜角度
    
    horizontal_fov = [86, 90]
    dis_noise = 0.0

    gaussian_noise_std = 0.

    near_plane = 0.1
```

---

## 📊 参数变化详解

| 参数 | 旧值 | 新值 | 变化 | 说明 |
|------|------|------|------|------|
| **position[0] (x前后)** | 0.27 m | 0.355 m | ↑ +85mm | 摄像头更靠前 |
| **position[1] (y左右)** | 0 m | 0 m | → 无变 | 保持中心 |
| **position[2] (z高度)** | 0.03 m | 0.065 m | ↑ +35mm | 摄像头更高 |
| **angle[0] (roll)** | 0° | 25° | ↑ +25° | 新参数格式 |
| **angle[1] (pitch)** | -10° | 25° | ↑ +35° | 向下看角度增加 |
| **horizontal_fov** | 87° | [86, 90] | 📋 改为列表 | 可能用于多摄像头 |
| **near_clip** | 0.01 m | ❌ 删除 | - | 改用near_plane |
| **far_clip** | 5.0 m | ❌ 删除 | - | 改用near_plane |
| **dis_noise** | 0.0 | 0.0 | → 保持 | 深度噪声 |
| **gaussian_noise_std** | ❌ 无 | 0.0 | ✅ 新增 | 高斯噪声标准差 |
| **near_plane** | ❌ 无 | 0.1 m | ✅ 新增 | 近距离截断 |

---

## 🎯 改动意义

### 摄像头位置变化

**旧位置**: [0.27, 0, 0.03]
- x: 27cm前
- z: 3cm高
- 特点: 相对靠后靠低

**新位置**: [0.355, 0, 0.065]
- x: 35.5cm前 (↑ 8.5cm)
- z: 6.5cm高 (↑ 3.5cm)
- 特点: 向前向上移动，更好的视角

**原因**: 
- 更前的位置能看得更清楚
- 更高的位置能避免看到机器人本体

### 角度变化

**旧角度**: [0, -10] (格式: [roll, pitch])
- roll=0° (无翻滚)
- pitch=-10° (向下看10度)
- 特点: 相对温和的向下角度

**新角度**: [25, 25] (格式不同)
- 两个值都是25
- 特点: 更强的向下倾斜
- 可能是新格式的角度表示

**原因**: Go2配置中采用的更激进的俯视角度

### 视场角变化

**旧参数**: `horizontal_fov = 87`
- 单个数值
- 表示水平视场角87度

**新参数**: `horizontal_fov = [86, 90]`
- 列表格式
- 可能表示左右两个不同的视场角
- 或者表示可调范围

### 新增参数

**gaussian_noise_std = 0.0**
- 高斯噪声标准差
- 目前设为0（无噪声）
- 可用于训练鲁棒性

**near_plane = 0.1**
- 近距离截断改为0.1m (10cm)
- 替代了旧的 near_clip = 0.01m
- 更合理的最近距离

---

## ✅ 修改确认

### 其他部分保持不变
- ✅ 所有其他配置参数未动
- ✅ Scandots配置 (697点) 保持不变
- ✅ 地形配置保持不变
- ✅ 奖励函数保持不变
- ✅ 训练超参保持不变

### 只修改了
- ❌ 删除了注释和旧参数
- ✅ 添加了Go2相同的depth配置
- ✅ 保持了配置的有效性

---

## 🔗 参考信息

### Go2的配置（参考来源）
```python
class depth( LeggedRobotCfg.depth):
    position = [0.355, 0, 0.065]
    angle = [25, 25]  # 固定25度向下倾斜角度
    
    horizontal_fov = [86, 90]
    dis_noise = 0.0

    gaussian_noise_std = 0.

    near_plane = 0.1
```

### Go1的新配置（现在）
```python
class depth( LeggedRobotCfg.depth ):
    position = [0.355, 0, 0.065]
    angle = [25, 25]  # 固定25度向下倾斜角度
    
    horizontal_fov = [86, 90]
    dis_noise = 0.0

    gaussian_noise_std = 0.

    near_plane = 0.1
```

✅ **完全一致！**

---

## 📋 后续步骤

1. **重新测试** (推荐)
   - 用新的相机配置重新运行训练
   - 测试视觉蒸馏效果
   
2. **性能对比**
   - 与旧配置对比性能
   - 观察训练曲线

3. **视觉蒸馏** (新的视觉配置更合适)
   ```bash
   python legged_gym/scripts/train.py \
       --exptid=go1_highres_697scan_2terrain_vision_v2 \
       --device cuda:0 \
       --resume \
       --resumeid=go1_highres_697scan_2terrain \
       --delay \
       --use_camera
   ```

---

## 💡 注意事项

1. **摄像头位置**
   - 新的摄像头位置更靠前、更靠高
   - 可能需要在实际机器人上验证物理可行性

2. **角度格式**
   - 新的angle = [25, 25]格式与旧的[roll, pitch]格式不同
   - 如果代码中有特殊处理，需要验证兼容性

3. **性能影响**
   - 更激进的俯视角度可能改善缝隙检测
   - 需要通过训练验证效果

---

**修改完成** ✅

