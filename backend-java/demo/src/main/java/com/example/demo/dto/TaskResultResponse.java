package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TaskResultResponse {
    private Long taskId;
    private Integer taskStatus;
    private List<ResourceItem> resources;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ResourceItem {
        private String resourceType;
        private String resourceUrl;
        private String contentText;
        private String coverUrl;
        private Integer duration;
    }
}
