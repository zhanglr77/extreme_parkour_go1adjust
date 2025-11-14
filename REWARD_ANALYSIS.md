# Reward分析与记录机制说明

## 问题总结
对比两次训练，发现总平均reward下降了4，但各项reward项的下降之和只有2.2：
- `terrain_level` reward: ↓ 2
- `tracking_yaw` reward: ↓ 0.1  
- `tracking_vel` reward: ↓ 0.2
- 其他项: 基本无影响
- **差额: ~1.8 未被记录**

---

## 答案：为什么会有差异？

### 1. **平均计算时间点不同**

```python
# on_policy_runner.py line 350 的reward记录方式：
self.extras["episode"]['rew_' + key] = torch.mean(self.episode_sums[key][env_ids]) / self.max_episode_length_s
```

这里的关键是 `/self.max_episode_length_s`：
- **`episode_sums[key]`** = 该episode中该reward项的累积总和（从episode开始到reset）
- **除以 `max_episode_length_s`** = 转换为每秒的平均reward

这意味着记录的是 **"单位时间内的平均reward"**，而不是"总reward"。

### 2. **平均vs实时的区别**

假设你看的是两个指标：

**A. WandB中的`Episode_rew/xxx`（平均化后）**
- 这是episode结束时计算的，经过了 `/max_episode_length_s` 的归一化
- 这是你说的"平均reward"

**B. 环境内部的`episode_sums[key]`（累积未归一化）**  
- 这是原始累积值，没有做时间归一化
- 这可能是你提到的"实时到最后的实时值"

---

## 关于 `terrain_level` Reward

### 这是什么？

`terrain_level` **不是一个reward项**，而是一个**课程学习状态指标**！

```python
# legged_robot.py line 356
if self.cfg.terrain.curriculum:
    self.extras["episode"]["terrain_level"] = torch.mean(self.terrain_levels.float())
```

这记录的是该episode中环境所处的难度等级（0-9的某个值）。

### 它不是reward，为什么会"下降"？

可能的原因：

1. **环境变得更难了**
   - 新配置（5cm + 15cm）相比旧配置（5cm + 15cm + variable gap）
   - 环境可能在curriculum中后退了（terrain_level变低）
   - 说明智能体在新地形上的表现比较差

2. **这反映了什么**
   - 从`terrain_level`下降意味着：机器人无法通过更难的地形，curriculum将其降到更简单的难度
   - 这不是reward减少，而是**难度等级减少**

3. **这个数值应该多少才算好？**
   - 范围：0-9（假设有10个难度级）
   - **越高越好**（说明可以处理更难的地形）
   - 理想情况：保持在接近9（或稳定在某个较高值）
   - 下降说明学习到了瓶颈或环境变难

---

## 完整的Reward机制

### Step 1: 环境计算Reward
```python
# legged_robot.py line 363-381
def compute_reward(self):
    for i in range(len(self.reward_functions)):
        name = self.reward_names[i]
        rew = self.reward_functions[i]() * self.reward_scales[name]
        # rew 现在是该timestep的reward
        self.episode_sums[name] += rew  # 累积
    
    # 检查只有正reward
    if self.cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp_min(total_reward, 0)
```

### Step 2: Episode结束时归一化
```python
# legged_robot.py line 349-351
for key in self.episode_sums.keys():
    # 重点：这里除以了max_episode_length_s
    self.extras["episode"]['rew_' + key] = torch.mean(self.episode_sums[key][env_ids]) / self.max_episode_length_s
    self.episode_sums[key][env_ids] = 0.  # 重置
```

### Step 3: WandB记录
```python
# on_policy_runner.py line 408-410
for key in locs['ep_infos'][0]:
    infotensor = torch.tensor([], device=self.device)
    for ep_info in locs['ep_infos']:
        infotensor = torch.cat((infotensor, ep_info[key].to(self.device)))
    value = torch.mean(infotensor)  # 对所有episode再取平均
    wandb_dict['Episode_rew/' + key] = value
```

### 因此：WandB记录的是"跨episode的平均，并且每个episode已经除以时长"

---

## 为什么会有2差额未被记录？

可能的原因：

### 原因1: `only_positive_rewards`导致的信息丢失
```python
if self.cfg.rewards.only_positive_rewards:
    total_reward = torch.clamp_min(total_reward, 0)
```

- 如果总reward < 0，会被clamp到0
- 但各个单独reward项不会被clamp（只有总reward被clamp）
- 这可能导致记录的单项之和 ≠ 总reward

### 原因2: 归一化导致的数值差异
- 总reward的归一化过程可能与各单项不同
- `max_episode_length_s`可能在某些情况下计算有差异

### 原因3: 未被记录的reward项
检查你的配置中是否有：
```python
# legged_robot_config.py line 293-311
class rewards:
    class scales:
        tracking_goal_vel = 1.5
        tracking_yaw = 0.5
        # ... 其他项
        # 是否有某项的scale在这次修改后变了？
        # 或者有些项因为scale=0而没被记录？
```

---

## 建议的Debug方法

### 1. 直接对比`episode_sums`

在legged_robot.py的compute_reward后添加logging：
```python
# 在compute_reward后
for key in self.episode_sums.keys():
    if self.episode_length_buf[0] % 100 == 0:  # 每100步打一次
        print(f"Env 0, {key}: {self.episode_sums[key][0].item()}")
```

### 2. 查看WandB的详细数据

在WandB网页上，对比两次训练的所有`Episode_rew/`开头的指标，包括：
- `Episode_rew/tracking_goal_vel`
- `Episode_rew/tracking_yaw`
- `Episode_rew/lin_vel_z` (可能被penalize了)
- `Episode_rew/ang_vel_xy` (可能被penalize了)
- `Episode_rew/orientation` (可能被penalize了)
- `Episode_rew/dof_acc` 
- `Episode_rew/collision`
- ... (所有reward项)

### 3. 检查terrain_level下降的原因

```python
# 在on_policy_runner.py的learn_RL中添加
if 'terrain_level' in locs['ep_infos'][0]:
    terrain_levels = [ep['terrain_level'] for ep in locs['ep_infos']]
    print(f"Terrain level distribution: min={min(terrain_levels)}, max={max(terrain_levels)}, mean={statistics.mean(terrain_levels)}")
```

---

## 总结

| 指标 | 含义 | 单位 | 应该怎样 |
|------|------|------|---------|
| `Episode_rew/xxx` | 每秒平均reward | reward/sec | 越高越好 |
| `terrain_level` | 课程难度等级 | 0-9 | 越高越好（应该上升或稳定） |
| `Mean reward (total)` | 总reward平均 | 绝对值 | 越高越好 |

**关键发现**：
- `terrain_level`下降说明新配置对机器人更困难
- 2点的下降 + 0.1 + 0.2 = 2.3，还差1.7
- 这1.7可能来自：
  1. Penalty项（负reward）增加了
  2. 数据平均化和归一化的差异
  3. `only_positive_rewards`导致的clamp

建议检查：
- 是否有penalty项（lin_vel_z, ang_vel_xy, orientation等）的reward大幅下降
- 机器人是否在新地形上更容易倾倒或出现不稳定行为
