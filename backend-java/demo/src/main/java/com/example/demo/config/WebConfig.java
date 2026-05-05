package com.example.demo.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 映射 /uploads/** 到 ai-worker/uploads/ 目录
        // 这样 GPT-SoVITS 生成的音频文件可以通过 http://localhost:8080/uploads/audio/xxx.wav 访问
        String uploadPath = System.getProperty("user.dir")
                .replace("backend-java\\demo", "ai-worker\\uploads\\")
                .replace("backend-java/demo", "ai-worker/uploads/");
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:" + uploadPath);

        // 映射 /avatar/** 到 ai-worker/avatar/Wav2Lip/avatars/ 目录
        // 这样数字人缩略图可通过 http://localhost:8080/avatar/asuka/asuka.png 访问
        String avatarPath = System.getProperty("user.dir")
                .replace("backend-java\\demo", "ai-worker\\avatar\\Wav2Lip\\avatars\\")
                .replace("backend-java/demo", "ai-worker/avatar/Wav2Lip/avatars/");
        registry.addResourceHandler("/avatar/**")
                .addResourceLocations("file:" + avatarPath);
    }
}


