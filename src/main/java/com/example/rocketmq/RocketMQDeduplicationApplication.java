package com.example.rocketmq;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * RocketMQ消息去重示例应用
 */
@SpringBootApplication
public class RocketMQDeduplicationApplication {
    public static void main(String[] args) {
        SpringApplication.run(RocketMQDeduplicationApplication.class, args);
    }
}