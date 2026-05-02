package com.example.demo.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * SSE 推送服务（基于 Redis Pub/Sub）
 * Worker 完成 → Redis Publish → Java Subscribe → SSE Push 到前端
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TaskSseService {

    private final StringRedisTemplate stringRedisTemplate;
    private final ObjectMapper objectMapper;

    /** 按 taskId 存储 SSE Emitter，用于推送任务完成通知 */
    private final Map<Long, SseEmitter> taskEmitters = new ConcurrentHashMap<>();

    /** 心跳线程 */
    private final ScheduledExecutorService heartbeatExecutor = Executors.newSingleThreadScheduledExecutor();

    /** Redis 订阅线程 */
    private volatile boolean running = true;

    @PostConstruct
    public void init() {
        // 启动 Redis 订阅（独立线程，避免阻塞 Tomcat 启动）
        Thread subscriber = new Thread(this::subscribeRedis, "redis-sse-subscriber");
        subscriber.setDaemon(true);
        subscriber.start();

        // 心跳保活
        heartbeatExecutor.scheduleAtFixedRate(this::heartbeat, 10, 10, TimeUnit.SECONDS);
    }

    @PreDestroy
    public void destroy() {
        running = false;
        heartbeatExecutor.shutdown();
    }

    /**
     * 订阅 Redis 频道 ai:task:notify
     */
    private void subscribeRedis() {
        // 先清理旧频道数据
        // 使用独立的 RedisConnection，因为 subscribe 是阻塞的
        try (var conn = stringRedisTemplate.getConnectionFactory().getConnection()) {
            conn.subscribe((message, pattern) -> {
                try {
                    String body = new String(message.getBody());
                    log.info("[SSE] Redis 收到通知: {}", body);

                    @SuppressWarnings("unchecked")
                    Map<String, Object> notify = objectMapper.readValue(body, Map.class);
                    Number taskIdNum = (Number) notify.get("taskId");
                    Long taskId = taskIdNum.longValue();
                    Integer status = (Integer) notify.get("status");

                    // 找到对应 taskId 的 SSE Emitter 推送
                    SseEmitter emitter = taskEmitters.get(taskId);
                    if (emitter != null) {
                        // 尝试推送完整结果（成功时获取 contentText）
                        if (status == 2) {
                            // 构建完整的推送数据
                            Map<String, Object> pushData = new java.util.HashMap<>();
                            pushData.put("taskId", taskId);
                            pushData.put("status", status);
                            pushData.put("type", "completed");
                            try {
                                emitter.send(SseEmitter.event()
                                        .name("task-completed")
                                        .data(objectMapper.writeValueAsString(pushData)));
                                log.info("[SSE] 已推送 taskId={} 成功通知", taskId);
                            } catch (IOException e) {
                                log.warn("[SSE] 推送失败 taskId={}, emitter已断开", taskId);
                                taskEmitters.remove(taskId);
                            }
                        } else if (status == 3) {
                            String errorMsg = (String) notify.get("errorMsg");
                            Map<String, Object> pushData = new java.util.HashMap<>();
                            pushData.put("taskId", taskId);
                            pushData.put("status", status);
                            pushData.put("type", "failed");
                            pushData.put("errorMsg", errorMsg);
                            try {
                                emitter.send(SseEmitter.event()
                                        .name("task-failed")
                                        .data(objectMapper.writeValueAsString(pushData)));
                            } catch (IOException e) {
                                taskEmitters.remove(taskId);
                            }
                        }
                    } else {
                        log.debug("[SSE] taskId={} 无前端监听，忽略通知", taskId);
                    }
                } catch (Exception e) {
                    log.error("[SSE] 处理通知异常", e);
                }
            }, "ai:task:notify".getBytes());
        } catch (Exception e) {
            log.error("[SSE] Redis 订阅连接异常，将在下次任务创建时重试", e);
        }
    }

    /**
     * 注册 SSE 连接（在创建任务时由 Controller 调用）
     */
    public SseEmitter register(Long taskId) {
        // 旧的 emitter 如果存在则先关闭
        SseEmitter old = taskEmitters.remove(taskId);
        if (old != null) {
            try { old.complete(); } catch (Exception ignored) {}
        }

        SseEmitter emitter = new SseEmitter(120_000L); // 2分钟超时
        taskEmitters.put(taskId, emitter);

        emitter.onCompletion(() -> {
            log.info("[SSE] taskId={} 连接完成", taskId);
            taskEmitters.remove(taskId);
        });
        emitter.onTimeout(() -> {
            log.info("[SSE] taskId={} 连接超时", taskId);
            taskEmitters.remove(taskId);
        });
        emitter.onError(e -> {
            log.warn("[SSE] taskId={} 连接错误: {}", taskId, e.getMessage());
            taskEmitters.remove(taskId);
        });

        return emitter;
    }

    /** 心跳保活 */
    private void heartbeat() {
        taskEmitters.forEach((taskId, emitter) -> {
            try {
                emitter.send(SseEmitter.event()
                        .name("heartbeat")
                        .data(""));
            } catch (IOException e) {
                taskEmitters.remove(taskId);
            }
        });
    }
}
