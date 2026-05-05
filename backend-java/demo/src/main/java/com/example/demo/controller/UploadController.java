package com.example.demo.controller;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

@RestController
@RequestMapping("/api/upload")
public class UploadController {

    /**
     * 上传音频文件（wav/mp3），保存到 ai-worker/uploads/audio/ 目录
     */
    @PostMapping("/audio")
    public ResponseEntity<Map<String, Object>> uploadAudio(
            @RequestParam("file") MultipartFile file,
            HttpServletRequest request) {

        Map<String, Object> result = new HashMap<>();

        if (file.isEmpty()) {
            result.put("code", 1);
            result.put("msg", "文件为空");
            return ResponseEntity.badRequest().body(result);
        }

        String originalName = file.getOriginalFilename();
        if (originalName == null || originalName.isEmpty()) {
            originalName = "audio.wav";
        }

        // 只允许 wav 和 mp3
        String ext = "";
        int dot = originalName.lastIndexOf('.');
        if (dot >= 0) {
            ext = originalName.substring(dot).toLowerCase();
        }
        if (!ext.equals(".wav") && !ext.equals(".mp3")) {
            result.put("code", 1);
            result.put("msg", "仅支持 wav 和 mp3 格式");
            return ResponseEntity.badRequest().body(result);
        }

        // 构造保存路径: ai-worker/uploads/audio/YYYYMMDD/ 目录下
        String uploadBase = System.getProperty("user.dir")
                .replace("backend-java\\demo", "ai-worker\\uploads\\audio")
                .replace("backend-java/demo", "ai-worker/uploads/audio");

        String dateDir = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        File destDir = new File(uploadBase, dateDir);
        if (!destDir.exists()) {
            destDir.mkdirs();
        }

        // 生成唯一文件名：时间戳 + 原文件名
        String saveName = System.currentTimeMillis() + "_" + originalName;
        File destFile = new File(destDir, saveName);

        try {
            file.transferTo(destFile);
        } catch (IOException e) {
            result.put("code", 1);
            result.put("msg", "文件保存失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(result);
        }

        String urlPath = "/uploads/audio/" + dateDir + "/" + saveName;

        result.put("code", 0);
        result.put("msg", "上传成功");
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("url", urlPath);
        data.put("fileName", originalName);
        data.put("size", file.getSize());
        result.put("data", data);
        return ResponseEntity.ok(result);
    }
}
