# Spring Boot 限流框架

一个功能完整、易于使用的Spring Boot限流框架，支持多种限流算法和灵活的配置选项。

## 特性

- 🚀 **多种限流算法**：支持令牌桶、滑动窗口、固定窗口三种限流算法
- 🎯 **注解驱动**：通过简单的注解即可实现限流功能
- ⚙️ **灵活配置**：支持全局配置和局部配置，满足不同场景需求
- 🔧 **SpEL表达式**：支持使用SpEL表达式动态生成限流键
- 📊 **监控支持**：内置监控和统计功能
- 🛡️ **异常处理**：完善的异常处理和响应机制
- 🔄 **自动配置**：Spring Boot自动配置，开箱即用

## 快速开始

### 1. 添加依赖

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>rate-limiter-framework</artifactId>
    <version>1.0.0</version>
</dependency>
```

### 2. 配置限流器

```yaml
rate-limiter:
  enabled: true
  default-type: token-bucket
  capacity: 100
  window-size: 60000
  refill-rate: 10
  refill-period: 1000
  max-keys: 10000
  expire-minutes: 60
  timeout: 5000
  retry-interval: 100
  distributed: false
  redis-key-prefix: "rate_limiter:"
  monitoring: true
```

### 3. 使用注解

```java
@RestController
public class ApiController {
    
    @GetMapping("/api/users")
    @RateLimit(
        key = "#userId",
        type = RateLimiterType.TOKEN_BUCKET,
        capacity = 10,
        refillRate = 2,
        refillPeriod = 1000
    )
    public ResponseEntity<User> getUser(@RequestParam String userId) {
        // 业务逻辑
        return ResponseEntity.ok(userService.getUser(userId));
    }
}
```

## 限流算法

### 1. 令牌桶算法 (Token Bucket)

令牌桶算法以固定速率向桶中添加令牌，请求需要消耗令牌才能通过。

**适用场景**：允许突发流量，适合需要平滑限流的场景。

```java
@RateLimit(
    type = RateLimiterType.TOKEN_BUCKET,
    capacity = 100,        // 桶容量
    refillRate = 10,       // 补充速率
    refillPeriod = 1000    // 补充周期(毫秒)
)
```

### 2. 滑动窗口算法 (Sliding Window)

滑动窗口算法在时间窗口内统计请求次数，超过限制则拒绝请求。

**适用场景**：需要精确控制请求频率的场景。

```java
@RateLimit(
    type = RateLimiterType.SLIDING_WINDOW,
    capacity = 100,        // 窗口内最大请求数
    windowSize = 60000     // 窗口大小(毫秒)
)
```

### 3. 固定窗口算法 (Fixed Window)

固定窗口算法将时间分割成固定大小的窗口，每个窗口内限制请求次数。

**适用场景**：对精度要求不高，但需要简单高效的限流。

```java
@RateLimit(
    type = RateLimiterType.FIXED_WINDOW,
    capacity = 100,        // 窗口内最大请求数
    windowSize = 60000     // 窗口大小(毫秒)
)
```

## 注解参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| key | String | "" | 限流键，支持SpEL表达式 |
| type | RateLimiterType | TOKEN_BUCKET | 限流器类型 |
| capacity | long | 100 | 容量 |
| windowSize | long | 60000 | 窗口大小(毫秒) |
| refillRate | long | 10 | 令牌桶补充速率 |
| refillPeriod | long | 1000 | 令牌桶补充周期(毫秒) |
| permits | int | 1 | 许可数量 |
| blocking | boolean | false | 是否阻塞等待 |
| timeout | long | 5000 | 超时时间(毫秒) |
| message | String | "Rate limit exceeded" | 限流失败消息 |

## SpEL表达式支持

限流键支持SpEL表达式，可以动态生成：

```java
@RateLimit(key = "#userId + ':' + #apiType")
public ResponseEntity<Object> getData(@RequestParam String userId, @RequestParam String apiType) {
    // 业务逻辑
}

@RateLimit(key = "#request.getRemoteAddr()")
public ResponseEntity<Object> getData(HttpServletRequest request) {
    // 业务逻辑
}
```

## 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| rate-limiter.enabled | boolean | true | 是否启用限流器 |
| rate-limiter.default-type | String | token-bucket | 默认限流器类型 |
| rate-limiter.capacity | long | 100 | 默认容量 |
| rate-limiter.window-size | long | 60000 | 默认窗口大小 |
| rate-limiter.refill-rate | long | 10 | 默认补充速率 |
| rate-limiter.refill-period | long | 1000 | 默认补充周期 |
| rate-limiter.max-keys | int | 10000 | 最大键数量 |
| rate-limiter.expire-minutes | int | 60 | 键过期时间 |
| rate-limiter.timeout | long | 5000 | 获取许可超时时间 |
| rate-limiter.retry-interval | long | 100 | 重试间隔 |
| rate-limiter.distributed | boolean | false | 是否启用分布式限流 |
| rate-limiter.redis-key-prefix | String | "rate_limiter:" | Redis键前缀 |
| rate-limiter.monitoring | boolean | true | 是否启用监控 |

## 异常处理

框架提供了完善的异常处理机制：

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(RateLimitExceededException.class)
    public ResponseEntity<RateLimitResponse> handleRateLimitExceeded(RateLimitExceededException ex) {
        // 自定义异常处理逻辑
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .header("Retry-After", String.valueOf(ex.getRetryAfter() / 1000))
                .body(RateLimitResponse.builder()
                        .success(false)
                        .message("Rate limit exceeded")
                        .key(ex.getKey())
                        .availablePermits(ex.getAvailablePermits())
                        .retryAfter(ex.getRetryAfter())
                        .build());
    }
}
```

## 测试接口

框架提供了测试接口，方便验证限流功能：

- `GET /api/rate-limit/token-bucket?userId=123` - 令牌桶测试
- `GET /api/rate-limit/sliding-window?ip=192.168.1.1` - 滑动窗口测试
- `GET /api/rate-limit/fixed-window?apiKey=abc123` - 固定窗口测试
- `GET /api/rate-limit/blocking?requestId=req123` - 阻塞式限流测试
- `GET /api/rate-limit/multi-permit?resourceId=res123` - 多许可消费测试
- `GET /api/rate-limit/health` - 健康检查

## 运行示例

1. 启动应用：
```bash
mvn spring-boot:run
```

2. 测试限流功能：
```bash
# 快速发送请求测试限流
for i in {1..20}; do
  curl "http://localhost:8080/api/rate-limit/token-bucket?userId=123"
  echo
done
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个框架。