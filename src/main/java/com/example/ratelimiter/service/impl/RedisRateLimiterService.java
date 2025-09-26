package com.example.ratelimiter.service.impl;

import com.example.ratelimiter.annotation.RateLimiter;
import com.example.ratelimiter.config.RateLimiterProperties;
import com.example.ratelimiter.model.RateLimiterResult;
import com.example.ratelimiter.service.RateLimiterService;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.script.RedisScript;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

/**
 * Redis分布式限流服务实现
 * 
 * @author Rate Limiter Framework
 */
@Service
public class RedisRateLimiterService implements RateLimiterService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final RateLimiterProperties properties;
    private final RedisScript<Long> tokenBucketScript;
    private final RedisScript<Long> slidingWindowScript;

    public RedisRateLimiterService(RedisTemplate<String, Object> redisTemplate, 
                                   RateLimiterProperties properties) {
        this.redisTemplate = redisTemplate;
        this.properties = properties;
        this.tokenBucketScript = createTokenBucketScript();
        this.slidingWindowScript = createSlidingWindowScript();
    }

    @Override
    public RateLimiterResult checkRateLimit(String key, RateLimiter rateLimiter) {
        String redisKey = buildRedisKey(key);
        
        switch (rateLimiter.algorithm()) {
            case TOKEN_BUCKET:
                return checkTokenBucketLimit(redisKey, rateLimiter);
            case SLIDING_WINDOW:
                return checkSlidingWindowLimit(redisKey, rateLimiter);
            default:
                return checkTokenBucketLimit(redisKey, rateLimiter);
        }
    }

    @Override
    public RateLimiterResult checkRateLimit(String key) {
        String redisKey = buildRedisKey(key);
        return checkTokenBucketLimit(redisKey, null);
    }

    @Override
    public void cleanup() {
        // Redis会自动过期，无需手动清理
    }

    /**
     * 检查令牌桶限流
     */
    private RateLimiterResult checkTokenBucketLimit(String key, RateLimiter rateLimiter) {
        int permitsPerSecond = getPermitsPerSecond(rateLimiter);
        int burstCapacity = getBurstCapacity(rateLimiter);
        
        List<String> keys = Collections.singletonList(key);
        Object[] args = {permitsPerSecond, burstCapacity, System.currentTimeMillis() / 1000};
        
        Long result = redisTemplate.execute(tokenBucketScript, keys, args);
        
        if (result != null && result > 0) {
            return RateLimiterResult.success(result, System.currentTimeMillis() + 60000);
        } else {
            return RateLimiterResult.failure(0L, System.currentTimeMillis() + 60000, 
                    rateLimiter != null ? rateLimiter.message() : "请求过于频繁，请稍后再试");
        }
    }

    /**
     * 检查滑动窗口限流
     */
    private RateLimiterResult checkSlidingWindowLimit(String key, RateLimiter rateLimiter) {
        int windowSize = getWindowSize(rateLimiter);
        int windowPermits = getWindowPermits(rateLimiter);
        
        List<String> keys = Collections.singletonList(key);
        Object[] args = {windowSize, windowPermits, System.currentTimeMillis() / 1000};
        
        Long result = redisTemplate.execute(slidingWindowScript, keys, args);
        
        if (result != null && result > 0) {
            return RateLimiterResult.success(result, System.currentTimeMillis() + windowSize * 1000L);
        } else {
            return RateLimiterResult.failure(0L, System.currentTimeMillis() + windowSize * 1000L, 
                    rateLimiter != null ? rateLimiter.message() : "请求过于频繁，请稍后再试");
        }
    }

    /**
     * 构建Redis key
     */
    private String buildRedisKey(String key) {
        return properties.getRedis().getKeyPrefix() + key;
    }

    /**
     * 获取每秒许可数
     */
    private int getPermitsPerSecond(RateLimiter rateLimiter) {
        if (rateLimiter != null && rateLimiter.permitsPerSecond() > 0) {
            return rateLimiter.permitsPerSecond();
        }
        return properties.getDefaultConfig().getPermitsPerSecond();
    }

    /**
     * 获取突发容量
     */
    private int getBurstCapacity(RateLimiter rateLimiter) {
        if (rateLimiter != null && rateLimiter.burstCapacity() > 0) {
            return rateLimiter.burstCapacity();
        }
        return properties.getDefaultConfig().getBurstCapacity();
    }

    /**
     * 获取窗口大小
     */
    private int getWindowSize(RateLimiter rateLimiter) {
        if (rateLimiter != null && rateLimiter.windowSize() > 0) {
            return rateLimiter.windowSize();
        }
        return properties.getDefaultConfig().getWindowSize();
    }

    /**
     * 获取窗口许可数
     */
    private int getWindowPermits(RateLimiter rateLimiter) {
        if (rateLimiter != null && rateLimiter.windowPermits() > 0) {
            return rateLimiter.windowPermits();
        }
        return properties.getDefaultConfig().getWindowPermits();
    }

    /**
     * 创建令牌桶Lua脚本
     */
    private RedisScript<Long> createTokenBucketScript() {
        String script = 
            "local key = KEYS[1]\n" +
            "local permits_per_second = tonumber(ARGV[1])\n" +
            "local burst_capacity = tonumber(ARGV[2])\n" +
            "local current_time = tonumber(ARGV[3])\n" +
            "\n" +
            "local bucket = redis.call('HMGET', key, 'tokens', 'last_refill_time')\n" +
            "local tokens = tonumber(bucket[1]) or burst_capacity\n" +
            "local last_refill_time = tonumber(bucket[2]) or current_time\n" +
            "\n" +
            "local time_passed = current_time - last_refill_time\n" +
            "local tokens_to_add = time_passed * permits_per_second\n" +
            "tokens = math.min(burst_capacity, tokens + tokens_to_add)\n" +
            "\n" +
            "if tokens >= 1 then\n" +
            "    tokens = tokens - 1\n" +
            "    redis.call('HMSET', key, 'tokens', tokens, 'last_refill_time', current_time)\n" +
            "    redis.call('EXPIRE', key, 3600)\n" +
            "    return tokens\n" +
            "else\n" +
            "    redis.call('HMSET', key, 'tokens', tokens, 'last_refill_time', current_time)\n" +
            "    redis.call('EXPIRE', key, 3600)\n" +
            "    return 0\n" +
            "end";
        
        return RedisScript.of(script, Long.class);
    }

    /**
     * 创建滑动窗口Lua脚本
     */
    private RedisScript<Long> createSlidingWindowScript() {
        String script = 
            "local key = KEYS[1]\n" +
            "local window_size = tonumber(ARGV[1])\n" +
            "local window_permits = tonumber(ARGV[2])\n" +
            "local current_time = tonumber(ARGV[3])\n" +
            "\n" +
            "local window_start = current_time - window_size\n" +
            "redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)\n" +
            "\n" +
            "local current_count = redis.call('ZCARD', key)\n" +
            "\n" +
            "if current_count < window_permits then\n" +
            "    redis.call('ZADD', key, current_time, current_time .. ':' .. math.random())\n" +
            "    redis.call('EXPIRE', key, window_size + 1)\n" +
            "    return window_permits - current_count - 1\n" +
            "else\n" +
            "    return 0\n" +
            "end";
        
        return RedisScript.of(script, Long.class);
    }
}