package com.example.rocketmq.config;

import org.apache.rocketmq.client.consumer.DefaultMQPushConsumer;
import org.apache.rocketmq.client.producer.DefaultMQProducer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * RocketMQ配置类
 */
@Configuration
public class RocketMQConfig {

    @Value("${rocketmq.name-server:127.0.0.1:9876}")
    private String nameServer;

    @Value("${rocketmq.producer.group:dedup-producer-group}")
    private String producerGroup;

    @Value("${rocketmq.consumer.group:dedup-consumer-group}")
    private String consumerGroup;

    /**
     * 生产者配置
     */
    @Bean
    public DefaultMQProducer producer() throws Exception {
        DefaultMQProducer producer = new DefaultMQProducer(producerGroup);
        producer.setNamesrvAddr(nameServer);
        // 设置消息去重相关配置
        producer.setRetryTimesWhenSendFailed(3);
        producer.setRetryAnotherBrokerWhenNotStoreOK(true);
        producer.start();
        return producer;
    }

    /**
     * 消费者配置
     */
    @Bean
    public DefaultMQPushConsumer consumer() throws Exception {
        DefaultMQPushConsumer consumer = new DefaultMQPushConsumer(consumerGroup);
        consumer.setNamesrvAddr(nameServer);
        // 设置消费模式为集群模式（避免重复消费）
        consumer.setMessageModel(org.apache.rocketmq.common.protocol.heartbeat.MessageModel.CLUSTERING);
        // 设置最大重试次数
        consumer.setMaxReconsumeTimes(3);
        return consumer;
    }
}