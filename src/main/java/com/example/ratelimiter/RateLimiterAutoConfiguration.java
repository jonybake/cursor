package com.example.ratelimiter;

import com.example.ratelimiter.algorithm.RateLimiterAlgorithm;
import com.example.ratelimiter.algorithm.SlidingWindowRateLimiter;
import com.example.ratelimiter.algorithm.TokenBucketRateLimiter;
import com.example.ratelimiter.aspect.RateLimiterAspect;
import com.example.ratelimiter.config.RateLimiterProperties;
import com.example.ratelimiter.service.RateLimiterService;
import com.example.ratelimiter.service.impl.LocalRateLimiterService;
import com.example.ratelimiter.service.impl.RedisRateLimiterService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.core.RedisTemplate;

/**
 * 限流框架自动配置类
 * 
 * @author Rate Limiter Framework
 */
@Configuration
@EnableConfigurationProperties(RateLimiterProperties.class)
@ConditionalOnClass(RateLimiterService.class)
public class RateLimiterAutoConfiguration {

    /**
     * 令牌桶限流算法
     */
    @Bean
    @ConditionalOnMissingBean(name = "tokenBucketRateLimiter")
    public RateLimiterAlgorithm tokenBucketRateLimiter() {
        return new TokenBucketRateLimiter();
    }

    /**
     * 滑动窗口限流算法
     */
    @Bean
    @ConditionalOnMissingBean(name = "slidingWindowRateLimiter")
    public RateLimiterAlgorithm slidingWindowRateLimiter() {
        return new SlidingWindowRateLimiter();
    }

    /**
     * 本地限流服务
     */
    @Bean
    @ConditionalOnMissingBean
    @ConditionalOnProperty(name = "rate-limiter.type", havingValue = "local", matchIfMissing = true)
    public RateLimiterService localRateLimiterService(RateLimiterProperties properties) {
        return new LocalRateLimiterService(properties);
    }

    /**
     * Redis分布式限流服务
     */
    @Bean
    @ConditionalOnMissingBean
    @ConditionalOnProperty(name = "rate-limiter.type", havingValue = "redis")
    @ConditionalOnClass(RedisTemplate.class)
    public RateLimiterService redisRateLimiterService(RedisTemplate<String, Object> redisTemplate, 
                                                      RateLimiterProperties properties) {
        return new RedisRateLimiterService(redisTemplate, properties);
    }

    /**
     * 限流切面
     */
    @Bean
    @ConditionalOnMissingBean
    public RateLimiterAspect rateLimiterAspect(RateLimiterService rateLimiterService) {
        return new RateLimiterAspect(rateLimiterService);
    }
}