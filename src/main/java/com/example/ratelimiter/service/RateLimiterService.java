package com.example.ratelimiter.service;

import com.example.ratelimiter.annotation.RateLimiter;
import com.example.ratelimiter.model.RateLimiterResult;

/**
 * 限流服务接口
 * 
 * @author Rate Limiter Framework
 */
public interface RateLimiterService {

    /**
     * 执行限流检查
     * 
     * @param key 限流key
     * @param rateLimiter 限流注解配置
     * @return 限流结果
     */
    RateLimiterResult checkRateLimit(String key, RateLimiter rateLimiter);

    /**
     * 执行限流检查（使用默认配置）
     * 
     * @param key 限流key
     * @return 限流结果
     */
    RateLimiterResult checkRateLimit(String key);

    /**
     * 清理过期的限流数据
     */
    void cleanup();
}