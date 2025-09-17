package com.example.rocketmq.service;

import com.example.rocketmq.model.MessageWrapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

/**
 * 消息去重服务
 */
@Slf4j
@Service
public class DeduplicationService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    // Redis键前缀
    private static final String MESSAGE_ID_PREFIX = "msg:id:";
    private static final String BUSINESS_KEY_PREFIX = "msg:business:";
    private static final String CONSUME_PREFIX = "msg:consume:";

    /**
     * 基于消息ID的去重检查
     * @param messageId 消息ID
     * @param expireMinutes 过期时间（分钟）
     * @return true表示消息已存在（需要去重），false表示消息不存在
     */
    public boolean isDuplicateByMessageId(String messageId, long expireMinutes) {
        String key = MESSAGE_ID_PREFIX + messageId;
        
        // 使用SETNX命令，如果key不存在则设置并返回true，如果存在则返回false
        Boolean isSet = redisTemplate.opsForValue().setIfAbsent(key, "1", Duration.ofMinutes(expireMinutes));
        
        if (Boolean.TRUE.equals(isSet)) {
            log.info("消息ID {} 首次出现，允许处理", messageId);
            return false; // 消息不存在，不是重复消息
        } else {
            log.warn("消息ID {} 已存在，需要去重", messageId);
            return true; // 消息已存在，是重复消息
        }
    }

    /**
     * 基于业务键的去重检查
     * @param businessKey 业务键
     * @param expireMinutes 过期时间（分钟）
     * @return true表示消息已存在（需要去重），false表示消息不存在
     */
    public boolean isDuplicateByBusinessKey(String businessKey, long expireMinutes) {
        String key = BUSINESS_KEY_PREFIX + businessKey;
        
        Boolean isSet = redisTemplate.opsForValue().setIfAbsent(key, "1", Duration.ofMinutes(expireMinutes));
        
        if (Boolean.TRUE.equals(isSet)) {
            log.info("业务键 {} 首次出现，允许处理", businessKey);
            return false;
        } else {
            log.warn("业务键 {} 已存在，需要去重", businessKey);
            return true;
        }
    }

    /**
     * 检查消息是否已被消费
     * @param messageId 消息ID
     * @param consumerGroup 消费者组
     * @return true表示已消费，false表示未消费
     */
    public boolean isMessageConsumed(String messageId, String consumerGroup) {
        String key = CONSUME_PREFIX + consumerGroup + ":" + messageId;
        
        Boolean exists = redisTemplate.hasKey(key);
        if (Boolean.TRUE.equals(exists)) {
            log.warn("消息 {} 已被消费者组 {} 消费过", messageId, consumerGroup);
            return true;
        }
        
        return false;
    }

    /**
     * 标记消息为已消费
     * @param messageId 消息ID
     * @param consumerGroup 消费者组
     * @param expireMinutes 过期时间（分钟）
     */
    public void markMessageAsConsumed(String messageId, String consumerGroup, long expireMinutes) {
        String key = CONSUME_PREFIX + consumerGroup + ":" + messageId;
        redisTemplate.opsForValue().set(key, "1", Duration.ofMinutes(expireMinutes));
        log.info("标记消息 {} 为已消费，消费者组: {}", messageId, consumerGroup);
    }

    /**
     * 综合去重检查
     * @param message 消息包装对象
     * @param expireMinutes 过期时间（分钟）
     * @return true表示需要去重，false表示可以处理
     */
    public boolean isDuplicate(MessageWrapper message, long expireMinutes) {
        // 1. 检查消息ID去重
        if (isDuplicateByMessageId(message.getMessageId(), expireMinutes)) {
            return true;
        }
        
        // 2. 检查业务键去重
        if (message.getBusinessKey() != null && 
            isDuplicateByBusinessKey(message.getBusinessKey(), expireMinutes)) {
            return true;
        }
        
        return false;
    }

    /**
     * 清理过期的去重记录
     * @param messageId 消息ID
     * @param businessKey 业务键
     */
    public void cleanDeduplicationRecords(String messageId, String businessKey) {
        if (messageId != null) {
            redisTemplate.delete(MESSAGE_ID_PREFIX + messageId);
        }
        if (businessKey != null) {
            redisTemplate.delete(BUSINESS_KEY_PREFIX + businessKey);
        }
        log.info("清理去重记录 - 消息ID: {}, 业务键: {}", messageId, businessKey);
    }
}