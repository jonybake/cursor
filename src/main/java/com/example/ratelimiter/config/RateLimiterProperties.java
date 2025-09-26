package com.example.ratelimiter.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 限流框架配置属性
 * 
 * @author Rate Limiter Framework
 */
@ConfigurationProperties(prefix = "rate-limiter")
public class RateLimiterProperties {

    /**
     * 限流类型：local(本地) 或 redis(分布式)
     */
    private String type = "local";

    /**
     * 默认限流算法：token-bucket 或 sliding-window
     */
    private String algorithm = "token-bucket";

    /**
     * 默认限流配置
     */
    private DefaultConfig defaultConfig = new DefaultConfig();

    /**
     * Redis配置
     */
    private RedisConfig redis = new RedisConfig();

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getAlgorithm() {
        return algorithm;
    }

    public void setAlgorithm(String algorithm) {
        this.algorithm = algorithm;
    }

    public DefaultConfig getDefaultConfig() {
        return defaultConfig;
    }

    public void setDefaultConfig(DefaultConfig defaultConfig) {
        this.defaultConfig = defaultConfig;
    }

    public RedisConfig getRedis() {
        return redis;
    }

    public void setRedis(RedisConfig redis) {
        this.redis = redis;
    }

    /**
     * 默认限流配置
     */
    public static class DefaultConfig {
        /**
         * 每秒允许的请求数
         */
        private int permitsPerSecond = 10;

        /**
         * 突发请求数
         */
        private int burstCapacity = 20;

        /**
         * 时间窗口大小（秒）
         */
        private int windowSize = 60;

        /**
         * 时间窗口内允许的请求数
         */
        private int windowPermits = 100;

        public int getPermitsPerSecond() {
            return permitsPerSecond;
        }

        public void setPermitsPerSecond(int permitsPerSecond) {
            this.permitsPerSecond = permitsPerSecond;
        }

        public int getBurstCapacity() {
            return burstCapacity;
        }

        public void setBurstCapacity(int burstCapacity) {
            this.burstCapacity = burstCapacity;
        }

        public int getWindowSize() {
            return windowSize;
        }

        public void setWindowSize(int windowSize) {
            this.windowSize = windowSize;
        }

        public int getWindowPermits() {
            return windowPermits;
        }

        public void setWindowPermits(int windowPermits) {
            this.windowPermits = windowPermits;
        }
    }

    /**
     * Redis配置
     */
    public static class RedisConfig {
        /**
         * Redis key前缀
         */
        private String keyPrefix = "rate_limiter:";

        /**
         * 脚本缓存
         */
        private boolean scriptCache = true;

        public String getKeyPrefix() {
            return keyPrefix;
        }

        public void setKeyPrefix(String keyPrefix) {
            this.keyPrefix = keyPrefix;
        }

        public boolean isScriptCache() {
            return scriptCache;
        }

        public void setScriptCache(boolean scriptCache) {
            this.scriptCache = scriptCache;
        }
    }
}