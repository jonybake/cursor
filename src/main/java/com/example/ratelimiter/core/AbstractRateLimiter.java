package com.example.ratelimiter.core;

import com.example.ratelimiter.config.RateLimiterProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 限流器抽象基类
 * 
 * @author Rate Limiter Framework
 */
public abstract class AbstractRateLimiter implements RateLimiter {
    
    protected final Logger logger = LoggerFactory.getLogger(getClass());
    
    protected final RateLimiterProperties properties;
    
    public AbstractRateLimiter(RateLimiterProperties properties) {
        this.properties = properties;
    }
    
    @Override
    public boolean tryAcquire(String key) {
        return tryAcquire(key, 1);
    }
    
    @Override
    public boolean acquire(String key) {
        return acquire(key, 1);
    }
    
    @Override
    public boolean acquire(String key, int permits) {
        long timeout = properties.getTimeout();
        long startTime = System.currentTimeMillis();
        
        while (System.currentTimeMillis() - startTime < timeout) {
            if (tryAcquire(key, permits)) {
                return true;
            }
            
            try {
                Thread.sleep(properties.getRetryInterval());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                logger.warn("Rate limiter acquire interrupted for key: {}", key);
                return false;
            }
        }
        
        logger.warn("Rate limiter acquire timeout for key: {}", key);
        return false;
    }
    
    /**
     * 验证限流键
     * 
     * @param key 限流键
     */
    protected void validateKey(String key) {
        if (key == null || key.trim().isEmpty()) {
            throw new IllegalArgumentException("Rate limiter key cannot be null or empty");
        }
    }
    
    /**
     * 验证许可数量
     * 
     * @param permits 许可数量
     */
    protected void validatePermits(int permits) {
        if (permits <= 0) {
            throw new IllegalArgumentException("Permits must be positive");
        }
    }
}