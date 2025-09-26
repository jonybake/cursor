package com.example.ratelimiter.config;

import com.example.ratelimiter.algorithm.FixedWindowRateLimiter;
import com.example.ratelimiter.algorithm.SlidingWindowRateLimiter;
import com.example.ratelimiter.algorithm.TokenBucketRateLimiter;
import com.example.ratelimiter.core.RateLimiter;
import com.example.ratelimiter.core.RateLimiterType;
import com.example.ratelimiter.manager.RateLimiterManager;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 限流器配置类
 * 
 * @author Rate Limiter Framework
 */
@Configuration
@EnableConfigurationProperties(RateLimiterProperties.class)
@ConditionalOnProperty(prefix = "rate-limiter", name = "enabled", havingValue = "true", matchIfMissing = true)
public class RateLimiterConfig {
    
    @Bean
    public TokenBucketRateLimiter tokenBucketRateLimiter(RateLimiterProperties properties) {
        return new TokenBucketRateLimiter(properties);
    }
    
    @Bean
    public SlidingWindowRateLimiter slidingWindowRateLimiter(RateLimiterProperties properties) {
        return new SlidingWindowRateLimiter(properties);
    }
    
    @Bean
    public FixedWindowRateLimiter fixedWindowRateLimiter(RateLimiterProperties properties) {
        return new FixedWindowRateLimiter(properties);
    }
    
    @Bean
    public RateLimiterManager rateLimiterManager(
            TokenBucketRateLimiter tokenBucketRateLimiter,
            SlidingWindowRateLimiter slidingWindowRateLimiter,
            FixedWindowRateLimiter fixedWindowRateLimiter,
            RateLimiterProperties properties) {
        return new RateLimiterManager(
                tokenBucketRateLimiter,
                slidingWindowRateLimiter,
                fixedWindowRateLimiter,
                properties
        );
    }
}