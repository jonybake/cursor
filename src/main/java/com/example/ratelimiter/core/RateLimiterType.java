package com.example.ratelimiter.core;

/**
 * 限流器类型枚举
 * 
 * @author Rate Limiter Framework
 */
public enum RateLimiterType {
    
    /**
     * 令牌桶算法
     */
    TOKEN_BUCKET("token-bucket"),
    
    /**
     * 滑动窗口算法
     */
    SLIDING_WINDOW("sliding-window"),
    
    /**
     * 固定窗口算法
     */
    FIXED_WINDOW("fixed-window");
    
    private final String value;
    
    RateLimiterType(String value) {
        this.value = value;
    }
    
    public String getValue() {
        return value;
    }
    
    public static RateLimiterType fromValue(String value) {
        for (RateLimiterType type : values()) {
            if (type.value.equals(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException("Unknown rate limiter type: " + value);
    }
}