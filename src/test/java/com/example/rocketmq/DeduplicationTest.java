package com.example.rocketmq;

import com.example.rocketmq.service.DeduplicationService;
import com.example.rocketmq.service.MessageProducerService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 消息去重功能测试
 */
@SpringBootTest
@ActiveProfiles("test")
public class DeduplicationTest {

    @Autowired
    private DeduplicationService deduplicationService;

    @Autowired
    private MessageProducerService messageProducerService;

    @Test
    public void testMessageIdDeduplication() {
        String messageId = "test-message-id-001";
        
        // 第一次检查应该返回false（不是重复消息）
        assertFalse(deduplicationService.isDuplicateByMessageId(messageId, 5));
        
        // 第二次检查应该返回true（是重复消息）
        assertTrue(deduplicationService.isDuplicateByMessageId(messageId, 5));
    }

    @Test
    public void testBusinessKeyDeduplication() {
        String businessKey = "test-business-key-001";
        
        // 第一次检查应该返回false（不是重复消息）
        assertFalse(deduplicationService.isDuplicateByBusinessKey(businessKey, 5));
        
        // 第二次检查应该返回true（是重复消息）
        assertTrue(deduplicationService.isDuplicateByBusinessKey(businessKey, 5));
    }

    @Test
    public void testMessageConsumption() {
        String messageId = "test-consume-001";
        String consumerGroup = "test-consumer-group";
        
        // 检查消息是否已被消费（应该返回false）
        assertFalse(deduplicationService.isMessageConsumed(messageId, consumerGroup));
        
        // 标记消息为已消费
        deduplicationService.markMessageAsConsumed(messageId, consumerGroup, 5);
        
        // 再次检查应该返回true
        assertTrue(deduplicationService.isMessageConsumed(messageId, consumerGroup));
    }

    @Test
    public void testOrderMessageDeduplication() {
        String orderId = "ORDER-TEST-001";
        String userId = "USER-001";
        Double amount = 100.0;
        
        // 第一次发送应该成功
        var result1 = messageProducerService.sendOrderMessage(orderId, userId, amount);
        assertNotNull(result1);
        
        // 第二次发送相同订单应该被去重
        var result2 = messageProducerService.sendOrderMessage(orderId, userId, amount);
        assertNull(result2);
    }

    @Test
    public void testPaymentMessageDeduplication() {
        String paymentId = "PAY-TEST-001";
        String orderId = "ORDER-001";
        Double amount = 100.0;
        
        // 第一次发送应该成功
        var result1 = messageProducerService.sendPaymentMessage(paymentId, orderId, amount);
        assertNotNull(result1);
        
        // 第二次发送相同支付应该被去重
        var result2 = messageProducerService.sendPaymentMessage(paymentId, orderId, amount);
        assertNull(result2);
    }
}