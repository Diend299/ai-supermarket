package com.example.demo.mapper;

import com.example.demo.entity.AiTask;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface AiTaskMapper {

    AiTask findById(@Param("id") Long id);

    List<AiTask> findByUserId(@Param("userId") Long userId);

    List<AiTask> findByStatus(@Param("status") Integer status);

    int insert(AiTask aiTask);

    int updateStatus(AiTask aiTask);

    int updateProgress(@Param("id") Long id, @Param("progress") Integer progress);
}
