package com.example.ratelimiter.autoconfigure;

import com.example.ratelimiter.config.RateLimiterConfig;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/**
 * 限流器自动配置类
 * 
 * @author Rate Limiter Framework
 */
@Configuration
@ConditionalOnClass(name = "com.example.ratelimiter.core.RateLimiter")
@ConditionalOnMissingBean(name = "rateLimiterManager")
@EnableConfigurationProperties
@Import(RateLimiterConfig.class)
public class RateLimiterAutoConfiguration {
    
    // 自动配置逻辑已通过 @Import 导入到 RateLimiterConfig 中
}