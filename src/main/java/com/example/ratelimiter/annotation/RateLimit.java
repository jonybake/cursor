package com.example.ratelimiter.annotation;

import com.example.ratelimiter.core.RateLimiterType;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 限流注解
 * 
 * @author Rate Limiter Framework
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RateLimit {
    
    /**
     * 限流键，支持SpEL表达式
     */
    String key() default "";
    
    /**
     * 限流器类型
     */
    RateLimiterType type() default RateLimiterType.TOKEN_BUCKET;
    
    /**
     * 容量
     */
    long capacity() default 100;
    
    /**
     * 窗口大小（毫秒）
     */
    long windowSize() default 60000;
    
    /**
     * 令牌桶补充速率
     */
    long refillRate() default 10;
    
    /**
     * 令牌桶补充周期（毫秒）
     */
    long refillPeriod() default 1000;
    
    /**
     * 许可数量
     */
    int permits() default 1;
    
    /**
     * 是否阻塞等待
     */
    boolean blocking() default false;
    
    /**
     * 超时时间（毫秒）
     */
    long timeout() default 5000;
    
    /**
     * 限流失败时的消息
     */
    String message() default "Rate limit exceeded";
}