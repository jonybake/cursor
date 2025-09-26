package com.example.ratelimiter.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import javax.validation.constraints.Min;
import javax.validation.constraints.NotNull;

/**
 * 限流器配置属性
 * 
 * @author Rate Limiter Framework
 */
@ConfigurationProperties(prefix = "rate-limiter")
@Validated
public class RateLimiterProperties {
    
    /**
     * 是否启用限流器
     */
    private boolean enabled = true;
    
    /**
     * 默认限流器类型
     */
    @NotNull
    private String defaultType = "token-bucket";
    
    /**
     * 默认容量
     */
    @Min(1)
    private long capacity = 100;
    
    /**
     * 默认窗口大小（毫秒）
     */
    @Min(1)
    private long windowSize = 60000; // 1分钟
    
    /**
     * 令牌桶补充速率
     */
    @Min(1)
    private long refillRate = 10;
    
    /**
     * 令牌桶补充周期（毫秒）
     */
    @Min(1)
    private long refillPeriod = 1000; // 1秒
    
    /**
     * 最大键数量
     */
    @Min(1)
    private int maxKeys = 10000;
    
    /**
     * 键过期时间（分钟）
     */
    @Min(1)
    private int expireMinutes = 60;
    
    /**
     * 获取许可超时时间（毫秒）
     */
    @Min(1)
    private long timeout = 5000;
    
    /**
     * 重试间隔（毫秒）
     */
    @Min(1)
    private long retryInterval = 100;
    
    /**
     * 是否启用分布式限流
     */
    private boolean distributed = false;
    
    /**
     * Redis键前缀
     */
    private String redisKeyPrefix = "rate_limiter:";
    
    /**
     * 是否启用监控
     */
    private boolean monitoring = true;
    
    // Getters and Setters
    public boolean isEnabled() {
        return enabled;
    }
    
    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }
    
    public String getDefaultType() {
        return defaultType;
    }
    
    public void setDefaultType(String defaultType) {
        this.defaultType = defaultType;
    }
    
    public long getCapacity() {
        return capacity;
    }
    
    public void setCapacity(long capacity) {
        this.capacity = capacity;
    }
    
    public long getWindowSize() {
        return windowSize;
    }
    
    public void setWindowSize(long windowSize) {
        this.windowSize = windowSize;
    }
    
    public long getRefillRate() {
        return refillRate;
    }
    
    public void setRefillRate(long refillRate) {
        this.refillRate = refillRate;
    }
    
    public long getRefillPeriod() {
        return refillPeriod;
    }
    
    public void setRefillPeriod(long refillPeriod) {
        this.refillPeriod = refillPeriod;
    }
    
    public int getMaxKeys() {
        return maxKeys;
    }
    
    public void setMaxKeys(int maxKeys) {
        this.maxKeys = maxKeys;
    }
    
    public int getExpireMinutes() {
        return expireMinutes;
    }
    
    public void setExpireMinutes(int expireMinutes) {
        this.expireMinutes = expireMinutes;
    }
    
    public long getTimeout() {
        return timeout;
    }
    
    public void setTimeout(long timeout) {
        this.timeout = timeout;
    }
    
    public long getRetryInterval() {
        return retryInterval;
    }
    
    public void setRetryInterval(long retryInterval) {
        this.retryInterval = retryInterval;
    }
    
    public boolean isDistributed() {
        return distributed;
    }
    
    public void setDistributed(boolean distributed) {
        this.distributed = distributed;
    }
    
    public String getRedisKeyPrefix() {
        return redisKeyPrefix;
    }
    
    public void setRedisKeyPrefix(String redisKeyPrefix) {
        this.redisKeyPrefix = redisKeyPrefix;
    }
    
    public boolean isMonitoring() {
        return monitoring;
    }
    
    public void setMonitoring(boolean monitoring) {
        this.monitoring = monitoring;
    }
}