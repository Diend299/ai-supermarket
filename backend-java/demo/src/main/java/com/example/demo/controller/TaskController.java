package com.example.demo.controller;

import com.example.demo.config.JwtUtil;
import com.example.demo.dto.*;
import com.example.demo.service.AiTaskService;
import com.example.demo.service.TaskSseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;

@RestController
@RequestMapping("/api/task")
@RequiredArgsConstructor
@Tag(name = "AI任务管理", description = "AI任务创建、查询、结果获取接口")
public class TaskController {

    private final AiTaskService aiTaskService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromToken(String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("未登录或token无效");
        }
        String token = authHeader.substring(7);
        return jwtUtil.extractUserId(token);
    }

    @PostMapping("/create")
    @Operation(summary = "创建AI生成任务")
    public Result<TaskResponse> createTask(
            @RequestHeader("Authorization") String authHeader,
            @Valid @RequestBody CreateTaskRequest request) {
        Long userId = getUserIdFromToken(authHeader);
        TaskResponse response = aiTaskService.createTask(userId, request);
        return Result.success(response);
    }

    @GetMapping("/{taskId}")
    @Operation(summary = "查询任务进度/详情")
    public Result<TaskDetailResponse> getTaskDetail(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable Long taskId) {
        Long userId = getUserIdFromToken(authHeader);
        TaskDetailResponse response = aiTaskService.getTaskDetail(taskId, userId);
        return Result.success(response);
    }

    @GetMapping("/{taskId}/result")
    @Operation(summary = "获取任务结果资源")
    public Result<TaskResultResponse> getTaskResult(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable Long taskId) {
        Long userId = getUserIdFromToken(authHeader);
        TaskResultResponse response = aiTaskService.getTaskResult(taskId, userId);
        return Result.success(response);
    }

    @GetMapping("/list")
    @Operation(summary = "获取用户的所有任务列表")
    public Result<List<TaskListResponse>> getUserTasks(
            @RequestHeader("Authorization") String authHeader) {
        Long userId = getUserIdFromToken(authHeader);
        List<TaskListResponse> response = aiTaskService.getUserTasks(userId);
        return Result.success(response);
    }

    private String extractToken(@RequestHeader(value = "Authorization", required = false) String authHeader,
                                @RequestParam(value = "token", required = false) String tokenParam) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            return authHeader.substring(7);
        }
        if (tokenParam != null && !tokenParam.isEmpty()) {
            return tokenParam;
        }
        throw new RuntimeException("未登录或token无效");
    }

    @GetMapping(value = "/{taskId}/subscribe", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter subscribe(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            @RequestParam(value = "token", required = false) String tokenParam,
            @PathVariable Long taskId) {
        String token = extractToken(authHeader, tokenParam);
        Long userId = jwtUtil.extractUserId(token);
        aiTaskService.getTaskDetail(taskId, userId);
        return aiTaskService.subscribeTask(taskId);
    }

    @ExceptionHandler(RuntimeException.class)
    public Result<Void> handleRuntimeException(RuntimeException e) {
        return Result.error(e.getMessage());
    }
}
