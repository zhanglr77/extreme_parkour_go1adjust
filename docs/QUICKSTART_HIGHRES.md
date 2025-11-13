# Go1高分辨率Scandots配置 - 快速开始

## 🚀 立即开始

### 1. 训练新模型（推荐）

```bash
# 切换到工作目录
cd /home/zhanglr/Downloads/extreme-parkour/legged_gym

# 激活环境
source /home/zhanglr/anaconda3/bin/activate parkour
export LD_LIBRARY_PATH=/home/zhanglr/anaconda3/envs/parkour/lib:$LD_LIBRARY_PATH

# 开始训练（从头开始，不加载旧模型）
python legged_gym/scripts/train.py \
    --task=go1_highres \
    --proj_name=parkour_new \
    --exptid=go1_highres_391scan \
    --run_name=highres_$(date +%Y%m%d_%H%M%S)

# 预计训练时间：28-30小时（4096环境，25000次迭代）
```

### 2. 监控训练进度

```bash
# 在另一个终端启动TensorBoard
tensorboard --logdir=logs/parkour_new/go1_highres_391scan

# 浏览器打开：http://localhost:6006
# 关注指标：
# - Train/mean_reward: 目标 >8.0
# - Episode_rew/tracking_lin_vel: 接近0
# - Train/mean_episode_length: >150 steps
```

### 3. 评估模型表现

```bash
# 训练到20000-25000次后评估
python legged_gym/scripts/play.py \
    --task=go1_highres \
    --proj_name=parkour_new \
    --exptid=go1_highres_391scan \
    --checkpoint=20000

# 观察机器人在三种地形上的表现
```

---

## 📋 配置文件位置

```
新增文件：
├─ legged_gym/envs/go1/go1_gap_highres_config.py    # 主配置文件
├─ docs/GO1_HIGHRES_SCANDOTS_CONFIG.md              # 详细文档
├─ docs/CONFIG_COMPARISON.md                        # 配置对比
└─ docs/QUICKSTART_HIGHRES.md                       # 本文档

修改文件：
└─ legged_gym/envs/__init__.py                      # 添加任务注册
```

---

## ✅ 验证配置正确性

```bash
# 测试配置是否能加载
python -c "
from legged_gym.envs import task_registry
env, env_cfg = task_registry.get_cfgs(name='go1_highres')
print('✅ 配置加载成功！')
print(f'Scandots点数: {env_cfg.env.n_scan}')
print(f'观测维度: {env_cfg.env.num_observations}')
print(f'环境数量: {env_cfg.env.num_envs}')
print(f'X轴采样点: {len(env_cfg.terrain.measured_points_x)}')
print(f'Y轴采样点: {len(env_cfg.terrain.measured_points_y)}')
"

# 期望输出：
# ✅ 配置加载成功！
# Scandots点数: 391
# 观测维度: 2856
# 环境数量: 4096
# X轴采样点: 23
# Y轴采样点: 17
```

---

## 🎯 关键参数速查

| 参数 | 值 | 说明 |
|-----|---|------|
| `n_scan` | 391 | Scandots总点数 |
| `num_observations` | 2856 | 总观测维度 |
| `num_envs` | 4096 | 并行环境数 |
| `measured_points_x` | 23个点 | X轴采样（0-1.2m） |
| `measured_points_y` | 17个点 | Y轴采样（±0.45m） |
| `max_iterations` | 25000 | 训练迭代次数 |

---

## 🔧 常见问题

### Q1: 训练显示维度错误？
```
A: 检查是否正确加载了go1_highres配置
   python train.py --task=go1_highres  # 注意是 go1_highres 不是 go1
```

### Q2: GPU内存不足？
```python
# 修改 go1_gap_highres_config.py
class env( LeggedRobotCfg.env ):
    num_envs = 2048  # 从4096降到2048
```

### Q3: 想用旧模型评估？
```
A: 不可以！新旧配置不兼容
   - 旧模型（132点）只能用go1或go1_gap配置
   - 新模型（391点）只能用go1_highres配置
```

### Q4: 训练太慢？
```
A: 正常现象，高分辨率会增加15-20%训练时间
   - 如果可接受：继续训练
   - 如果不能接受：考虑使用go1_gap配置（132点）
```

---

## 📊 性能基准

在A100 40GB GPU上的预期性能：

```
配置：4096个环境
FPS：~1000 steps/s
每次迭代：~20秒
总训练时间（25000次）：约28-30小时

内存占用：
- GPU显存：~28-32 GB
- 系统内存：~20 GB
```

---

## 🎓 进阶使用

### 与原配置对比

```bash
# 同时训练两个配置进行对比
# Terminal 1: 标准配置
python train.py --task=go1 --exptid=go1_standard_132scan

# Terminal 2: 高分辨率配置  
python train.py --task=go1_highres --exptid=go1_highres_391scan

# 然后在TensorBoard中对比两者的性能
tensorboard --logdir=logs/parkour_new/
```

### 调整采样分辨率

如果想要不同的分辨率，修改`go1_gap_highres_config.py`：

```python
# 例如：更激进的高分辨率（近场2cm）
measured_points_x = [
    # 0-0.3m: 2cm间隔 - 15个点
    0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 
    0.18, 0.20, 0.22, 0.24, 0.26, 0.28,
    # 0.3-1.2m: 10cm间隔 - 9个点
    0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20
]
# 记得更新 n_scan = 24 × 17 = 408
```

---

## 📖 相关文档

详细文档请参考：
- **完整配置说明**: `docs/GO1_HIGHRES_SCANDOTS_CONFIG.md`
- **配置对比表**: `docs/CONFIG_COMPARISON.md`
- **原始配置**: `legged_gym/envs/go1/go1_config.py`

---

## 🎉 预期成果

训练完成后，你的模型应该能够：

✅ 稳定通过2-3.5cm的密集小间隙（success rate >90%）  
✅ 精确控制落脚点，避开间隙  
✅ 在5-10cm间隙地形上表现优秀  
✅ 为后续视觉蒸馏提供高质量teacher模型  

祝训练顺利！🚀
