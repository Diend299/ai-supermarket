package com.example.demo.util;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.ListOperations;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * Redis 工具封装
 */
@Component
@RequiredArgsConstructor
public class RedisUtil {

    private final RedisTemplate<String, Object> redisTemplate;

    /**
     * 纯字符串序列化的 RedisTemplate，用于跨语言（Python）队列通信
     * 避免 Jackson 的 DefaultTyping 注入 Java 类型信息
     */
    private final StringRedisTemplate stringRedisTemplate;

    // ==================== 通用操作 ====================

    public void set(String key, Object value) {
        redisTemplate.opsForValue().set(key, value);
    }

    public void set(String key, Object value, long timeout, TimeUnit unit) {
        redisTemplate.opsForValue().set(key, value, timeout, unit);
    }

    public Object get(String key) {
        return redisTemplate.opsForValue().get(key);
    }

    public Boolean delete(String key) {
        return redisTemplate.delete(key);
    }

    public Boolean hasKey(String key) {
        return redisTemplate.hasKey(key);
    }

    // ==================== List (队列)操作 ====================

    /**
     * 从右侧推入 JSON 字符串到队列 (RPUSH)
     * 使用 StringRedisTemplate 确保纯 JSON 格式，可跨语言消费
     */
    public Long rightPushString(String key, String jsonValue) {
        return stringRedisTemplate.opsForList().rightPush(key, jsonValue);
    }

    /**
     * 从左侧弹出队列 (LPOP)
     */
    public Object leftPop(String key) {
        ListOperations<String, Object> listOps = redisTemplate.opsForList();
        return listOps.leftPop(key);
    }

    /**
     * 阻塞式从左侧弹出队列 (BLPOP) - 用于Worker
     */
    public Object leftPop(String key, long timeout, TimeUnit unit) {
        ListOperations<String, Object> listOps = redisTemplate.opsForList();
        return listOps.leftPop(key, timeout, unit);
    }

    /**
     * 从左侧推入队列 (LPUSH)
     */
    public Long leftPush(String key, Object value) {
        ListOperations<String, Object> listOps = redisTemplate.opsForList();
        return listOps.leftPush(key, value);
    }

    /**
     * 获取队列长度
     */
    public Long listSize(String key) {
        ListOperations<String, Object> listOps = redisTemplate.opsForList();
        return listOps.size(key);
    }

    /**
     * 获取队列中所有元素
     */
    public List<Object> listRange(String key, long start, long end) {
        ListOperations<String, Object> listOps = redisTemplate.opsForList();
        return listOps.range(key, start, end);
    }
}
