package com.example.rocketmq.service;

import com.example.rocketmq.model.MessageWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.apache.rocketmq.client.producer.DefaultMQProducer;
import org.apache.rocketmq.client.producer.SendResult;
import org.apache.rocketmq.common.message.Message;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * 消息生产者服务
 */
@Slf4j
@Service
public class MessageProducerService {

    @Autowired
    private DefaultMQProducer producer;

    @Autowired
    private DeduplicationService deduplicationService;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * 发送消息（带去重检查）
     * @param topic 主题
     * @param tags 标签
     * @param content 消息内容
     * @param businessKey 业务键（可选）
     * @return 发送结果
     */
    public SendResult sendMessage(String topic, String tags, String content, String businessKey) {
        try {
            // 生成消息ID
            String messageId = UUID.randomUUID().toString();
            
            // 创建消息包装对象
            MessageWrapper messageWrapper = new MessageWrapper();
            messageWrapper.setMessageId(messageId);
            messageWrapper.setBusinessKey(businessKey);
            messageWrapper.setContent(content);
            messageWrapper.setMessageType("business");
            messageWrapper.setCreateTime(LocalDateTime.now());
            messageWrapper.setExpireTime(LocalDateTime.now().plusMinutes(30));
            messageWrapper.setSource("producer");
            messageWrapper.setTags(tags);

            // 检查去重
            if (deduplicationService.isDuplicate(messageWrapper, 30)) {
                log.warn("消息重复，跳过发送 - 消息ID: {}, 业务键: {}", messageId, businessKey);
                return null;
            }

            // 序列化消息
            String messageBody = objectMapper.writeValueAsString(messageWrapper);
            
            // 创建RocketMQ消息
            Message message = new Message(topic, tags, messageBody.getBytes());
            // 设置消息ID用于去重
            message.setKeys(messageId);
            
            // 发送消息
            SendResult sendResult = producer.send(message);
            
            log.info("消息发送成功 - 消息ID: {}, 业务键: {}, 结果: {}", 
                    messageId, businessKey, sendResult.getSendStatus());
            
            return sendResult;
            
        } catch (Exception e) {
            log.error("消息发送失败", e);
            throw new RuntimeException("消息发送失败", e);
        }
    }

    /**
     * 发送订单消息（业务场景示例）
     * @param orderId 订单ID
     * @param userId 用户ID
     * @param amount 金额
     * @return 发送结果
     */
    public SendResult sendOrderMessage(String orderId, String userId, Double amount) {
        String content = String.format("订单处理 - 订单ID: %s, 用户ID: %s, 金额: %.2f", orderId, userId, amount);
        String businessKey = "order:" + orderId; // 使用订单ID作为业务键
        
        return sendMessage("ORDER_TOPIC", "ORDER_CREATE", content, businessKey);
    }

    /**
     * 发送支付消息（业务场景示例）
     * @param paymentId 支付ID
     * @param orderId 订单ID
     * @param amount 金额
     * @return 发送结果
     */
    public SendResult sendPaymentMessage(String paymentId, String orderId, Double amount) {
        String content = String.format("支付处理 - 支付ID: %s, 订单ID: %s, 金额: %.2f", paymentId, orderId, amount);
        String businessKey = "payment:" + paymentId; // 使用支付ID作为业务键
        
        return sendMessage("PAYMENT_TOPIC", "PAYMENT_SUCCESS", content, businessKey);
    }

    /**
     * 发送用户消息（业务场景示例）
     * @param userId 用户ID
     * @param action 操作类型
     * @param details 详细信息
     * @return 发送结果
     */
    public SendResult sendUserMessage(String userId, String action, String details) {
        String content = String.format("用户操作 - 用户ID: %s, 操作: %s, 详情: %s", userId, action, details);
        String businessKey = "user:" + userId + ":" + action; // 使用用户ID和操作类型作为业务键
        
        return sendMessage("USER_TOPIC", "USER_ACTION", content, businessKey);
    }
}