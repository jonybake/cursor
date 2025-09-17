package com.example.rocketmq.service;

import com.example.rocketmq.model.MessageWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.apache.rocketmq.client.consumer.listener.ConsumeConcurrentlyContext;
import org.apache.rocketmq.client.consumer.listener.ConsumeConcurrentlyStatus;
import org.apache.rocketmq.client.consumer.listener.MessageListenerConcurrently;
import org.apache.rocketmq.common.message.MessageExt;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 消息消费者服务
 */
@Slf4j
@Service
public class MessageConsumerService implements MessageListenerConcurrently {

    @Autowired
    private DeduplicationService deduplicationService;

    @Autowired
    private ObjectMapper objectMapper;

    @Override
    public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> messages, 
                                                   ConsumeConcurrentlyContext context) {
        
        for (MessageExt messageExt : messages) {
            try {
                // 获取消息ID
                String messageId = messageExt.getKeys();
                String consumerGroup = context.getConsumerGroup();
                
                log.info("接收到消息 - 消息ID: {}, 主题: {}, 标签: {}", 
                        messageId, messageExt.getTopic(), messageExt.getTags());
                
                // 检查消息是否已被消费（幂等性检查）
                if (deduplicationService.isMessageConsumed(messageId, consumerGroup)) {
                    log.warn("消息 {} 已被消费过，跳过处理", messageId);
                    return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
                }
                
                // 解析消息内容
                String messageBody = new String(messageExt.getBody());
                MessageWrapper messageWrapper = objectMapper.readValue(messageBody, MessageWrapper.class);
                
                // 处理消息
                boolean processResult = processMessage(messageWrapper);
                
                if (processResult) {
                    // 标记消息为已消费
                    deduplicationService.markMessageAsConsumed(messageId, consumerGroup, 60);
                    log.info("消息 {} 处理成功", messageId);
                } else {
                    log.error("消息 {} 处理失败", messageId);
                    return ConsumeConcurrentlyStatus.RECONSUME_LATER;
                }
                
            } catch (Exception e) {
                log.error("消息处理异常", e);
                return ConsumeConcurrentlyStatus.RECONSUME_LATER;
            }
        }
        
        return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
    }

    /**
     * 处理消息的具体业务逻辑
     * @param messageWrapper 消息包装对象
     * @return 处理结果
     */
    private boolean processMessage(MessageWrapper messageWrapper) {
        try {
            String messageType = messageWrapper.getMessageType();
            String content = messageWrapper.getContent();
            String businessKey = messageWrapper.getBusinessKey();
            
            log.info("开始处理消息 - 类型: {}, 业务键: {}, 内容: {}", 
                    messageType, businessKey, content);
            
            // 根据消息类型进行不同的处理
            switch (messageType) {
                case "business":
                    return processBusinessMessage(messageWrapper);
                case "order":
                    return processOrderMessage(messageWrapper);
                case "payment":
                    return processPaymentMessage(messageWrapper);
                case "user":
                    return processUserMessage(messageWrapper);
                default:
                    log.warn("未知的消息类型: {}", messageType);
                    return true; // 未知类型也认为处理成功，避免重复消费
            }
            
        } catch (Exception e) {
            log.error("消息处理异常", e);
            return false;
        }
    }

    /**
     * 处理业务消息
     */
    private boolean processBusinessMessage(MessageWrapper messageWrapper) {
        log.info("处理业务消息: {}", messageWrapper.getContent());
        // 模拟业务处理
        try {
            Thread.sleep(100); // 模拟处理时间
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return true;
    }

    /**
     * 处理订单消息
     */
    private boolean processOrderMessage(MessageWrapper messageWrapper) {
        log.info("处理订单消息: {}", messageWrapper.getContent());
        // 模拟订单处理逻辑
        try {
            Thread.sleep(200);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return true;
    }

    /**
     * 处理支付消息
     */
    private boolean processPaymentMessage(MessageWrapper messageWrapper) {
        log.info("处理支付消息: {}", messageWrapper.getContent());
        // 模拟支付处理逻辑
        try {
            Thread.sleep(150);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return true;
    }

    /**
     * 处理用户消息
     */
    private boolean processUserMessage(MessageWrapper messageWrapper) {
        log.info("处理用户消息: {}", messageWrapper.getContent());
        // 模拟用户操作处理逻辑
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return true;
    }
}