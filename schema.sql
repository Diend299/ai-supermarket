-- 创建数据库
CREATE DATABASE IF NOT EXISTS `ai_supermarket` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `ai_supermarket`;

-- 创建用户表
CREATE TABLE `user` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(64) NOT NULL COMMENT '用户名',
    `email` VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    
    `balance` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '账户余额（人民币/美元）',
    `points` INT NOT NULL DEFAULT 0 COMMENT '积分（用于任务消耗）',
    
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1=正常，0=禁用',
    
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';


CREATE TABLE `ai_task` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    
    `task_type` VARCHAR(50) NOT NULL COMMENT '任务类型（video_generate / avatar_generate 等）',
    
    `task_status` TINYINT NOT NULL DEFAULT 0 COMMENT '任务状态：0=排队中，1=生成中，2=成功，3=失败',
    
    `params` JSON NOT NULL COMMENT '任务参数(JSON)，如 prompt、人物、语音、分辨率等',
    
    `progress` INT DEFAULT 0 COMMENT '进度(0-100)',
    
    `error_msg` VARCHAR(500) DEFAULT NULL COMMENT '失败原因',
    
    `consume_points` INT NOT NULL DEFAULT 0 COMMENT '消耗积分',
    `consume_balance` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '消耗余额',
    
    `started_at` DATETIME DEFAULT NULL COMMENT '开始执行时间',
    `finished_at` DATETIME DEFAULT NULL COMMENT '完成时间',
    
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_task_status` (`task_status`),
    INDEX `idx_created_at` (`created_at`),
    
    CONSTRAINT `fk_task_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI任务表';

CREATE TABLE `ai_result_resource` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '资源ID',
    `task_id` BIGINT UNSIGNED NOT NULL COMMENT '任务ID',
    
    `resource_type` VARCHAR(20) NOT NULL COMMENT '资源类型：video/image/audio',
    
    `resource_url` VARCHAR(500) NOT NULL COMMENT '资源访问URL',
    `content_text` TEXT COMMENT '生成文本内容(text类型用)',
    
    `cover_url` VARCHAR(500) DEFAULT NULL COMMENT '封面图URL（视频用）',
    
    `duration` INT DEFAULT NULL COMMENT '时长（秒）',
    
    `file_size` BIGINT DEFAULT NULL COMMENT '文件大小（字节）',
    
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1=有效，0=已删除',
    
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    INDEX `idx_task_id` (`task_id`),
    
    CONSTRAINT `fk_resource_task` FOREIGN KEY (`task_id`) REFERENCES `ai_task`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI生成结果资源表';