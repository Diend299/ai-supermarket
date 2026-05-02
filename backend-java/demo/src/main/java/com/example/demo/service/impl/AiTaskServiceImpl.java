package com.example.demo.service.impl;

import com.example.demo.dto.*;
import com.example.demo.entity.AiTask;
import com.example.demo.entity.AiResultResource;
import com.example.demo.mapper.AiTaskMapper;
import com.example.demo.mapper.AiResultResourceMapper;
import com.example.demo.service.AiTaskService;
import com.example.demo.service.TaskSseService;
import com.example.demo.util.RedisKeyConstant;
import com.example.demo.util.RedisUtil;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class AiTaskServiceImpl implements AiTaskService {

    private final AiTaskMapper aiTaskMapper;
    private final AiResultResourceMapper resourceMapper;
    private final RedisUtil redisUtil;
    private final ObjectMapper objectMapper;
    private final TaskSseService taskSseService;

    @Override
    @Transactional
    public TaskResponse createTask(Long userId, CreateTaskRequest request) {
        String taskType = request.getTaskType();
        Map<String, Object> params = request.getParams();

        AiTask task = new AiTask();
        task.setUserId(userId);
        task.setTaskType(taskType);
        task.setTaskStatus(0);
        task.setProgress(0);

        try {
            task.setParams(objectMapper.writeValueAsString(params));
        } catch (JsonProcessingException e) {
            throw new RuntimeException("任务参数序列化失败", e);
        }

        task.setConsumePoints(10);
        task.setConsumeBalance(BigDecimal.ZERO);

        aiTaskMapper.insert(task);
        Long taskId = task.getId();
        log.info("AI任务已创建: taskId={}, type={}", taskId, taskType);

        Map<String, Object> queueMessage = new HashMap<>();
        queueMessage.put("taskId", taskId);
        queueMessage.put("userId", userId);
        queueMessage.put("taskType", taskType);
        queueMessage.put("params", params);

        try {
            String jsonMessage = objectMapper.writeValueAsString(queueMessage);
            redisUtil.rightPushString(RedisKeyConstant.AI_TASK_QUEUE, jsonMessage);
            log.info("任务已推入Redis队列: taskId={}", taskId);
        } catch (JsonProcessingException e) {
            log.error("队列消息序列化失败: taskId={}", taskId, e);
            throw new RuntimeException("队列消息序列化失败", e);
        }

        return new TaskResponse(taskId, task.getTaskStatus());
    }

    @Override
    public TaskDetailResponse getTaskDetail(Long taskId, Long userId) {
        AiTask task = aiTaskMapper.findById(taskId);
        if (task == null) {
            throw new RuntimeException("任务不存在");
        }
        if (!task.getUserId().equals(userId)) {
            throw new RuntimeException("无权访问该任务");
        }

        return new TaskDetailResponse(
                task.getId(),
                task.getTaskType(),
                task.getTaskStatus(),
                task.getProgress(),
                task.getErrorMsg(),
                task.getCreatedAt(),
                task.getFinishedAt()
        );
    }

    @Override
    public TaskResultResponse getTaskResult(Long taskId, Long userId) {
        AiTask task = aiTaskMapper.findById(taskId);
        if (task == null) {
            throw new RuntimeException("任务不存在");
        }
        if (!task.getUserId().equals(userId)) {
            throw new RuntimeException("无权访问该任务");
        }
        if (task.getTaskStatus() != 2) {
            throw new RuntimeException("任务尚未完成");
        }

        List<AiResultResource> resources = resourceMapper.findByTaskId(taskId);
        List<TaskResultResponse.ResourceItem> items = resources.stream()
                .map(r -> new TaskResultResponse.ResourceItem(
                        r.getResourceType(),
                        r.getResourceUrl(),
                        r.getContentText(),
                        r.getCoverUrl(),
                        r.getDuration()
                ))
                .collect(Collectors.toList());

        return new TaskResultResponse(taskId, task.getTaskStatus(), items);
    }

    @Override
    public SseEmitter subscribeTask(Long taskId) {
        return taskSseService.register(taskId);
    }

    @Override
    public List<TaskListResponse> getUserTasks(Long userId) {
        List<AiTask> tasks = aiTaskMapper.findByUserId(userId);
        return tasks.stream()
                .map(task -> new TaskListResponse(
                        task.getId(),
                        task.getTaskType(),
                        task.getTaskStatus(),
                        task.getProgress(),
                        task.getCreatedAt(),
                        task.getFinishedAt()
                ))
                .collect(Collectors.toList());
    }
}
