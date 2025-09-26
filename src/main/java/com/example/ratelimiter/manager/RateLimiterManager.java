package com.example.ratelimiter.manager;

import com.example.ratelimiter.algorithm.FixedWindowRateLimiter;
import com.example.ratelimiter.algorithm.SlidingWindowRateLimiter;
import com.example.ratelimiter.algorithm.TokenBucketRateLimiter;
import com.example.ratelimiter.config.RateLimiterProperties;
import com.example.ratelimiter.core.RateLimiter;
import com.example.ratelimiter.core.RateLimiterType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * 限流器管理器
 * 
 * @author Rate Limiter Framework
 */
@Component
public class RateLimiterManager {
    
    private static final Logger logger = LoggerFactory.getLogger(RateLimiterManager.class);
    
    private final Map<RateLimiterType, RateLimiter> rateLimiters;
    private final RateLimiterProperties properties;
    
    public RateLimiterManager(
            TokenBucketRateLimiter tokenBucketRateLimiter,
            SlidingWindowRateLimiter slidingWindowRateLimiter,
            FixedWindowRateLimiter fixedWindowRateLimiter,
            RateLimiterProperties properties) {
        
        this.properties = properties;
        this.rateLimiters = new HashMap<>();
        
        rateLimiters.put(RateLimiterType.TOKEN_BUCKET, tokenBucketRateLimiter);
        rateLimiters.put(RateLimiterType.SLIDING_WINDOW, slidingWindowRateLimiter);
        rateLimiters.put(RateLimiterType.FIXED_WINDOW, fixedWindowRateLimiter);
        
        logger.info("Rate limiter manager initialized with {} limiters", rateLimiters.size());
    }
    
    /**
     * 获取指定类型的限流器
     * 
     * @param type 限流器类型
     * @return 限流器实例
     */
    public RateLimiter getRateLimiter(RateLimiterType type) {
        RateLimiter rateLimiter = rateLimiters.get(type);
        if (rateLimiter == null) {
            throw new IllegalArgumentException("Unsupported rate limiter type: " + type);
        }
        return rateLimiter;
    }
    
    /**
     * 获取默认限流器
     * 
     * @return 默认限流器实例
     */
    public RateLimiter getDefaultRateLimiter() {
        RateLimiterType defaultType = RateLimiterType.fromValue(properties.getDefaultType());
        return getRateLimiter(defaultType);
    }
    
    /**
     * 获取所有限流器
     * 
     * @return 限流器映射
     */
    public Map<RateLimiterType, RateLimiter> getAllRateLimiters() {
        return new HashMap<>(rateLimiters);
    }
    
    /**
     * 检查限流器是否可用
     * 
     * @param type 限流器类型
     * @return 是否可用
     */
    public boolean isRateLimiterAvailable(RateLimiterType type) {
        return rateLimiters.containsKey(type);
    }
    
    /**
     * 获取限流器统计信息
     * 
     * @return 统计信息
     */
    public Map<String, Object> getStatistics() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalLimiters", rateLimiters.size());
        stats.put("availableTypes", rateLimiters.keySet());
        stats.put("defaultType", properties.getDefaultType());
        stats.put("enabled", properties.isEnabled());
        return stats;
    }
}