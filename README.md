# Rate Limiter Spring Boot Starter

一个功能完整的Spring Boot限流框架，支持多种限流算法和分布式限流。

## 特性

- 🚀 **多种限流算法**：支持令牌桶算法和滑动窗口算法
- 🌐 **分布式限流**：支持Redis分布式限流
- 📝 **注解式配置**：简单易用的注解配置
- 🔧 **灵活配置**：支持SpEL表达式和多种配置方式
- ⚡ **高性能**：基于Guava RateLimiter和Redis Lua脚本
- 🛡️ **异常处理**：完善的异常处理和错误信息
- 📊 **监控支持**：支持Spring Boot Actuator监控

## 快速开始

### 1. 添加依赖

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>rate-limiter-spring-boot-starter</artifactId>
    <version>1.0.0</version>
</dependency>
```

### 2. 配置限流

在`application.yml`中配置：

```yaml
rate-limiter:
  type: local  # local 或 redis
  algorithm: token-bucket  # token-bucket 或 sliding-window
  default-config:
    permits-per-second: 10
    burst-capacity: 20
    window-size: 60
    window-permits: 100
```

### 3. 使用注解

```java
@RestController
public class ApiController {
    
    @GetMapping("/api/test")
    @RateLimiter(permitsPerSecond = 5, burstCapacity = 10)
    public String test() {
        return "success";
    }
    
    @GetMapping("/api/user/{userId}")
    @RateLimiter(key = "#userId", permitsPerSecond = 3)
    public String userApi(@PathVariable String userId) {
        return "user: " + userId;
    }
}
```

## 详细使用说明

### 注解配置

#### @RateLimiter 注解参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| key | String | "" | 限流key，支持SpEL表达式 |
| algorithm | Algorithm | TOKEN_BUCKET | 限流算法类型 |
| permitsPerSecond | int | -1 | 每秒允许的请求数（令牌桶） |
| burstCapacity | int | -1 | 突发请求数（令牌桶） |
| windowSize | int | -1 | 时间窗口大小（秒）（滑动窗口） |
| windowPermits | int | -1 | 时间窗口内允许的请求数（滑动窗口） |
| message | String | "请求过于频繁，请稍后再试" | 限流失败提示信息 |
| statusCode | int | 429 | 限流失败HTTP状态码 |

#### 限流算法

**令牌桶算法 (TOKEN_BUCKET)**
- 适合处理突发流量
- 允许短时间内的突发请求
- 配置参数：`permitsPerSecond`、`burstCapacity`

**滑动窗口算法 (SLIDING_WINDOW)**
- 适合精确控制时间窗口内的请求数
- 更严格的限流控制
- 配置参数：`windowSize`、`windowPermits`

### 配置示例

#### 本地限流配置

```yaml
rate-limiter:
  type: local
  algorithm: token-bucket
  default-config:
    permits-per-second: 10
    burst-capacity: 20
```

#### Redis分布式限流配置

```yaml
rate-limiter:
  type: redis
  algorithm: sliding-window
  default-config:
    window-size: 60
    window-permits: 100
  redis:
    key-prefix: "rate_limiter:"
    script-cache: true

spring:
  redis:
    host: localhost
    port: 6379
    database: 0
```

### 使用示例

#### 1. 基础限流

```java
@RestController
public class BasicController {
    
    @GetMapping("/basic")
    @RateLimiter
    public String basic() {
        return "basic rate limit";
    }
}
```

#### 2. 自定义配置限流

```java
@RestController
public class CustomController {
    
    @GetMapping("/custom")
    @RateLimiter(
        algorithm = RateLimiter.Algorithm.TOKEN_BUCKET,
        permitsPerSecond = 5,
        burstCapacity = 10,
        message = "自定义限流信息"
    )
    public String custom() {
        return "custom rate limit";
    }
}
```

#### 3. 基于用户ID限流

```java
@RestController
public class UserController {
    
    @GetMapping("/user/{userId}")
    @RateLimiter(
        key = "#userId",
        permitsPerSecond = 3,
        message = "用户请求过于频繁"
    )
    public String userApi(@PathVariable String userId) {
        return "user: " + userId;
    }
}
```

#### 4. 基于方法参数限流

```java
@RestController
public class ParamController {
    
    @PostMapping("/action")
    @RateLimiter(
        key = "#requestId + ':' + #action",
        algorithm = RateLimiter.Algorithm.SLIDING_WINDOW,
        windowSize = 60,
        windowPermits = 10
    )
    public String action(@RequestParam String requestId, 
                        @RequestParam String action) {
        return "action: " + action;
    }
}
```

#### 5. 类级别限流

```java
@RestController
@RateLimiter(permitsPerSecond = 2, burstCapacity = 5)
public class ClassLevelController {
    
    @GetMapping("/method1")
    public String method1() {
        return "method1";
    }
    
    @GetMapping("/method2")
    public String method2() {
        return "method2";
    }
}
```

### 异常处理

框架提供了完善的异常处理机制：

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(RateLimiterException.class)
    public ResponseEntity<Map<String, Object>> handleRateLimiterException(
            RateLimiterException e) {
        Map<String, Object> response = new HashMap<>();
        response.put("error", "Rate limit exceeded");
        response.put("message", e.getMessage());
        response.put("remainingPermits", e.getRemainingPermits());
        response.put("resetTime", e.getResetTime());
        return ResponseEntity.status(429).body(response);
    }
}
```

### 监控和调试

#### 启用调试日志

```yaml
logging:
  level:
    com.example.ratelimiter: DEBUG
```

#### 健康检查

框架集成了Spring Boot Actuator，可以通过以下端点监控限流状态：

- `/actuator/health` - 健康检查
- `/actuator/metrics` - 指标监控

## 测试

运行测试：

```bash
mvn test
```

运行演示应用：

```bash
mvn spring-boot:run
```

测试API端点：

```bash
# 基础限流测试
curl http://localhost:8080/api/rate-limiter/basic

# 令牌桶限流测试
curl http://localhost:8080/api/rate-limiter/token-bucket

# 滑动窗口限流测试
curl http://localhost:8080/api/rate-limiter/sliding-window

# 用户限流测试
curl http://localhost:8080/api/rate-limiter/user/user123

# 参数限流测试
curl -X POST "http://localhost:8080/api/rate-limiter/param-based?requestId=req123&action=test"
```

## 架构设计

### 核心组件

1. **RateLimiterAlgorithm** - 限流算法接口
2. **RateLimiterService** - 限流服务接口
3. **RateLimiterAspect** - AOP切面实现
4. **RateLimiterProperties** - 配置属性
5. **RateLimiterAutoConfiguration** - 自动配置

### 限流算法实现

- **TokenBucketRateLimiter** - 基于Guava RateLimiter的令牌桶实现
- **SlidingWindowRateLimiter** - 基于时间桶的滑动窗口实现

### 分布式限流

- **RedisRateLimiterService** - 基于Redis Lua脚本的分布式限流
- 支持Redis集群和哨兵模式
- 使用Lua脚本保证原子性操作

## 性能优化

1. **本地缓存** - 使用ConcurrentHashMap缓存限流器
2. **Lua脚本** - Redis操作使用Lua脚本保证原子性
3. **异步清理** - 定时清理过期的限流数据
4. **连接池** - Redis连接池优化

## 注意事项

1. 本地限流适用于单机应用
2. 分布式限流需要Redis支持
3. 限流key的设计要考虑业务场景
4. 合理设置限流参数避免误杀正常请求
5. 监控限流效果及时调整参数

## 许可证

MIT License