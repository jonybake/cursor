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
 * 固定窗口限流算法实现
 * 
 * @author Rate Limiter Framework
 */
@Component
public class FixedWindowRateLimiter extends AbstractRateLimiter {
    
    private final Cache<String, FixedWindow> windowCache;
    
    public FixedWindowRateLimiter(RateLimiterProperties properties) {
        super(properties);
        this.windowCache = Caffeine.newBuilder()
                .maximumSize(properties.getMaxKeys())
                .expireAfterAccess(Duration.ofMinutes(properties.getExpireMinutes()))
                .build();
    }
    
    @Override
    public boolean tryAcquire(String key, int permits) {
        validateKey(key);
        validatePermits(permits);
        
        FixedWindow window = windowCache.get(key, k -> new FixedWindow(
                properties.getCapacity(),
                properties.getWindowSize()
        ));
        
        return window.tryConsume(permits);
    }
    
    @Override
    public long getAvailablePermits(String key) {
        validateKey(key);
        
        FixedWindow window = windowCache.getIfPresent(key);
        return window != null ? window.getAvailablePermits() : 0;
    }
    
    @Override
    public void reset(String key) {
        validateKey(key);
        windowCache.invalidate(key);
    }
    
    @Override
    public String getType() {
        return RateLimiterType.FIXED_WINDOW.getValue();
    }
    
    /**
     * 固定窗口内部类
     */
    private static class FixedWindow {
        private final long capacity;
        private final long windowSize;
        private final AtomicLong currentCount;
        private volatile long windowStart;
        
        public FixedWindow(long capacity, long windowSize) {
            this.capacity = capacity;
            this.windowSize = windowSize;
            this.currentCount = new AtomicLong(0);
            this.windowStart = System.currentTimeMillis();
        }
        
        public boolean tryConsume(int permits) {
            long now = System.currentTimeMillis();
            
            // 检查是否需要重置窗口
            if (now - windowStart >= windowSize) {
                synchronized (this) {
                    // 双重检查
                    if (now - windowStart >= windowSize) {
                        currentCount.set(0);
                        windowStart = now;
                    }
                }
            }
            
            // 尝试消费许可
            long current = currentCount.get();
            if (current + permits <= capacity) {
                return currentCount.compareAndSet(current, current + permits);
            }
            
            return false;
        }
        
        public long getAvailablePermits() {
            long now = System.currentTimeMillis();
            
            // 检查是否需要重置窗口
            if (now - windowStart >= windowSize) {
                synchronized (this) {
                    // 双重检查
                    if (now - windowStart >= windowSize) {
                        currentCount.set(0);
                        windowStart = now;
                    }
                }
            }
            
            return Math.max(0, capacity - currentCount.get());
        }
    }
}