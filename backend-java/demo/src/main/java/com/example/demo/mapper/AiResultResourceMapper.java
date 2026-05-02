package com.example.demo.mapper;

import com.example.demo.entity.AiResultResource;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface AiResultResourceMapper {

    List<AiResultResource> findByTaskId(@Param("taskId") Long taskId);

    int insert(AiResultResource resource);
}
