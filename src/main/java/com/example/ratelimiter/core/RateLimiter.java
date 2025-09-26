package com.example.ratelimiter.core;

/**
 * 限流器核心接口
 * 
 * @author Rate Limiter Framework
 */
public interface RateLimiter {
    
    /**
     * 尝试获取许可
     * 
     * @param key 限流键
     * @return 是否获取成功
     */
    boolean tryAcquire(String key);
    
    /**
     * 尝试获取指定数量的许可
     * 
     * @param key 限流键
     * @param permits 许可数量
     * @return 是否获取成功
     */
    boolean tryAcquire(String key, int permits);
    
    /**
     * 获取许可（阻塞）
     * 
     * @param key 限流键
     * @return 是否获取成功
     */
    boolean acquire(String key);
    
    /**
     * 获取指定数量的许可（阻塞）
     * 
     * @param key 限流键
     * @param permits 许可数量
     * @return 是否获取成功
     */
    boolean acquire(String key, int permits);
    
    /**
     * 获取当前可用许可数
     * 
     * @param key 限流键
     * @return 可用许可数
     */
    long getAvailablePermits(String key);
    
    /**
     * 重置限流器
     * 
     * @param key 限流键
     */
    void reset(String key);
    
    /**
     * 获取限流器类型
     * 
     * @return 限流器类型
     */
    String getType();
}