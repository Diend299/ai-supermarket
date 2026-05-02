package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TaskDetailResponse {
    private Long taskId;
    private String taskType;
    private Integer taskStatus;
    private Integer progress;
    private String errorMsg;
    private LocalDateTime createdAt;
    private LocalDateTime finishedAt;
}
