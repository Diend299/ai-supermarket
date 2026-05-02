package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TaskListResponse {
    private Long taskId;
    private String taskType;
    private Integer taskStatus;
    private Integer progress;
    private LocalDateTime createdAt;
    private LocalDateTime finishedAt;
}
