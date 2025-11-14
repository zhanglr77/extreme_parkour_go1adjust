# Reward项详解与配置

## 当前配置中的所有Reward项

```python
# legged_robot_config.py line 295-310 的reward_scales
class scales:
    # ✅ 正向Reward（鼓励的行为）
    tracking_goal_vel = 1.5      # 追踪目标速度的奖励
    tracking_yaw = 0.5            # 追踪目标偏航角的奖励
    
    # ❌ 负向Reward（惩罚的行为）
    lin_vel_z = -1.0              # 竖直速度惩罚（不要往上/下跳）
    ang_vel_xy = -0.05            # XY平面角速度惩罚（保持平衡）
    orientation = -1.0            # 身体倾斜惩罚（保持直立）
    dof_acc = -2.5e-7             # 关节加速度惩罚（动作平滑）
    collision = -10.0             # 碰撞惩罚（避免碰撞）
    action_rate = -0.1            # 动作变化率惩罚（动作连贯）
    delta_torques = -1.0e-7        # 扭矩变化率惩罚（平滑扭矩）
    torques = -0.00001            # 扭矩大小惩罚（节省能量）
    hip_pos = -0.5                # 髋部位置惩罚（站立姿态）
    dof_error = -0.04             # 关节误差惩罚（准确跟踪）
    feet_stumble = -1             # 脚绊倒惩罚（稳定行走）
    feet_edge = -1                # 脚在边缘惩罚（避免摔倒）
```

---

## 各Reward项的含义与影响

### 正向Reward（目标相关）

#### 1. `tracking_goal_vel` = 1.5 ⭐ **最重要**
- **含义**: 机器人跟踪目标线速度的能力
- **计算**: `exp(-error²/sigma)` 其中 sigma=0.2
- **范围**: [0, 1]
- **影响**: 
  - 直接影响机器人能否按指令速度移动
  - 值高(>0.8) = 速度跟踪准确
  - 值低(<0.3) = 速度跟踪差，可能摔倒或太慢
- **在新配置下下降0.2**: 说明机器人在新地形上速度表现不如以前

#### 2. `tracking_yaw` = 0.5 ⭐ **重要**
- **含义**: 机器人跟踪目标偏航角（转向）的能力
- **计算**: `exp(-error²/sigma)` 其中 sigma=0.2
- **范围**: [0, 1]
- **影响**:
  - 决定机器人转向准确度
  - 值高(>0.7) = 转向平滑准确
  - 值低(<0.3) = 转向困难或过度
- **在新配置下下降0.1**: 说明新地形下转向能力稍差

---

### 负向Reward（稳定性相关）

#### 3. `lin_vel_z` = -1.0 ⚠️ **重要**
- **含义**: 竖直速度惩罚（上下跳跃）
- **计算**: `-1.0 * lin_vel_z² * dt`
- **影响**:
  - 防止机器人在间隙前跳跃
  - 保持身体稳定贴地
  - **在新配置下可能增加**: 如果下降2是来自terrain_level这个指标，可能是机器人在跳跃时摔倒了，这个惩罚增加了
- **检查**: 如果这项变成-2而不是0，就解释了为什么总reward少了~1-2

#### 4. `orientation` = -1.0 ⚠️ **重要**
- **含义**: 身体倾斜惩罚
- **计算**: `-1.0 * (1 - cos(roll))² * dt` 等
- **影响**:
  - 鼓励机器人保持正立姿态
  - 防止侧翻
  - **在新地形上可能增加**: 如果新地形导致身体不稳定，这项也会增加

#### 5. `ang_vel_xy` = -0.05
- **含义**: XY平面角速度惩罚
- **计算**: `-0.05 * (ang_vel_x² + ang_vel_y²) * dt`
- **影响**:
  - 防止身体滚动和俯仰过度
  - 下降0.05不太可能解释丢失的reward

#### 6. `collision` = -10.0 ⚠️ **很可能**
- **含义**: 碰撞惩罚
- **计算**: `-10.0 * collision_force * dt`
- **影响**:
  - 机器人与障碍物接触会受到巨大惩罚
  - **这可能是关键！** 如果新配置下机器人更容易与间隙边缘碰撞，这项会增加（变成负数）
- **推测**: 新配置下机器人可能在跨越小间隙时更容易碰到边缘

---

## "缺失的2点"可能来自哪里？

### 假设对比：

**旧配置**: parkour_gap(33%) + fixed_gap_5cm(33%) + fixed_gap_15cm(34%)
**新配置**: fixed_gap_5cm(50%) + fixed_gap_15cm(50%)

机器人表现差异：

```
总reward下降: 4
├─ tracking_vel ↓0.2 (因为新地形更陡峭或间隙更复杂)
├─ tracking_yaw ↓0.1 (因为新地形改变了方向要求)
├─ terrain_level ↓2  (因为curriculum认为当前难度太高了，退回)
├─ orientation ↓? (可能增加，如果倾倒更频繁)
├─ lin_vel_z ↓? (可能增加，如果需要更多垂直跳跃)
├─ collision ↓? (可能增加，如果间隙边缘碰撞更多)
└─ 其他项
```

**关键问题**: 记录的是什么和什么的下降？

---

## 如何解读 `terrain_level` 下降2

### 这意味着：

1. **环境变更前**: 机器人能在难度level 7-8上训练
2. **环境变更后**: 机器人只能在难度level 5-6上存活

### 原因可能：

```
新配置的特点：
- 移除了parkour_gap（变化间隙）
- fixed_gap_5cm增加到50%
- fixed_gap_15cm增加到50%

后果：
- 环境变化多样性减少 → curriculum应该加速
- 但实际terrain_level下降 → 说明机器人表现变差

反推：
- 新地形的难度更高 OR
- 机器人对新地形的学到策略不适应
```

---

## 完整诊断表

检查你的WandB，找以下指标：

| 指标 | 旧值 | 新值 | 差异 | 诊断 |
|------|------|------|------|------|
| `Episode_rew/tracking_goal_vel` | ? | ?-0.2 | 预期↓ | ✅ 符合 |
| `Episode_rew/tracking_yaw` | ? | ?-0.1 | 预期↓ | ✅ 符合 |
| `Episode_rew/lin_vel_z` | ? | ? | **可能↓2** | ⚠️ 检查这个 |
| `Episode_rew/orientation` | ? | ? | **可能↓1** | ⚠️ 检查这个 |
| `Episode_rew/collision` | ? | ? | **可能↓1** | ⚠️ 检查这个 |
| `Episode_rew/dof_error` | ? | ? | ? | 检查 |
| `Episode_rew/feet_stumble` | ? | ? | ? | 检查 |
| `Episode_rew/feet_edge` | ? | ? | **可能↓2** | ⚠️ 检查这个 |
| `terrain_level` | ? | ?-2 | ✅ 符合 | 环境难度下降 |

---

## 建议的优化方向

### 如果是稳定性问题（lin_vel_z, orientation增加）
1. 减少`lin_vel_z`的惩罚权重
2. 增加curriculum的初始难度
3. 检查间隙宽度范围是否太接近机器人腿长

### 如果是碰撞问题（collision/feet_edge增加）
1. 增加预留margin
2. 减少地形间隙变化的陡峭度
3. 增加扫描点（Scandots）的密度来提前预测

### 如果是综合问题
1. 从检查点恢复训练而不是重新开始
2. 调整curriculum的学习速率
3. 增加training环境数量来加速学习

---

## 数据对齐建议

下次对比时，同时记录：
```
Mean reward总和 = sum of all Episode_rew/* (记录到spreadsheet)
terrain_level数值 = Episode/terrain_level (记录到spreadsheet)
Episode长度 = Episode/episode_length (看有无变化)
```

这样可以快速定位问题。
