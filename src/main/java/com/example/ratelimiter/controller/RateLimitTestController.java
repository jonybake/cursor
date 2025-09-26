package com.example.ratelimiter.controller;

import com.example.ratelimiter.annotation.RateLimit;
import com.example.ratelimiter.core.RateLimiterType;
import com.example.ratelimiter.model.RateLimitResponse;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 限流测试控制器
 * 
 * @author Rate Limiter Framework
 */
@RestController
@RequestMapping("/api/rate-limit")
public class RateLimitTestController {
    
    /**
     * 令牌桶限流测试
     */
    @GetMapping("/token-bucket")
    @RateLimit(
            key = "#userId",
            type = RateLimiterType.TOKEN_BUCKET,
            capacity = 10,
            refillRate = 2,
            refillPeriod = 1000
    )
    public Map<String, Object> tokenBucketTest(@RequestParam String userId) {
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "Token bucket rate limit test passed");
        result.put("userId", userId);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
    
    /**
     * 滑动窗口限流测试
     */
    @GetMapping("/sliding-window")
    @RateLimit(
            key = "#ip",
            type = RateLimiterType.SLIDING_WINDOW,
            capacity = 5,
            windowSize = 10000
    )
    public Map<String, Object> slidingWindowTest(@RequestParam String ip) {
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "Sliding window rate limit test passed");
        result.put("ip", ip);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
    
    /**
     * 固定窗口限流测试
     */
    @GetMapping("/fixed-window")
    @RateLimit(
            key = "#apiKey",
            type = RateLimiterType.FIXED_WINDOW,
            capacity = 3,
            windowSize = 5000
    )
    public Map<String, Object> fixedWindowTest(@RequestParam String apiKey) {
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "Fixed window rate limit test passed");
        result.put("apiKey", apiKey);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
    
    /**
     * 阻塞式限流测试
     */
    @GetMapping("/blocking")
    @RateLimit(
            key = "#requestId",
            type = RateLimiterType.TOKEN_BUCKET,
            capacity = 2,
            refillRate = 1,
            refillPeriod = 2000,
            blocking = true,
            timeout = 10000
    )
    public Map<String, Object> blockingTest(@RequestParam String requestId) {
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "Blocking rate limit test passed");
        result.put("requestId", requestId);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
    
    /**
     * 多许可消费测试
     */
    @GetMapping("/multi-permit")
    @RateLimit(
            key = "#resourceId",
            type = RateLimiterType.TOKEN_BUCKET,
            capacity = 20,
            refillRate = 5,
            refillPeriod = 1000,
            permits = 3
    )
    public Map<String, Object> multiPermitTest(@RequestParam String resourceId) {
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "Multi-permit rate limit test passed");
        result.put("resourceId", resourceId);
        result.put("permits", 3);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
    
    /**
     * 健康检查
     */
    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "UP");
        result.put("service", "Rate Limiter Framework");
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
}