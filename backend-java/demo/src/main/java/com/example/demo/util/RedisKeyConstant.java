package com.example.demo.util;

/**
 * Redis Key 常量管理
 */
public class RedisKeyConstant {

    /** AI任务队列 - 使用List结构 */
    public static final String AI_TASK_QUEUE = "ai:task:queue";

    /** AI任务信息缓存（用于高频查询） */
    public static final String AI_TASK_INFO = "ai:task:info:";

    /**
     * 获取指定任务的缓存Key
     */
    public static String getTaskInfoKey(Long taskId) {
        return AI_TASK_INFO + taskId;
    }
}
