package com.example.demo.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class AiResultResource {
    private Long id;
    private Long taskId;
    private String resourceType; // video/image/audio/text
    private String resourceUrl;
    private String contentText;  // 文本生成结果（text类型用）
    private String coverUrl;
    private Integer duration;
    private Long fileSize;
    private Integer status;      // 1=有效, 0=已删除
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
