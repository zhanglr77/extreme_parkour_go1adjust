# 推送代码到GitHub仓库指南

## 当前状态
✅ 代码已经在本地提交 (commit b7c5404)
⏳ 等待推送到远程仓库

## 方法1: 使用GitHub Personal Access Token (推荐)

### 步骤：
1. 创建GitHub Personal Access Token:
   - 访问: https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 勾选 `repo` 权限
   - 生成并复制token

2. 推送代码:
```bash
cd /home/zhanglr/Downloads/extreme-parkour

# 设置远程仓库地址（使用token）
git remote set-url origin https://<YOUR_TOKEN>@github.com/ATECrl/extreme_parkour_go1adjust.git

# 推送代码
git push -u origin main
```

## 方法2: 使用SSH密钥

### 步骤：
1. 生成SSH密钥（如果没有）:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. 添加SSH密钥到GitHub:
```bash
cat ~/.ssh/id_ed25519.pub
```
   - 复制输出的公钥
   - 访问: https://github.com/settings/keys
   - 添加新的SSH密钥

3. 推送代码:
```bash
cd /home/zhanglr/Downloads/extreme-parkour
git remote set-url origin git@github.com:ATECrl/extreme_parkour_go1adjust.git
git push -u origin main
```

## 方法3: 在GitHub网页上创建仓库并推送

1. 访问 https://github.com/ATECrl/extreme_parkour_go1adjust
2. 如果仓库不存在，创建新仓库
3. 按照GitHub提供的指令推送：

```bash
cd /home/zhanglr/Downloads/extreme-parkour
git remote set-url origin https://github.com/ATECrl/extreme_parkour_go1adjust.git
git push -u origin main
```

## 已提交的修改内容

### 核心文件：
- `legged_gym/legged_gym/envs/go1/go1_config.py` - Go1训练配置（3种地形平均分布）
- `legged_gym/legged_gym/envs/go1/go1_gap_config.py` - Go1间隙训练配置
- `legged_gym/legged_gym/envs/a1/a1_gap_config.py` - A1间隙训练配置
- `legged_gym/legged_gym/utils/terrain.py` - 新增fixed_gap_5cm和fixed_gap_15cm地形函数
- `legged_gym/legged_gym/scripts/play.py` - 支持自定义地形可视化
- `legged_gym/legged_gym/scripts/train.py` - 支持有头/无头模式切换
- `legged_gym/legged_gym/envs/__init__.py` - 注册新任务
- `legged_gym/legged_gym/envs/base/legged_robot_config.py` - 基础配置更新

### 配置详情：
- **地形网格**: 10行 × 40列 = 400个子地形
- **地形分布**: 
  * parkour_gap: 33% (0.1m-0.8m随机间隙)
  * fixed_gap_5cm: 33% (2cm->5cm课程学习)
  * fixed_gap_15cm: 34% (5cm->15cm课程学习)
- **并行环境**: 2048个
- **课程学习**: 从难度5开始（0-9，共10级）
- **地形尺寸**: 18m × 4m，5cm网格分辨率

## 服务器训练命令

推送成功后，在服务器上执行：

```bash
# 克隆仓库
git clone https://github.com/ATECrl/extreme_parkour_go1adjust.git
cd extreme_parkour_go1adjust

# 安装依赖
bash install.sh

# 开始训练
cd legged_gym
python legged_gym/scripts/train.py \
    --task=go1 \
    --headless \
    --proj_name=parkour_new \
    --exptid=go1_3terrain_2048envs
```
