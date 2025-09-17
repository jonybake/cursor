# RocketMQ 消息去重示例

本项目演示了如何在RocketMQ中实现消息去重功能，包括基于消息ID的去重、基于业务键的去重以及幂等性消费。

## 功能特性

### 1. 消息去重机制

- **基于消息ID去重**: 使用Redis的SETNX命令确保相同消息ID的消息只被处理一次
- **基于业务键去重**: 支持基于业务逻辑键（如订单ID、支付ID等）进行去重
- **综合去重检查**: 同时检查消息ID和业务键，确保消息不重复

### 2. 幂等性消费

- **消费状态记录**: 在Redis中记录消息的消费状态
- **重复消费检测**: 消费前检查消息是否已被处理过
- **消费状态标记**: 成功处理后标记消息为已消费

### 3. 业务场景示例

- **订单消息**: 使用订单ID作为业务键进行去重
- **支付消息**: 使用支付ID作为业务键进行去重
- **用户消息**: 使用用户ID+操作类型作为业务键进行去重

## 项目结构

```
src/main/java/com/example/rocketmq/
├── RocketMQDeduplicationApplication.java    # 主启动类
├── config/
│   ├── RocketMQConfig.java                 # RocketMQ配置
│   └── ConsumerConfig.java                 # 消费者配置
├── controller/
│   └── MessageController.java              # REST API控制器
├── model/
│   └── MessageWrapper.java                 # 消息包装类
└── service/
    ├── DeduplicationService.java           # 去重服务
    ├── MessageProducerService.java         # 生产者服务
    └── MessageConsumerService.java         # 消费者服务
```

## 快速开始

### 1. 环境准备

- JDK 8+
- Maven 3.6+
- RocketMQ 4.9.4+
- Redis 6.0+

### 2. 启动RocketMQ

```bash
# 启动NameServer
nohup sh mqnamesrv &

# 启动Broker
nohup sh mqbroker -n localhost:9876 &
```

### 3. 启动Redis

```bash
redis-server
```

### 4. 运行应用

```bash
mvn spring-boot:run
```

## API接口

### 发送消息

```bash
# 发送普通消息
curl -X POST "http://localhost:8080/api/message/send" \
  -d "topic=TEST_TOPIC&tags=TEST_TAG&content=测试消息&businessKey=test-key-1"

# 发送订单消息
curl -X POST "http://localhost:8080/api/message/order" \
  -d "orderId=ORDER-001&userId=USER-001&amount=100.00"

# 发送支付消息
curl -X POST "http://localhost:8080/api/message/payment" \
  -d "paymentId=PAY-001&orderId=ORDER-001&amount=100.00"

# 发送用户消息
curl -X POST "http://localhost:8080/api/message/user" \
  -d "userId=USER-001&action=LOGIN&details=用户登录"
```

### 批量测试去重

```bash
# 批量发送测试消息（测试去重功能）
curl -X POST "http://localhost:8080/api/message/batch-test?count=10"
```

## 去重策略详解

### 1. 消息ID去重

```java
// 使用Redis的SETNX命令实现原子性去重检查
Boolean isSet = redisTemplate.opsForValue().setIfAbsent(
    "msg:id:" + messageId, 
    "1", 
    Duration.ofMinutes(30)
);
```

### 2. 业务键去重

```java
// 基于业务逻辑键进行去重
Boolean isSet = redisTemplate.opsForValue().setIfAbsent(
    "msg:business:" + businessKey, 
    "1", 
    Duration.ofMinutes(30)
);
```

### 3. 消费幂等性

```java
// 检查消息是否已被消费
String consumeKey = "msg:consume:" + consumerGroup + ":" + messageId;
Boolean exists = redisTemplate.hasKey(consumeKey);

// 标记消息为已消费
redisTemplate.opsForValue().set(consumeKey, "1", Duration.ofMinutes(60));
```

## 配置说明

### application.yml

```yaml
rocketmq:
  name-server: 127.0.0.1:9876          # RocketMQ NameServer地址
  producer:
    group: dedup-producer-group         # 生产者组
  consumer:
    group: dedup-consumer-group         # 消费者组
    topics: ORDER_TOPIC,PAYMENT_TOPIC   # 订阅的主题

spring:
  redis:
    host: localhost                     # Redis地址
    port: 6379                          # Redis端口
    database: 0                         # Redis数据库
```

## 最佳实践

### 1. 消息ID生成

- 使用UUID确保全局唯一性
- 可以结合业务信息生成有意义的ID
- 考虑在高并发场景下的性能

### 2. 业务键设计

- 选择具有业务意义的唯一标识
- 考虑键的长度和复杂度
- 避免使用可能重复的键

### 3. 过期时间设置

- 根据业务需求设置合理的过期时间
- 考虑消息处理的最大延迟时间
- 避免过期时间过短导致重复处理

### 4. 错误处理

- 实现重试机制
- 记录详细的错误日志
- 考虑死信队列处理

## 监控和运维

### 1. 日志监控

- 监控去重相关的日志
- 关注重复消息的统计
- 监控Redis连接状态

### 2. 性能监控

- 监控消息处理延迟
- 监控Redis操作性能
- 监控RocketMQ消费性能

### 3. 告警设置

- 设置重复消息率告警
- 设置消费延迟告警
- 设置Redis连接异常告警

## 常见问题

### 1. 消息重复消费

- 检查消费者组配置
- 确认去重逻辑是否正确
- 检查Redis连接状态

### 2. 去重失效

- 检查Redis键的过期时间
- 确认业务键的唯一性
- 检查并发处理逻辑

### 3. 性能问题

- 优化Redis操作
- 考虑使用Redis集群
- 调整消费者并发数

## 扩展功能

### 1. 分布式锁

可以使用Redis分布式锁进一步确保去重逻辑的原子性：

```java
@Autowired
private RedisTemplate<String, Object> redisTemplate;

public boolean tryLock(String key, long expireTime) {
    return Boolean.TRUE.equals(redisTemplate.opsForValue()
        .setIfAbsent("lock:" + key, "1", Duration.ofSeconds(expireTime)));
}
```

### 2. 消息去重统计

可以添加统计功能来监控去重效果：

```java
@Autowired
private RedisTemplate<String, Object> redisTemplate;

public void incrementDuplicateCount(String topic) {
    redisTemplate.opsForValue().increment("stats:duplicate:" + topic);
}
```

### 3. 多级去重

可以实现多级去重策略：

1. 第一级：基于消息ID
2. 第二级：基于业务键
3. 第三级：基于消息内容哈希

## 总结

本示例提供了完整的RocketMQ消息去重解决方案，包括：

- 多种去重策略的实现
- 幂等性消费保证
- 完整的业务场景示例
- 详细的配置和监控说明

通过合理使用这些去重机制，可以确保消息系统的可靠性和一致性。