# 🎥 快速开始 - 摄像头深度预览

## 你的问题
> 我想知道是否可以现在看到这个训练的摄像头的深度画面，方便我在训练视觉蒸馏阶段之前去调整摄像头角度来让摄像头能够看到缝隙但是看不到本体？

## ✅ 答案：可以！

你现在就可以预览摄像头深度画面来调整角度。

---

## 🚀 快速操作步骤

### 第一步：临时启用摄像头

编辑 `legged_gym/legged_gym/envs/go1/go1_gap_highres_config.py`：

找到这一行（约第214行）：
```python
use_camera = False  # 初始训练不使用相机
```

改为：
```python
use_camera = True  # 改为True以启用摄像头
```

### 第二步：运行play脚本查看深度画面

```bash
cd /home/zhanglr/Downloads/extreme-parkour-server-training/legged_gym

# 命令1: 用模型12500预览（推荐，这是最好的模型）
python legged_gym/scripts/play.py \
    --task=go1_highres \
    --proj_name=parkour_new \
    --exptid=go1_highres_697scan_2terrain \
    --checkpoint=12500 \
    --use_camera

# 或者用10000或7500的模型
python legged_gym/scripts/play.py \
    --task=go1_highres \
    --proj_name=parkour_new \
    --exptid=go1_highres_697scan_2terrain \
    --checkpoint=10000 \
    --use_camera
```

### 第三步：观察深度图像

- IsaacGym窗口会实时显示摄像头看到的深度画面
- **黑色** = 远距离（看不到或超过范围）
- **白色** = 近距离（摄像头前方）
- **灰色** = 中间距离

### 第四步：调整摄像头参数

根据观察结果，修改 `go1_gap_highres_config.py` 中的摄像头参数：

```python
class depth(LeggedRobotCfg.depth):
    # ============= 可以调整的参数 =============
    
    position = [0.27, 0, 0.03]  # [x前后, y左右, z高度] 单位: 米
    # x: 0.27 = 摄像头在机器人前方27cm
    #    增加 → 摄像头更靠前 → 看近处
    #    减少 → 摄像头更靠后 → 看远处
    # y: 0 = 中心（通常不改）
    # z: 0.03 = 摄像头离地3cm（离body多高）
    #    增加 → 摄像头更高 → 看不到本体
    #    减少 → 摄像头更低 → 容易看到本体
    
    angle = [0, -10]  # [roll翻滚, pitch俯仰] 单位: 度
    # pitch: -10 = 向下看10度（负数=向下，正数=向上）
    #    减小(更负) → 更低头 → 看缝隙更清楚
    #    增大(更正) → 抬头 → 看远处
    
    # ============= 不用改的参数 =============
    horizontal_fov = 87  # 视场角
    original = (106, 60)  # 原始分辨率
    resized = (87, 58)  # 缩放分辨率
```

---

## 📊 快速参考：常见调整

### 🔴 问题：看到了机器人本体/腿部

**原因**: 摄像头位置太低或角度不对

**解决方案**:
```python
# 方案1：增加高度（最有效）
position = [0.27, 0, 0.05]  # 从0.03改成0.05

# 方案2：增大向下看的角度
angle = [0, -15]  # 从-10改成-15，更俯视

# 方案3：向前移动摄像头
position = [0.35, 0, 0.03]  # 从0.27改成0.35
```

### 🟢 问题：看不清楚缝隙

**原因**: 距离太远或角度不对

**解决方案**:
```python
# 方案1：减小俯仰角（更低头看）
angle = [0, -15]  # 从-10改成-15

# 方案2：向前靠近缝隙
position = [0.25, 0, 0.03]  # 从0.27改成0.25

# 方案3：结合调整
position = [0.30, 0, 0.04]
angle = [0, -12]
```

### 🟡 问题：视野太窄或太宽

**原因**: 视场角不合适

**解决方案**:
```python
# 视野太窄（看不全）
horizontal_fov = 100  # 从87改成100

# 视野太宽（看得太散）
horizontal_fov = 70   # 从87改成70
```

---

## 🔄 完整调整工作流

```
1. 启用摄像头 (use_camera = True)
     ↓
2. 运行 play --checkpoint=12500 --use_camera
     ↓
3. 观察深度画面
     ↓
4. 根据观察修改 position/angle
     ↓
5. 再次运行 play 查看效果
     ↓
6. 循环2-5，直到满足要求
     ↓
7. 关闭摄像头 (use_camera = False)
     ↓
8. 启动视觉蒸馏训练
```

---

## ⚙️ 视觉蒸馏训练准备

### 当你调整好摄像头参数后

#### 步骤1: 确保配置正确
编辑 `go1_gap_highres_config.py`：
```python
class depth(LeggedRobotCfg.depth):
    use_camera = False  # 保持False（通过--use_camera命令行启用）
    # position 和 angle 设置为最佳值
    position = [你调整的最佳值]
    angle = [你调整的最佳值]
```

#### 步骤2: 启动视觉蒸馏训练
```bash
cd legged_gym

# 创建蒸馏版本的新训练
python legged_gym/scripts/train.py \
    --exptid=go1_highres_697scan_2terrain_vision_distill \
    --device cuda:0 \
    --resume \
    --resumeid=go1_highres_697scan_2terrain \
    --delay \
    --use_camera

# 说明：
# --resume: 从base policy恢复
# --resumeid: base policy的ID（会自动从logs中查找）
# --delay: 添加动作延迟
# --use_camera: 启用摄像头输入
```

训练 5-10k 迭代（5-10小时，3090 GPU）

#### 步骤3: 测试蒸馏模型
```bash
python legged_gym/scripts/play.py \
    --exptid=go1_highres_697scan_2terrain_vision_distill \
    --delay \
    --use_camera
```

---

## 📋 现在就可以做什么

✅ **立即可做**:
1. 启用摄像头，查看深度画面
2. 调整 `position` 和 `angle` 参数
3. 反复测试找到最优配置

⏳ **准备好后**:
4. 关闭摄像头（use_camera = False）
5. 启动视觉蒸馏训练
6. 获得最终的视觉+Scandots联合模型

---

## 💡 关键提示

1. **现在的模型（model_12500.pt）已经很好了**
   - 基于Scandots训练，能成功跨越缝隙
   - 用它来预览摄像头很合适

2. **视觉蒸馏是可选的增强**
   - base policy 已能工作 ✅
   - 视觉蒸馏可以进一步提升性能
   - 需要在摄像头参数优化后再做

3. **摄像头参数调整很关键**
   - 好的摄像头视角 = 更好的蒸馏效果
   - 现在就调，比之后再调省时间

---

## 🎯 下一步建议

1. **立即**: 修改 `use_camera = True` 并运行 play 脚本
2. **5分钟内**: 观察深度画面，记录问题
3. **调整**: 修改 position/angle 参数
4. **验证**: 再次运行 play，看效果
5. **确认**: 当满足要求后（看到缝隙，看不到本体），记下最终参数
6. **准备**: 更新配置并准备蒸馏训练

---

## 📚 相关文件

- **详细指南**: `VISION_DISTILLATION_GUIDE.md`
- **配置文件**: `legged_gym/legged_gym/envs/go1/go1_gap_highres_config.py` (第212-233行)
- **play脚本**: `legged_gym/legged_gym/scripts/play.py`
- **预览脚本**: `legged_gym/legged_gym/scripts/preview_depth.py`

