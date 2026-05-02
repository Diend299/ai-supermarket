package com.example.demo.service;

import com.example.demo.dto.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;

public interface AiTaskService {

    /**
     * 创建AI任务：写入数据库 → 推入Redis队列
     */
    TaskResponse createTask(Long userId, CreateTaskRequest request);

    /**
     * 查询任务状态/详情
     */
    TaskDetailResponse getTaskDetail(Long taskId, Long userId);

    /**
     * 查询任务结果资源
     */
    TaskResultResponse getTaskResult(Long taskId, Long userId);

    /**
     * 订阅任务状态 SSE 推送（替代轮询）
     */
    SseEmitter subscribeTask(Long taskId);

    /**
     * 获取用户的所有任务列表
     */
    List<TaskListResponse> getUserTasks(Long userId);
}
