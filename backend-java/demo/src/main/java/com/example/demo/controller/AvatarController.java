package com.example.demo.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.File;
import java.util.*;

@RestController
@RequestMapping("/api/avatar")
public class AvatarController {

    /**
     * 获取可用的数字人列表
     * 自动扫描 ai-worker/avatar/Wav2Lip/avatars/ 下的文件夹
     */
    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> listAvatars() {
        // 构造 avatars 目录路径（与 WebConfig 中一致）
        String avatarDir = System.getProperty("user.dir")
                .replace("backend-java\\demo", "ai-worker\\avatar\\Wav2Lip\\avatars")
                .replace("backend-java/demo", "ai-worker/avatar/Wav2Lip/avatars");

        List<Map<String, Object>> avatars = new ArrayList<>();
        File dir = new File(avatarDir);
        if (dir.exists() && dir.isDirectory()) {
            File[] subDirs = dir.listFiles(File::isDirectory);
            if (subDirs != null) {
                for (File sub : subDirs) {
                    String name = sub.getName();
                    // 查找文件夹中的 png 作为缩略图
                    String thumbUrl = null;
                    File[] pngFiles = sub.listFiles((f, fn) -> fn.toLowerCase().endsWith(".png"));
                    if (pngFiles != null && pngFiles.length > 0) {
                        thumbUrl = "/avatar/" + name + "/" + pngFiles[0].getName();
                    }

                    // 查找文件夹中的 mp4 作为参考视频
                    List<String> videos = new ArrayList<>();
                    File[] mp4Files = sub.listFiles((f, fn) -> fn.toLowerCase().endsWith(".mp4"));
                    if (mp4Files != null) {
                        for (File mp4 : mp4Files) {
                            videos.add(mp4.getName());
                        }
                    }

                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("id", name);
                    item.put("name", name);
                    item.put("thumbnail", thumbUrl != null ? thumbUrl : "");
                    item.put("videos", videos);
                    avatars.add(item);
                }
            }
        }

        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("data", avatars);
        return ResponseEntity.ok(result);
    }
}
