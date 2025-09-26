package com.example.ratelimiter.annotation;

import java.lang.annotation.*;

/**
 * 限流注解
 * 
 * @author Rate Limiter Framework
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface RateLimiter {

    /**
     * 限流key，支持SpEL表达式
     * 例如：@RateLimiter(key = "#userId")
     */
    String key() default "";

    /**
     * 限流算法类型
     */
    Algorithm algorithm() default Algorithm.TOKEN_BUCKET;

    /**
     * 每秒允许的请求数（令牌桶算法）
     */
    int permitsPerSecond() default -1;

    /**
     * 突发请求数（令牌桶算法）
     */
    int burstCapacity() default -1;

    /**
     * 时间窗口大小（秒）（滑动窗口算法）
     */
    int windowSize() default -1;

    /**
     * 时间窗口内允许的请求数（滑动窗口算法）
     */
    int windowPermits() default -1;

    /**
     * 限流失败时的提示信息
     */
    String message() default "请求过于频繁，请稍后再试";

    /**
     * 限流失败时的HTTP状态码
     */
    int statusCode() default 429;

    /**
     * 限流算法枚举
     */
    enum Algorithm {
        /**
         * 令牌桶算法
         */
        TOKEN_BUCKET,
        
        /**
         * 滑动窗口算法
         */
        SLIDING_WINDOW
    }
}