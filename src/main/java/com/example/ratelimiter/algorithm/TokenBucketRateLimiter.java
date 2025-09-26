package com.example.ratelimiter.algorithm;

import com.example.ratelimiter.core.AbstractRateLimiter;
import com.example.ratelimiter.core.RateLimiterType;
import com.example.ratelimiter.config.RateLimiterProperties;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 令牌桶限流算法实现
 * 
 * @author Rate Limiter Framework
 */
@Component
public class TokenBucketRateLimiter extends AbstractRateLimiter {
    
    private final Cache<String, TokenBucket> bucketCache;
    
    public TokenBucketRateLimiter(RateLimiterProperties properties) {
        super(properties);
        this.bucketCache = Caffeine.newBuilder()
                .maximumSize(properties.getMaxKeys())
                .expireAfterAccess(Duration.ofMinutes(properties.getExpireMinutes()))
                .build();
    }
    
    @Override
    public boolean tryAcquire(String key, int permits) {
        validateKey(key);
        validatePermits(permits);
        
        TokenBucket bucket = bucketCache.get(key, k -> new TokenBucket(
                properties.getCapacity(),
                properties.getRefillRate(),
                properties.getRefillPeriod()
        ));
        
        return bucket.tryConsume(permits);
    }
    
    @Override
    public long getAvailablePermits(String key) {
        validateKey(key);
        
        TokenBucket bucket = bucketCache.getIfPresent(key);
        return bucket != null ? bucket.getAvailableTokens() : 0;
    }
    
    @Override
    public void reset(String key) {
        validateKey(key);
        bucketCache.invalidate(key);
    }
    
    @Override
    public String getType() {
        return RateLimiterType.TOKEN_BUCKET.getValue();
    }
    
    /**
     * 令牌桶内部类
     */
    private static class TokenBucket {
        private final long capacity;
        private final long refillRate;
        private final long refillPeriod;
        private final AtomicLong tokens;
        private volatile long lastRefillTime;
        
        public TokenBucket(long capacity, long refillRate, long refillPeriod) {
            this.capacity = capacity;
            this.refillRate = refillRate;
            this.refillPeriod = refillPeriod;
            this.tokens = new AtomicLong(capacity);
            this.lastRefillTime = System.currentTimeMillis();
        }
        
        public boolean tryConsume(int permits) {
            refill();
            long currentTokens = tokens.get();
            if (currentTokens >= permits) {
                return tokens.compareAndSet(currentTokens, currentTokens - permits);
            }
            return false;
        }
        
        public long getAvailableTokens() {
            refill();
            return tokens.get();
        }
        
        private void refill() {
            long now = System.currentTimeMillis();
            long timePassed = now - lastRefillTime;
            
            if (timePassed >= refillPeriod) {
                long tokensToAdd = (timePassed / refillPeriod) * refillRate;
                long currentTokens = tokens.get();
                long newTokens = Math.min(capacity, currentTokens + tokensToAdd);
                tokens.set(newTokens);
                lastRefillTime = now;
            }
        }
    }
}