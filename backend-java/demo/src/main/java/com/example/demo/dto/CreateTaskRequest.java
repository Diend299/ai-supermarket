package com.example.demo.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.Map;

@Data
public class CreateTaskRequest {

    @NotBlank(message = "任务类型不能为空")
    private String taskType;

    @NotNull(message = "任务参数不能为空")
    private Map<String, Object> params;
}
