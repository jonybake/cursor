package com.example.ratelimiter.demo.controller;

import com.example.ratelimiter.annotation.RateLimiter;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 限流测试控制器
 * 
 * @author Rate Limiter Framework
 */
@RestController
@RequestMapping("/api/rate-limiter")
@RateLimiter(
    algorithm = RateLimiter.Algorithm.TOKEN_BUCKET,
    permitsPerSecond = 2,
    burstCapacity = 5,
    message = "类级别限流：请求过于频繁"
)
public class RateLimiterTestController {

    /**
     * 基础限流测试 - 使用默认配置
     */
    @GetMapping("/basic")
    @RateLimiter
    public Map<String, Object> basicTest() {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "Basic rate limit test passed");
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 令牌桶算法限流测试
     */
    @GetMapping("/token-bucket")
    @RateLimiter(
        algorithm = RateLimiter.Algorithm.TOKEN_BUCKET,
        permitsPerSecond = 5,
        burstCapacity = 10,
        message = "令牌桶限流：请求过于频繁"
    )
    public Map<String, Object> tokenBucketTest() {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "Token bucket rate limit test passed");
        result.put("algorithm", "TOKEN_BUCKET");
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 滑动窗口算法限流测试
     */
    @GetMapping("/sliding-window")
    @RateLimiter(
        algorithm = RateLimiter.Algorithm.SLIDING_WINDOW,
        windowSize = 30,
        windowPermits = 20,
        message = "滑动窗口限流：请求过于频繁"
    )
    public Map<String, Object> slidingWindowTest() {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "Sliding window rate limit test passed");
        result.put("algorithm", "SLIDING_WINDOW");
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 基于用户ID的限流测试
     */
    @GetMapping("/user/{userId}")
    @RateLimiter(
        key = "#userId",
        algorithm = RateLimiter.Algorithm.TOKEN_BUCKET,
        permitsPerSecond = 3,
        burstCapacity = 5,
        message = "用户限流：您的请求过于频繁"
    )
    public Map<String, Object> userBasedTest(@PathVariable String userId) {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "User-based rate limit test passed");
        result.put("userId", userId);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 基于方法参数的限流测试
     */
    @PostMapping("/param-based")
    @RateLimiter(
        key = "#requestId + ':' + #action",
        algorithm = RateLimiter.Algorithm.SLIDING_WINDOW,
        windowSize = 60,
        windowPermits = 10,
        message = "参数限流：该操作的请求过于频繁"
    )
    public Map<String, Object> paramBasedTest(@RequestParam String requestId, 
                                            @RequestParam String action) {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "Parameter-based rate limit test passed");
        result.put("requestId", requestId);
        result.put("action", action);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 类级别限流测试
     */
    @GetMapping("/class-level")
    public Map<String, Object> classLevelTest() {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "Class-level rate limit test passed");
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 无限流测试（用于对比）
     */
    @GetMapping("/no-limit")
    public Map<String, Object> noLimitTest() {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "No rate limit test passed");
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
}