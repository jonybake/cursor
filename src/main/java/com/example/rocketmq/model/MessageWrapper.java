package com.example.rocketmq.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 消息包装类，用于消息去重
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MessageWrapper implements Serializable {
    
    /**
     * 消息唯一ID（用于去重）
     */
    private String messageId;
    
    /**
     * 业务键（用于业务去重）
     */
    private String businessKey;
    
    /**
     * 消息内容
     */
    private String content;
    
    /**
     * 消息类型
     */
    private String messageType;
    
    /**
     * 创建时间
     */
    private LocalDateTime createTime;
    
    /**
     * 过期时间（用于Redis去重）
     */
    private LocalDateTime expireTime;
    
    /**
     * 重试次数
     */
    private Integer retryCount = 0;
    
    /**
     * 消息来源
     */
    private String source;
    
    /**
     * 消息标签
     */
    private String tags;
}