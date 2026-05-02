package com.example.demo.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class AiTask {
    private Long id;
    private Long userId;
    private String taskType;
    private Integer taskStatus; // 0=排队中, 1=生成中, 2=成功, 3=失败
    private String params;      // JSON格式任务参数
    private Integer progress;   // 进度 0-100
    private String errorMsg;
    private Integer consumePoints;
    private BigDecimal consumeBalance;
    private LocalDateTime startedAt;
    private LocalDateTime finishedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
