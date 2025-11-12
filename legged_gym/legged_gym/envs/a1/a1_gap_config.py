# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause

from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO


class A1GapCfg( LeggedRobotCfg ):
    """
    A1机器人专门用于间隙跳跃训练的配置
    重点训练跨越固定间隙的能力
    """
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
        stiffness = {'joint': 40.}  # [N*m/rad]
        damping = {'joint': 1}     # [N*m*s/rad]
        action_scale = 0.25
        decimation = 4

    class asset( LeggedRobotCfg.asset ):
        file = '{LEGGED_GYM_ROOT_DIR}/resources/robots/a1/urdf/a1.urdf'
        foot_name = "foot"
        penalize_contacts_on = ["thigh", "calf", "base"]
        terminate_after_contacts_on = ["base"]
        self_collisions = 1 # 1 to disable, 0 to enable...bitwise filter
  
    class rewards( LeggedRobotCfg.rewards ):
        soft_dof_pos_limit = 0.9
        base_height_target = 0.25

    class terrain( LeggedRobotCfg.terrain ):
        # 专注于间隙地形的配置
        mesh_type = 'trimesh'
        horizontal_scale = 0.05 # [m]
        vertical_scale = 0.005 # [m]
        border_size = 5 # [m]
        
        # 间隙相关参数
        gap_size = [0.15, 0.4] # 间隙大小范围 [0.15m, 0.4m]
        height = [0.02, 0.06]
        
        curriculum = True
        max_init_terrain_level = 2 # 从较低难度开始
        
        # 地形分布：专注于间隙和相关地形
        terrain_dict = {
            "smooth slope": 0.0, 
            "rough slope up": 0.0,
            "rough slope down": 0.0,
            "rough stairs up": 0.0, 
            "rough stairs down": 0.0, 
            "discrete": 0.0, 
            "stepping stones": 0.0,
            "gaps": 0.0,  # 暂时设为0，我们主要用parkour_gap
            "smooth flat": 0.1,  # 少量平地用于恢复
            "pit": 0.0,
            "wall": 0.0,
            "platform": 0.0,
            "large stairs up": 0.0,
            "large stairs down": 0.0,
            "parkour": 0.0,
            "parkour_hurdle": 0.0,
            "parkour_flat": 0.1,  # 少量跑酷平地
            "parkour_step": 0.0,
            "parkour_gap": 0.8,    # 80%的地形为跑酷间隙！
            "demo": 0.0,
        }
        
    class commands( LeggedRobotCfg.commands ):
        curriculum = False
        max_curriculum = 1.
        num_commands = 4
        resampling_time = 8. # 稍微延长命令重采样时间
        
        class ranges:
            lin_vel_x = [0.5, 1.5] # 保持中等前进速度，专注跳跃
            lin_vel_y = [-0.2, 0.2] # 减少侧向移动
            ang_vel_yaw = [-0.3, 0.3] # 减少转向
            heading = [-3.14, 3.14]

    class domain_rand( LeggedRobotCfg.domain_rand ):
        # 减少随机化，专注学习跳跃技能
        randomize_friction = True
        friction_range = [0.8, 1.5] # 缩小摩擦力范围
        randomize_base_mass = True
        added_mass_range = [0., 2.] # 减少质量变化
        push_robots = True
        push_interval_s = 10 # 增加推力间隔


class A1GapCfgPPO( LeggedRobotCfgPPO ):
    """
    间隙跳跃训练的PPO配置
    """
    class algorithm( LeggedRobotCfgPPO.algorithm ):
        entropy_coef = 0.01
        learning_rate = 1.e-3
        num_learning_epochs = 5
        gamma = 0.99
        lam = 0.95
        num_mini_batches = 4
        desired_kl = 0.01
        max_grad_norm = 1.

    class runner( LeggedRobotCfgPPO.runner ):
        run_name = ''
        experiment_name = 'a1_gap'
        max_iterations = 15000 # 15k迭代
        save_interval = 500
        
    class policy( LeggedRobotCfgPPO.policy ):
        init_noise_std = 1.0
        actor_hidden_dims = [512, 256, 128]
        critic_hidden_dims = [512, 256, 128]
        activation = 'elu'