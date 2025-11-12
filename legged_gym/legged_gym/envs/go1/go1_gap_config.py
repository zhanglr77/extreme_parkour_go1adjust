# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause

from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

class Go1GapCfg( LeggedRobotCfg ):
    class env( LeggedRobotCfg.env ):
        num_envs = 2048  # 2048个并行环境
    class init_state( LeggedRobotCfg.init_state ):
        pos = [0.0, 0.0, 0.42] # x,y,z [m]
        default_joint_angles = { # = target angles [rad] when action = 0.0
            'FL_hip_joint': 0.1,   # [rad]
            'RL_hip_joint': 0.1,   # [rad]
            'FR_hip_joint': -0.1 ,  # [rad]
            'RR_hip_joint': -0.1,   # [rad]

            'FL_thigh_joint': 0.8,     # [rad]
            'RL_thigh_joint': 1.,   # [rad]
            'FR_thigh_joint': 0.8,     # [rad]
            'RR_thigh_joint': 1.,   # [rad]

            'FL_calf_joint': -1.5,   # [rad]
            'RL_calf_joint': -1.5,    # [rad]
            'FR_calf_joint': -1.5,  # [rad]
            'RR_calf_joint': -1.5,    # [rad]
        }
        
    class control( LeggedRobotCfg.control ):
        # PD Drive parameters:
        control_type = 'P'
        stiffness = {'joint': 30.}  # [N*m/rad] - Go1适合的刚性
        damping = {'joint': 0.6}     # [N*m*s/rad] - Go1适合的阻尼
        # action scale: target angle = actionScale * action + defaultAngle
        action_scale = 0.25
        # decimation: Number of control action updates @ sim DT per policy DT
        decimation = 4

    class asset( LeggedRobotCfg.asset ):
        file = '{LEGGED_GYM_ROOT_DIR}/resources/robots/go1/urdf/go1_new.urdf'
        foot_name = "foot"
        penalize_contacts_on = ["thigh", "calf"]
        terminate_after_contacts_on = ["base"]#, "thigh", "calf"]
        self_collisions = 1 # 1 to disable, 0 to enable...bitwise filter
  
    class rewards( LeggedRobotCfg.rewards ):
        soft_dof_pos_limit = 0.9
        base_height_target = 0.35  # Go1比A1高0.1m
        # class scales( LeggedRobotCfg.rewards.scales ):
            # torques = -0.0002
            # dof_pos_limits = -10.0

    class terrain( LeggedRobotCfg.terrain ):
        """
        训练配置：仅使用3种地形平均分布
        - parkour_gap: 原始随机间隙地形 (0.1m-0.8m)
        - fixed_gap_5cm: 固定5cm间隙 (课程学习: 2cm->5cm)
        - fixed_gap_15cm: 固定15cm间隙 (课程学习: 5cm->15cm)
        """
        mesh_type = 'trimesh'
        horizontal_scale = 0.05  # 恢复默认精度
        vertical_scale = 0.005   # [m]
        border_size = 5          # 恢复默认边界
        
        # 调整间隙参数适配5-15cm目标
        gap_size = [0.03, 0.18]  # 3-18cm，覆盖目标范围
        height = [0.02, 0.06]
        
        curriculum = True
        max_init_terrain_level = 3  # 从难度3开始
        
        # 地形规模
        terrain_length = 18.  # 每个子地形18米
        terrain_width = 4     # 每个子地形4米
        num_rows = 10         # 10个难度级别
        num_cols = 40         # 40种地形类型
        
        # 地形分布：仅使用3种地形，平均分配
        terrain_dict = {
            "smooth slope": 0., 
            "rough slope up": 0.0,
            "rough slope down": 0.0,
            "rough stairs up": 0.0, 
            "rough stairs down": 0.0, 
            "discrete": 0.0, 
            "stepping stones": 0.0,
            "gaps": 0.0,
            "smooth flat": 0.0,
            "pit": 0.0,
            "wall": 0.0,
            "platform": 0.0,
            "large stairs up": 0.0,
            "large stairs down": 0.0,
            "parkour": 0.0,
            "parkour_hurdle": 0.0,
            "parkour_flat": 0.0,
            "parkour_step": 0.0,
            "parkour_gap": 0.33,          # 33% - 原始随机间隙地形 ⭐
            "demo": 0.0,
            "fixed_gap_5cm": 0.33,        # 33% - 固定5cm间隙 ⭐（课程：2cm->5cm）
            "fixed_gap_15cm": 0.34,       # 34% - 固定15cm间隙 ⭐（课程：5cm->15cm）
        }
        terrain_proportions = list(terrain_dict.values())
        
    class commands( LeggedRobotCfg.commands ):
        curriculum = False
        max_curriculum = 1.
        num_commands = 4
        resampling_time = 7. # 适中的命令重采样时间
        
        class ranges:
            lin_vel_x = [0.3, 1.2] # Go1适中的前进速度
            lin_vel_y = [-0.3, 0.3] # 允许适度侧向移动
            ang_vel_yaw = [-0.5, 0.5] # 适度转向能力
            heading = [-3.14, 3.14]

    class domain_rand( LeggedRobotCfg.domain_rand ):
        # Go1的域随机化设置
        randomize_friction = True
        friction_range = [0.7, 1.8] 
        randomize_base_mass = True
        added_mass_range = [0., 2.5] 
        push_robots = True
        push_interval_s = 8

class Go1GapCfgPPO( LeggedRobotCfgPPO ):
    class algorithm( LeggedRobotCfgPPO.algorithm ):
        entropy_coef = 0.01
    class runner( LeggedRobotCfgPPO.runner ):
        run_name = ''
        experiment_name = 'go1_gap'