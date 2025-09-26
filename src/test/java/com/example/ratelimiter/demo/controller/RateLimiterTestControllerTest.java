package com.example.ratelimiter.demo.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureTestMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 限流测试控制器测试
 * 
 * @author Rate Limiter Framework
 */
@SpringBootTest
@AutoConfigureTestMvc
@TestPropertySource(properties = {
    "rate-limiter.type=local",
    "rate-limiter.algorithm=token-bucket",
    "rate-limiter.default-config.permits-per-second=2"
})
public class RateLimiterTestControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testBasicRateLimit() throws Exception {
        // 第一次请求应该成功
        mockMvc.perform(get("/api/rate-limiter/basic"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Basic rate limit test passed"));

        // 第二次请求应该成功
        mockMvc.perform(get("/api/rate-limiter/basic"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Basic rate limit test passed"));

        // 第三次请求应该被限流
        mockMvc.perform(get("/api/rate-limiter/basic"))
                .andExpect(status().isTooManyRequests())
                .andExpect(jsonPath("$.error").value("Rate limit exceeded"));
    }

    @Test
    public void testTokenBucketRateLimit() throws Exception {
        // 测试令牌桶限流
        for (int i = 0; i < 5; i++) {
            if (i < 3) {
                mockMvc.perform(get("/api/rate-limiter/token-bucket"))
                        .andExpect(status().isOk())
                        .andExpect(jsonPath("$.message").value("Token bucket rate limit test passed"));
            } else {
                mockMvc.perform(get("/api/rate-limiter/token-bucket"))
                        .andExpect(status().isTooManyRequests())
                        .andExpect(jsonPath("$.error").value("Rate limit exceeded"));
            }
        }
    }

    @Test
    public void testUserBasedRateLimit() throws Exception {
        String userId = "user123";
        
        // 同一用户的请求应该被限流
        for (int i = 0; i < 4; i++) {
            if (i < 3) {
                mockMvc.perform(get("/api/rate-limiter/user/" + userId))
                        .andExpect(status().isOk())
                        .andExpect(jsonPath("$.userId").value(userId));
            } else {
                mockMvc.perform(get("/api/rate-limiter/user/" + userId))
                        .andExpect(status().isTooManyRequests());
            }
        }
        
        // 不同用户的请求应该独立限流
        mockMvc.perform(get("/api/rate-limiter/user/user456"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.userId").value("user456"));
    }

    @Test
    public void testParamBasedRateLimit() throws Exception {
        String requestId = "req123";
        String action = "test";
        
        // 测试基于参数的限流
        for (int i = 0; i < 12; i++) {
            if (i < 10) {
                mockMvc.perform(post("/api/rate-limiter/param-based")
                        .param("requestId", requestId)
                        .param("action", action))
                        .andExpect(status().isOk())
                        .andExpect(jsonPath("$.requestId").value(requestId))
                        .andExpect(jsonPath("$.action").value(action));
            } else {
                mockMvc.perform(post("/api/rate-limiter/param-based")
                        .param("requestId", requestId)
                        .param("action", action))
                        .andExpect(status().isTooManyRequests());
            }
        }
    }

    @Test
    public void testNoLimitEndpoint() throws Exception {
        // 无限流的端点应该始终成功
        for (int i = 0; i < 10; i++) {
            mockMvc.perform(get("/api/rate-limiter/no-limit"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.message").value("No rate limit test passed"));
        }
    }
}