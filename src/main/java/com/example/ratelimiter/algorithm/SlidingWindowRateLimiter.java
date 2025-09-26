package com.example.ratelimiter.algorithm;

import org.springframework.stereotype.Component;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 基于滑动窗口算法的限流器
 * 
 * @author Rate Limiter Framework
 */
@Component("slidingWindowRateLimiter")
public class SlidingWindowRateLimiter implements RateLimiterAlgorithm {

    /**
     * 滑动窗口数据缓存
     */
    private final ConcurrentHashMap<String, SlidingWindow> windows = new ConcurrentHashMap<>();

    /**
     * 定时清理任务
     */
    private final ScheduledExecutorService cleanupExecutor = Executors.newScheduledThreadPool(1);

    /**
     * 默认配置
     */
    private static final int DEFAULT_WINDOW_SIZE = 60; // 60秒
    private static final int DEFAULT_WINDOW_PERMITS = 100; // 100个请求

    public SlidingWindowRateLimiter() {
        // 启动定时清理任务
        cleanupExecutor.scheduleAtFixedRate(this::cleanup, 1, 1, TimeUnit.MINUTES);
    }

    @Override
    public boolean tryAcquire(String key, int permits) {
        SlidingWindow window = getOrCreateWindow(key, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_PERMITS);
        return window.tryAcquire(permits);
    }

    @Override
    public boolean tryAcquire(String key) {
        return tryAcquire(key, 1);
    }

    @Override
    public long getAvailablePermits(String key) {
        SlidingWindow window = windows.get(key);
        if (window == null) {
            return 0;
        }
        return window.getAvailablePermits();
    }

    @Override
    public void reset(String key) {
        windows.remove(key);
    }

    @Override
    public void cleanup() {
        long currentTime = System.currentTimeMillis();
        windows.entrySet().removeIf(entry -> {
            SlidingWindow window = entry.getValue();
            // 清理超过窗口时间的数据
            return currentTime - window.getLastAccessTime() > window.getWindowSize() * 1000L;
        });
    }

    /**
     * 获取或创建滑动窗口
     */
    private SlidingWindow getOrCreateWindow(String key, int windowSize, int windowPermits) {
        return windows.computeIfAbsent(key, k -> new SlidingWindow(windowSize, windowPermits));
    }

    /**
     * 创建自定义配置的滑动窗口
     */
    public SlidingWindow createWindow(String key, int windowSize, int windowPermits) {
        SlidingWindow window = new SlidingWindow(windowSize, windowPermits);
        windows.put(key, window);
        return window;
    }

    /**
     * 滑动窗口实现
     */
    private static class SlidingWindow {
        private final int windowSize; // 窗口大小（秒）
        private final int windowPermits; // 窗口内允许的请求数
        private final AtomicLong[] buckets; // 时间桶
        private final AtomicLong lastAccessTime = new AtomicLong(System.currentTimeMillis());
        private volatile int currentBucketIndex = 0;

        public SlidingWindow(int windowSize, int windowPermits) {
            this.windowSize = windowSize;
            this.windowPermits = windowPermits;
            this.buckets = new AtomicLong[windowSize];
            for (int i = 0; i < windowSize; i++) {
                buckets[i] = new AtomicLong(0);
            }
        }

        public synchronized boolean tryAcquire(int permits) {
            long currentTime = System.currentTimeMillis();
            lastAccessTime.set(currentTime);

            // 计算当前时间对应的桶索引
            int bucketIndex = (int) ((currentTime / 1000) % windowSize);
            
            // 如果时间窗口滑动，重置旧桶
            if (bucketIndex != currentBucketIndex) {
                buckets[bucketIndex].set(0);
                currentBucketIndex = bucketIndex;
            }

            // 计算当前窗口内的总请求数
            long totalRequests = 0;
            for (AtomicLong bucket : buckets) {
                totalRequests += bucket.get();
            }

            // 检查是否超过限制
            if (totalRequests + permits > windowPermits) {
                return false;
            }

            // 增加当前桶的计数
            buckets[bucketIndex].addAndGet(permits);
            return true;
        }

        public long getAvailablePermits() {
            long totalRequests = 0;
            for (AtomicLong bucket : buckets) {
                totalRequests += bucket.get();
            }
            return Math.max(0, windowPermits - totalRequests);
        }

        public int getWindowSize() {
            return windowSize;
        }

        public long getLastAccessTime() {
            return lastAccessTime.get();
        }
    }
}