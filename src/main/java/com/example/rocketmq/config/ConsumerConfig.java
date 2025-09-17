package com.example.rocketmq.config;

import com.example.rocketmq.service.MessageConsumerService;
import lombok.extern.slf4j.Slf4j;
import org.apache.rocketmq.client.consumer.DefaultMQPushConsumer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

/**
 * 消费者配置和启动类
 */
@Slf4j
@Configuration
public class ConsumerConfig {

    @Autowired
    private DefaultMQPushConsumer consumer;

    @Autowired
    private MessageConsumerService messageConsumerService;

    @Value("${rocketmq.consumer.topics:ORDER_TOPIC,PAYMENT_TOPIC,USER_TOPIC,TEST_TOPIC}")
    private String topics;

    @PostConstruct
    public void startConsumer() {
        try {
            // 设置消息监听器
            consumer.setMessageListener(messageConsumerService);
            
            // 订阅主题
            String[] topicArray = topics.split(",");
            for (String topic : topicArray) {
                consumer.subscribe(topic.trim(), "*"); // 订阅所有标签
                log.info("订阅主题: {}", topic.trim());
            }
            
            // 启动消费者
            consumer.start();
            log.info("RocketMQ消费者启动成功");
            
        } catch (Exception e) {
            log.error("启动RocketMQ消费者失败", e);
        }
    }

    @PreDestroy
    public void stopConsumer() {
        try {
            if (consumer != null) {
                consumer.shutdown();
                log.info("RocketMQ消费者已关闭");
            }
        } catch (Exception e) {
            log.error("关闭RocketMQ消费者失败", e);
        }
    }
}