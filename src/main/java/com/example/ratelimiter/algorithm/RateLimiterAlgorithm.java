package com.example.ratelimiter.algorithm;

/**
 * 限流算法接口
 * 
 * @author Rate Limiter Framework
 */
public interface RateLimiterAlgorithm {

    /**
     * 尝试获取许可
     * 
     * @param key 限流key
     * @param permits 请求的许可数
     * @return 是否获取成功
     */
    boolean tryAcquire(String key, int permits);

    /**
     * 尝试获取许可（默认1个）
     * 
     * @param key 限流key
     * @return 是否获取成功
     */
    default boolean tryAcquire(String key) {
        return tryAcquire(key, 1);
    }

    /**
     * 获取剩余许可数
     * 
     * @param key 限流key
     * @return 剩余许可数
     */
    long getAvailablePermits(String key);

    /**
     * 重置限流器
     * 
     * @param key 限流key
     */
    void reset(String key);

    /**
     * 清理过期的key
     */
    void cleanup();
}