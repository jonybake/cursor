package com.example.ratelimiter.algorithm;

import com.example.ratelimiter.core.AbstractRateLimiter;
import com.example.ratelimiter.core.RateLimiterType;
import com.example.ratelimiter.config.RateLimiterProperties;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 滑动窗口限流算法实现
 * 
 * @author Rate Limiter Framework
 */
@Component
public class SlidingWindowRateLimiter extends AbstractRateLimiter {
    
    private final Cache<String, SlidingWindow> windowCache;
    
    public SlidingWindowRateLimiter(RateLimiterProperties properties) {
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
        
        SlidingWindow window = windowCache.get(key, k -> new SlidingWindow(
                properties.getCapacity(),
                properties.getWindowSize()
        ));
        
        return window.tryConsume(permits);
    }
    
    @Override
    public long getAvailablePermits(String key) {
        validateKey(key);
        
        SlidingWindow window = windowCache.getIfPresent(key);
        return window != null ? window.getAvailablePermits() : 0;
    }
    
    @Override
    public void reset(String key) {
        validateKey(key);
        windowCache.invalidate(key);
    }
    
    @Override
    public String getType() {
        return RateLimiterType.SLIDING_WINDOW.getValue();
    }
    
    /**
     * 滑动窗口内部类
     */
    private static class SlidingWindow {
        private final long capacity;
        private final long windowSize;
        private final ConcurrentLinkedQueue<Long> requests;
        private final AtomicLong totalRequests;
        
        public SlidingWindow(long capacity, long windowSize) {
            this.capacity = capacity;
            this.windowSize = windowSize;
            this.requests = new ConcurrentLinkedQueue<>();
            this.totalRequests = new AtomicLong(0);
        }
        
        public boolean tryConsume(int permits) {
            long now = System.currentTimeMillis();
            long windowStart = now - windowSize;
            
            // 清理过期的请求记录
            while (!requests.isEmpty() && requests.peek() < windowStart) {
                requests.poll();
                totalRequests.decrementAndGet();
            }
            
            // 检查是否还有容量
            if (totalRequests.get() + permits <= capacity) {
                for (int i = 0; i < permits; i++) {
                    requests.offer(now);
                    totalRequests.incrementAndGet();
                }
                return true;
            }
            
            return false;
        }
        
        public long getAvailablePermits() {
            long now = System.currentTimeMillis();
            long windowStart = now - windowSize;
            
            // 清理过期的请求记录
            while (!requests.isEmpty() && requests.peek() < windowStart) {
                requests.poll();
                totalRequests.decrementAndGet();
            }
            
            return Math.max(0, capacity - totalRequests.get());
        }
    }
}