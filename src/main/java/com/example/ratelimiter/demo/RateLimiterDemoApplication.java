package com.example.ratelimiter.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 限流框架演示应用
 * 
 * @author Rate Limiter Framework
 */
@SpringBootApplication
public class RateLimiterDemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(RateLimiterDemoApplication.class, args);
    }
}