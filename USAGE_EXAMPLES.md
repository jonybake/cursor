# 使用示例

## 1. 基础使用

### 简单限流
```java
@RestController
public class UserController {
    
    @GetMapping("/users/{id}")
    @RateLimit(key = "#id", capacity = 10)
    public User getUser(@PathVariable String id) {
        return userService.findById(id);
    }
}
```

### 按IP限流
```java
@RestController
public class ApiController {
    
    @PostMapping("/api/data")
    @RateLimit(
        key = "#request.getRemoteAddr()",
        type = RateLimiterType.SLIDING_WINDOW,
        capacity = 100,
        windowSize = 60000
    )
    public ResponseEntity<Data> createData(@RequestBody Data data, HttpServletRequest request) {
        return ResponseEntity.ok(dataService.create(data));
    }
}
```

## 2. 高级配置

### 令牌桶配置
```java
@RestController
public class PaymentController {
    
    @PostMapping("/payments")
    @RateLimit(
        key = "#userId + ':' + #paymentType",
        type = RateLimiterType.TOKEN_BUCKET,
        capacity = 50,
        refillRate = 5,
        refillPeriod = 1000,
        permits = 2
    )
    public PaymentResult processPayment(
            @RequestParam String userId,
            @RequestParam String paymentType,
            @RequestBody PaymentRequest request) {
        return paymentService.process(request);
    }
}
```

### 阻塞式限流
```java
@RestController
public class FileController {
    
    @PostMapping("/files/upload")
    @RateLimit(
        key = "#userId",
        type = RateLimiterType.TOKEN_BUCKET,
        capacity = 5,
        refillRate = 1,
        refillPeriod = 2000,
        blocking = true,
        timeout = 30000
    )
    public FileUploadResult uploadFile(
            @RequestParam String userId,
            @RequestParam MultipartFile file) {
        return fileService.upload(file);
    }
}
```

## 3. 类级别限流

```java
@RestController
@RateLimit(key = "#request.getRemoteAddr()", capacity = 20)
public class ApiController {
    
    @GetMapping("/api/users")
    public List<User> getUsers(HttpServletRequest request) {
        return userService.findAll();
    }
    
    @GetMapping("/api/orders")
    public List<Order> getOrders(HttpServletRequest request) {
        return orderService.findAll();
    }
    
    // 方法级别配置会覆盖类级别配置
    @PostMapping("/api/users")
    @RateLimit(key = "#user.email", capacity = 5)
    public User createUser(@RequestBody User user) {
        return userService.create(user);
    }
}
```

## 4. 自定义限流键

### 使用SpEL表达式
```java
@RestController
public class OrderController {
    
    @GetMapping("/orders")
    @RateLimit(
        key = "#userId + ':' + #orderStatus + ':' + T(java.time.LocalDate).now()",
        capacity = 100
    )
    public List<Order> getOrders(
            @RequestParam String userId,
            @RequestParam String orderStatus) {
        return orderService.findByUserAndStatus(userId, orderStatus);
    }
}
```

### 复杂表达式
```java
@RestController
public class ReportController {
    
    @GetMapping("/reports")
    @RateLimit(
        key = "#request.getHeader('X-API-Key') + ':' + #reportType + ':' + T(java.time.LocalDateTime).now().getHour()",
        capacity = 10,
        windowSize = 3600000  // 1小时窗口
    )
    public Report generateReport(
            @RequestParam String reportType,
            HttpServletRequest request) {
        return reportService.generate(reportType);
    }
}
```

## 5. 配置示例

### application.yml
```yaml
rate-limiter:
  enabled: true
  default-type: token-bucket
  capacity: 1000
  window-size: 60000
  refill-rate: 100
  refill-period: 1000
  max-keys: 50000
  expire-minutes: 120
  timeout: 10000
  retry-interval: 50
  monitoring: true

# 不同环境的配置
---
spring:
  profiles: production
rate-limiter:
  capacity: 10000
  max-keys: 100000
  distributed: true
  redis-key-prefix: "prod:rate_limiter:"

---
spring:
  profiles: test
rate-limiter:
  capacity: 10
  max-keys: 100
  monitoring: false
```

## 6. 异常处理

### 全局异常处理
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(RateLimitExceededException.class)
    public ResponseEntity<Map<String, Object>> handleRateLimitExceeded(
            RateLimitExceededException ex) {
        
        Map<String, Object> response = new HashMap<>();
        response.put("error", "Rate limit exceeded");
        response.put("key", ex.getKey());
        response.put("availablePermits", ex.getAvailablePermits());
        response.put("retryAfter", ex.getRetryAfter());
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .header("Retry-After", String.valueOf(ex.getRetryAfter() / 1000))
                .body(response);
    }
}
```

### 自定义限流响应
```java
@RestController
public class CustomController {
    
    @GetMapping("/custom")
    @RateLimit(key = "#userId", capacity = 5)
    public ResponseEntity<Object> customEndpoint(@RequestParam String userId) {
        try {
            // 业务逻辑
            return ResponseEntity.ok("Success");
        } catch (RateLimitExceededException e) {
            // 自定义处理
            Map<String, Object> error = new HashMap<>();
            error.put("message", "请求过于频繁，请稍后再试");
            error.put("retryAfter", e.getRetryAfter());
            return ResponseEntity.status(429).body(error);
        }
    }
}
```

## 7. 监控和统计

### 获取限流器统计
```java
@RestController
public class MonitorController {
    
    @Autowired
    private RateLimiterManager rateLimiterManager;
    
    @GetMapping("/monitor/stats")
    public Map<String, Object> getStats() {
        return rateLimiterManager.getStatistics();
    }
    
    @GetMapping("/monitor/available/{type}/{key}")
    public Map<String, Object> getAvailablePermits(
            @PathVariable String type,
            @PathVariable String key) {
        
        RateLimiterType rateLimiterType = RateLimiterType.fromValue(type);
        RateLimiter rateLimiter = rateLimiterManager.getRateLimiter(rateLimiterType);
        
        Map<String, Object> result = new HashMap<>();
        result.put("key", key);
        result.put("type", type);
        result.put("availablePermits", rateLimiter.getAvailablePermits(key));
        
        return result;
    }
}
```

## 8. 测试示例

### 单元测试
```java
@SpringBootTest
public class RateLimiterTest {
    
    @Autowired
    private RateLimiterManager rateLimiterManager;
    
    @Test
    public void testTokenBucketRateLimiter() {
        RateLimiter rateLimiter = rateLimiterManager.getRateLimiter(RateLimiterType.TOKEN_BUCKET);
        String key = "test-key";
        
        // 测试正常获取
        assertTrue(rateLimiter.tryAcquire(key));
        
        // 测试超出限制
        for (int i = 0; i < 100; i++) {
            rateLimiter.tryAcquire(key);
        }
        assertFalse(rateLimiter.tryAcquire(key));
    }
}
```

### 集成测试
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class RateLimiterIntegrationTest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    public void testRateLimitEndpoint() {
        String url = "/api/rate-limit/token-bucket?userId=123";
        
        // 发送多个请求测试限流
        for (int i = 0; i < 15; i++) {
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            if (i < 10) {
                assertEquals(HttpStatus.OK, response.getStatusCode());
            } else {
                assertEquals(HttpStatus.TOO_MANY_REQUESTS, response.getStatusCode());
            }
        }
    }
}
```

这些示例展示了框架的各种使用场景和配置选项，可以根据实际需求选择合适的配置方式。