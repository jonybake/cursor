package com.example.ratelimiter.service.impl;

import com.example.ratelimiter.annotation.RateLimiter;
import com.example.ratelimiter.config.RateLimiterProperties;
import com.example.ratelimiter.model.RateLimiterResult;
import com.example.ratelimiter.service.RateLimiterService;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

/**
 * 本地限流服务实现
 * 
 * @author Rate Limiter Framework
 */
@Service
public class LocalRateLimiterService implements RateLimiterService {

    private final com.example.ratelimiter.algorithm.RateLimiterAlgorithm tokenBucketRateLimiter;
    private final com.example.ratelimiter.algorithm.RateLimiterAlgorithm slidingWindowRateLimiter;
    private final RateLimiterProperties properties;

    public LocalRateLimiterService(
            @Qualifier("tokenBucketRateLimiter") com.example.ratelimiter.algorithm.RateLimiterAlgorithm tokenBucketRateLimiter,
            @Qualifier("slidingWindowRateLimiter") com.example.ratelimiter.algorithm.RateLimiterAlgorithm slidingWindowRateLimiter,
            RateLimiterProperties properties) {
        this.tokenBucketRateLimiter = tokenBucketRateLimiter;
        this.slidingWindowRateLimiter = slidingWindowRateLimiter;
        this.properties = properties;
    }

    @Override
    public RateLimiterResult checkRateLimit(String key, RateLimiter rateLimiter) {
        com.example.ratelimiter.algorithm.RateLimiterAlgorithm algorithm = getAlgorithm(rateLimiter);
        
        // 应用配置
        applyConfiguration(algorithm, rateLimiter);
        
        boolean allowed = algorithm.tryAcquire(key);
        long remainingPermits = algorithm.getAvailablePermits(key);
        
        if (allowed) {
            return RateLimiterResult.success(remainingPermits, System.currentTimeMillis() + 60000);
        } else {
            return RateLimiterResult.failure(remainingPermits, System.currentTimeMillis() + 60000, 
                    rateLimiter.message());
        }
    }

    @Override
    public RateLimiterResult checkRateLimit(String key) {
        // 使用默认配置
        com.example.ratelimiter.algorithm.RateLimiterAlgorithm algorithm = getDefaultAlgorithm();
        boolean allowed = algorithm.tryAcquire(key);
        long remainingPermits = algorithm.getAvailablePermits(key);
        
        if (allowed) {
            return RateLimiterResult.success(remainingPermits, System.currentTimeMillis() + 60000);
        } else {
            return RateLimiterResult.failure(remainingPermits, System.currentTimeMillis() + 60000, 
                    "请求过于频繁，请稍后再试");
        }
    }

    @Override
    public void cleanup() {
        tokenBucketRateLimiter.cleanup();
        slidingWindowRateLimiter.cleanup();
    }

    /**
     * 获取限流算法
     */
    private com.example.ratelimiter.algorithm.RateLimiterAlgorithm getAlgorithm(RateLimiter rateLimiter) {
        switch (rateLimiter.algorithm()) {
            case TOKEN_BUCKET:
                return tokenBucketRateLimiter;
            case SLIDING_WINDOW:
                return slidingWindowRateLimiter;
            default:
                return getDefaultAlgorithm();
        }
    }

    /**
     * 获取默认限流算法
     */
    private com.example.ratelimiter.algorithm.RateLimiterAlgorithm getDefaultAlgorithm() {
        String algorithm = properties.getAlgorithm();
        if ("sliding-window".equals(algorithm)) {
            return slidingWindowRateLimiter;
        }
        return tokenBucketRateLimiter;
    }

    /**
     * 应用配置（这里简化实现，实际应该动态创建限流器）
     */
    private void applyConfiguration(com.example.ratelimiter.algorithm.RateLimiterAlgorithm algorithm, RateLimiter rateLimiter) {
        // 这里简化实现，实际应该根据配置动态创建限流器
        // 或者使用配置管理器来管理不同配置的限流器
    }
}