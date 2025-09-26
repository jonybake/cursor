package com.example.ratelimiter.algorithm;

import com.google.common.util.concurrent.RateLimiter;
import org.springframework.stereotype.Component;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

/**
 * 基于令牌桶算法的限流器
 * 
 * @author Rate Limiter Framework
 */
@Component("tokenBucketRateLimiter")
public class TokenBucketRateLimiter implements RateLimiterAlgorithm {

    /**
     * 限流器缓存
     */
    private final ConcurrentHashMap<String, RateLimiter> rateLimiters = new ConcurrentHashMap<>();

    /**
     * 默认配置
     */
    private static final int DEFAULT_PERMITS_PER_SECOND = 10;
    private static final int DEFAULT_BURST_CAPACITY = 20;

    @Override
    public boolean tryAcquire(String key, int permits) {
        RateLimiter rateLimiter = getOrCreateRateLimiter(key, DEFAULT_PERMITS_PER_SECOND, DEFAULT_BURST_CAPACITY);
        return rateLimiter.tryAcquire(permits);
    }

    @Override
    public boolean tryAcquire(String key) {
        return tryAcquire(key, 1);
    }

    @Override
    public long getAvailablePermits(String key) {
        RateLimiter rateLimiter = rateLimiters.get(key);
        if (rateLimiter == null) {
            return 0;
        }
        return (long) rateLimiter.getRate();
    }

    @Override
    public void reset(String key) {
        rateLimiters.remove(key);
    }

    @Override
    public void cleanup() {
        // 清理长时间未使用的限流器
        rateLimiters.entrySet().removeIf(entry -> {
            RateLimiter rateLimiter = entry.getValue();
            // 如果限流器在1分钟内没有被使用，则清理
            return System.currentTimeMillis() - getLastAccessTime(rateLimiter) > 60000;
        });
    }

    /**
     * 获取或创建限流器
     */
    private RateLimiter getOrCreateRateLimiter(String key, int permitsPerSecond, int burstCapacity) {
        return rateLimiters.computeIfAbsent(key, k -> {
            // 创建令牌桶限流器
            RateLimiter rateLimiter = RateLimiter.create(permitsPerSecond);
            // 预热，允许突发请求
            rateLimiter.tryAcquire(burstCapacity);
            return rateLimiter;
        });
    }

    /**
     * 获取最后访问时间（简化实现）
     */
    private long getLastAccessTime(RateLimiter rateLimiter) {
        // 这里简化实现，实际应该记录最后访问时间
        return System.currentTimeMillis();
    }

    /**
     * 创建自定义配置的限流器
     */
    public RateLimiter createRateLimiter(String key, int permitsPerSecond, int burstCapacity) {
        RateLimiter rateLimiter = RateLimiter.create(permitsPerSecond);
        // 预热
        rateLimiter.tryAcquire(burstCapacity);
        rateLimiters.put(key, rateLimiter);
        return rateLimiter;
    }

    /**
     * 尝试获取许可（带超时）
     */
    public boolean tryAcquire(String key, int permits, long timeout, TimeUnit unit) {
        RateLimiter rateLimiter = getOrCreateRateLimiter(key, DEFAULT_PERMITS_PER_SECOND, DEFAULT_BURST_CAPACITY);
        return rateLimiter.tryAcquire(permits, timeout, unit);
    }
}