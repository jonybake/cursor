package com.example.rocketmq.controller;

import com.example.rocketmq.service.MessageProducerService;
import lombok.extern.slf4j.Slf4j;
import org.apache.rocketmq.client.producer.SendResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 消息控制器 - 用于测试消息去重功能
 */
@Slf4j
@RestController
@RequestMapping("/api/message")
public class MessageController {

    @Autowired
    private MessageProducerService messageProducerService;

    /**
     * 发送测试消息
     */
    @PostMapping("/send")
    public Map<String, Object> sendMessage(@RequestParam String topic,
                                         @RequestParam String tags,
                                         @RequestParam String content,
                                         @RequestParam(required = false) String businessKey) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            SendResult sendResult = messageProducerService.sendMessage(topic, tags, content, businessKey);
            
            if (sendResult != null) {
                result.put("success", true);
                result.put("messageId", sendResult.getMsgId());
                result.put("sendStatus", sendResult.getSendStatus());
                result.put("message", "消息发送成功");
            } else {
                result.put("success", false);
                result.put("message", "消息重复，未发送");
            }
            
        } catch (Exception e) {
            log.error("发送消息失败", e);
            result.put("success", false);
            result.put("message", "发送失败: " + e.getMessage());
        }
        
        return result;
    }

    /**
     * 发送订单消息
     */
    @PostMapping("/order")
    public Map<String, Object> sendOrderMessage(@RequestParam String orderId,
                                              @RequestParam String userId,
                                              @RequestParam Double amount) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            SendResult sendResult = messageProducerService.sendOrderMessage(orderId, userId, amount);
            
            if (sendResult != null) {
                result.put("success", true);
                result.put("messageId", sendResult.getMsgId());
                result.put("message", "订单消息发送成功");
            } else {
                result.put("success", false);
                result.put("message", "订单消息重复，未发送");
            }
            
        } catch (Exception e) {
            log.error("发送订单消息失败", e);
            result.put("success", false);
            result.put("message", "发送失败: " + e.getMessage());
        }
        
        return result;
    }

    /**
     * 发送支付消息
     */
    @PostMapping("/payment")
    public Map<String, Object> sendPaymentMessage(@RequestParam String paymentId,
                                                @RequestParam String orderId,
                                                @RequestParam Double amount) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            SendResult sendResult = messageProducerService.sendPaymentMessage(paymentId, orderId, amount);
            
            if (sendResult != null) {
                result.put("success", true);
                result.put("messageId", sendResult.getMsgId());
                result.put("message", "支付消息发送成功");
            } else {
                result.put("success", false);
                result.put("message", "支付消息重复，未发送");
            }
            
        } catch (Exception e) {
            log.error("发送支付消息失败", e);
            result.put("success", false);
            result.put("message", "发送失败: " + e.getMessage());
        }
        
        return result;
    }

    /**
     * 发送用户消息
     */
    @PostMapping("/user")
    public Map<String, Object> sendUserMessage(@RequestParam String userId,
                                             @RequestParam String action,
                                             @RequestParam String details) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            SendResult sendResult = messageProducerService.sendUserMessage(userId, action, details);
            
            if (sendResult != null) {
                result.put("success", true);
                result.put("messageId", sendResult.getMsgId());
                result.put("message", "用户消息发送成功");
            } else {
                result.put("success", false);
                result.put("message", "用户消息重复，未发送");
            }
            
        } catch (Exception e) {
            log.error("发送用户消息失败", e);
            result.put("success", false);
            result.put("message", "发送失败: " + e.getMessage());
        }
        
        return result;
    }

    /**
     * 批量发送测试消息（用于测试去重功能）
     */
    @PostMapping("/batch-test")
    public Map<String, Object> batchTest(@RequestParam(defaultValue = "5") int count) {
        Map<String, Object> result = new HashMap<>();
        int successCount = 0;
        int duplicateCount = 0;
        
        for (int i = 0; i < count; i++) {
            try {
                // 使用相同的业务键来测试去重
                String businessKey = "test-batch-" + (i % 3); // 只有3个不同的业务键
                SendResult sendResult = messageProducerService.sendMessage(
                    "TEST_TOPIC", 
                    "TEST_TAG", 
                    "批量测试消息 " + i, 
                    businessKey
                );
                
                if (sendResult != null) {
                    successCount++;
                } else {
                    duplicateCount++;
                }
                
            } catch (Exception e) {
                log.error("批量发送消息失败", e);
            }
        }
        
        result.put("success", true);
        result.put("totalCount", count);
        result.put("successCount", successCount);
        result.put("duplicateCount", duplicateCount);
        result.put("message", String.format("批量测试完成 - 成功: %d, 重复: %d", successCount, duplicateCount));
        
        return result;
    }
}