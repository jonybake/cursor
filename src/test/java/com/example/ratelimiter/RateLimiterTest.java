package com.example.ratelimiter;

import com.example.ratelimiter.annotation.RateLimiter;
import com.example.ratelimiter.service.RateLimiterService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 限流框架测试
 * 
 * @author Rate Limiter Framework
 */
@SpringBootTest
@TestPropertySource(properties = {
    "rate-limiter.type=local",
    "rate-limiter.algorithm=token-bucket",
    "rate-limiter.default-config.permits-per-second=2"
})
public class RateLimiterTest {

    @Autowired
    private RateLimiterService rateLimiterService;

    @Test
    public void testBasicRateLimit() {
        String key = "test-key";
        
        // 第一次请求应该成功
        assertTrue(rateLimiterService.checkRateLimit(key).isAllowed());
        
        // 第二次请求应该成功
        assertTrue(rateLimiterService.checkRateLimit(key).isAllowed());
        
        // 第三次请求应该被限流
        assertFalse(rateLimiterService.checkRateLimit(key).isAllowed());
    }

    @Test
    public void testTokenBucketRateLimit() {
        String key = "token-bucket-test";
        RateLimiter rateLimiter = createTokenBucketRateLimiter();
        
        // 测试令牌桶限流
        for (int i = 0; i < 5; i++) {
            boolean allowed = rateLimiterService.checkRateLimit(key, rateLimiter).isAllowed();
            if (i < 3) {
                assertTrue(allowed, "Request " + i + " should be allowed");
            } else {
                assertFalse(allowed, "Request " + i + " should be rate limited");
            }
        }
    }

    @Test
    public void testSlidingWindowRateLimit() {
        String key = "sliding-window-test";
        RateLimiter rateLimiter = createSlidingWindowRateLimiter();
        
        // 测试滑动窗口限流
        for (int i = 0; i < 15; i++) {
            boolean allowed = rateLimiterService.checkRateLimit(key, rateLimiter).isAllowed();
            if (i < 10) {
                assertTrue(allowed, "Request " + i + " should be allowed");
            } else {
                assertFalse(allowed, "Request " + i + " should be rate limited");
            }
        }
    }

    @Test
    public void testDifferentKeys() {
        String key1 = "key1";
        String key2 = "key2";
        
        // 不同key的限流应该独立
        assertTrue(rateLimiterService.checkRateLimit(key1).isAllowed());
        assertTrue(rateLimiterService.checkRateLimit(key2).isAllowed());
        assertTrue(rateLimiterService.checkRateLimit(key1).isAllowed());
        assertTrue(rateLimiterService.checkRateLimit(key2).isAllowed());
    }

    private RateLimiter createTokenBucketRateLimiter() {
        return new RateLimiter() {
            @Override
            public Class<? extends Annotation> annotationType() {
                return RateLimiter.class;
            }

            @Override
            public String key() {
                return "";
            }

            @Override
            public Algorithm algorithm() {
                return Algorithm.TOKEN_BUCKET;
            }

            @Override
            public int permitsPerSecond() {
                return 2;
            }

            @Override
            public int burstCapacity() {
                return 3;
            }

            @Override
            public int windowSize() {
                return -1;
            }

            @Override
            public int windowPermits() {
                return -1;
            }

            @Override
            public String message() {
                return "Rate limit exceeded";
            }

            @Override
            public int statusCode() {
                return 429;
            }
        };
    }

    private RateLimiter createSlidingWindowRateLimiter() {
        return new RateLimiter() {
            @Override
            public Class<? extends Annotation> annotationType() {
                return RateLimiter.class;
            }

            @Override
            public String key() {
                return "";
            }

            @Override
            public Algorithm algorithm() {
                return Algorithm.SLIDING_WINDOW;
            }

            @Override
            public int permitsPerSecond() {
                return -1;
            }

            @Override
            public int burstCapacity() {
                return -1;
            }

            @Override
            public int windowSize() {
                return 60;
            }

            @Override
            public int windowPermits() {
                return 10;
            }

            @Override
            public String message() {
                return "Rate limit exceeded";
            }

            @Override
            public int statusCode() {
                return 429;
            }
        };
    }
}