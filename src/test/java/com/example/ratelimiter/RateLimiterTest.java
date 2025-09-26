package com.example.ratelimiter;

import com.example.ratelimiter.algorithm.TokenBucketRateLimiter;
import com.example.ratelimiter.config.RateLimiterProperties;
import com.example.ratelimiter.core.RateLimiterType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 限流器测试类
 * 
 * @author Rate Limiter Framework
 */
@SpringBootTest
public class RateLimiterTest {
    
    private TokenBucketRateLimiter rateLimiter;
    
    @BeforeEach
    void setUp() {
        RateLimiterProperties properties = new RateLimiterProperties();
        properties.setCapacity(10);
        properties.setRefillRate(2);
        properties.setRefillPeriod(1000);
        rateLimiter = new TokenBucketRateLimiter(properties);
    }
    
    @Test
    void testTokenBucketRateLimiter() {
        String key = "test-key";
        
        // 测试正常获取许可
        assertTrue(rateLimiter.tryAcquire(key));
        assertTrue(rateLimiter.tryAcquire(key, 2));
        
        // 测试超出容量限制
        assertFalse(rateLimiter.tryAcquire(key, 10));
        
        // 测试获取可用许可数
        long available = rateLimiter.getAvailablePermits(key);
        assertTrue(available >= 0);
        
        // 测试重置
        rateLimiter.reset(key);
        assertTrue(rateLimiter.tryAcquire(key));
    }
    
    @Test
    void testRateLimiterType() {
        assertEquals("token-bucket", RateLimiterType.TOKEN_BUCKET.getValue());
        assertEquals("sliding-window", RateLimiterType.SLIDING_WINDOW.getValue());
        assertEquals("fixed-window", RateLimiterType.FIXED_WINDOW.getValue());
        
        assertEquals(RateLimiterType.TOKEN_BUCKET, RateLimiterType.fromValue("token-bucket"));
        assertEquals(RateLimiterType.SLIDING_WINDOW, RateLimiterType.fromValue("sliding-window"));
        assertEquals(RateLimiterType.FIXED_WINDOW, RateLimiterType.fromValue("fixed-window"));
        
        assertThrows(IllegalArgumentException.class, () -> RateLimiterType.fromValue("unknown"));
    }
    
    @Test
    void testInvalidKey() {
        assertThrows(IllegalArgumentException.class, () -> rateLimiter.tryAcquire(null));
        assertThrows(IllegalArgumentException.class, () -> rateLimiter.tryAcquire(""));
        assertThrows(IllegalArgumentException.class, () -> rateLimiter.tryAcquire("   "));
    }
    
    @Test
    void testInvalidPermits() {
        String key = "test-key";
        assertThrows(IllegalArgumentException.class, () -> rateLimiter.tryAcquire(key, 0));
        assertThrows(IllegalArgumentException.class, () -> rateLimiter.tryAcquire(key, -1));
    }
}