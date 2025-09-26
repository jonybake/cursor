# Spring Boot 限流框架架构说明

## 项目结构

```
src/main/java/com/example/ratelimiter/
├── annotation/                    # 注解定义
│   └── RateLimit.java            # 限流注解
├── aspect/                       # AOP切面
│   └── RateLimitAspect.java      # 限流切面实现
├── autoconfigure/                # 自动配置
│   └── RateLimiterAutoConfiguration.java
├── config/                       # 配置类
│   ├── RateLimiterConfig.java    # 限流器配置
│   └── RateLimiterProperties.java # 配置属性
├── core/                         # 核心接口
│   ├── RateLimiter.java          # 限流器接口
│   ├── AbstractRateLimiter.java  # 抽象基类
│   └── RateLimiterType.java      # 限流器类型枚举
├── algorithm/                    # 限流算法实现
│   ├── TokenBucketRateLimiter.java      # 令牌桶算法
│   ├── SlidingWindowRateLimiter.java    # 滑动窗口算法
│   └── FixedWindowRateLimiter.java      # 固定窗口算法
├── manager/                      # 管理器
│   └── RateLimiterManager.java   # 限流器管理器
├── exception/                    # 异常处理
│   ├── RateLimitExceededException.java  # 限流异常
│   └── RateLimitExceptionHandler.java  # 异常处理器
├── model/                        # 数据模型
│   └── RateLimitResponse.java    # 限流响应模型
└── controller/                   # 测试控制器
    └── RateLimitTestController.java
```

## 核心组件

### 1. 注解层 (Annotation Layer)
- **RateLimit**: 限流注解，支持多种参数配置
- 支持SpEL表达式动态生成限流键
- 支持方法级和类级限流配置

### 2. AOP切面层 (Aspect Layer)
- **RateLimitAspect**: 拦截带有@RateLimit注解的方法
- 解析SpEL表达式生成限流键
- 调用限流器进行限流判断
- 处理限流异常

### 3. 核心接口层 (Core Layer)
- **RateLimiter**: 限流器核心接口
- **AbstractRateLimiter**: 抽象基类，提供通用功能
- **RateLimiterType**: 限流器类型枚举

### 4. 算法实现层 (Algorithm Layer)
- **TokenBucketRateLimiter**: 令牌桶算法实现
- **SlidingWindowRateLimiter**: 滑动窗口算法实现
- **FixedWindowRateLimiter**: 固定窗口算法实现

### 5. 管理层 (Manager Layer)
- **RateLimiterManager**: 限流器管理器
- 统一管理所有限流器实例
- 提供限流器获取和统计功能

### 6. 配置层 (Configuration Layer)
- **RateLimiterProperties**: 配置属性类
- **RateLimiterConfig**: 限流器配置类
- **RateLimiterAutoConfiguration**: 自动配置类

### 7. 异常处理层 (Exception Layer)
- **RateLimitExceededException**: 限流异常
- **RateLimitExceptionHandler**: 全局异常处理器
- **RateLimitResponse**: 统一响应格式

## 工作流程

1. **请求进入**: 用户请求到达Controller方法
2. **AOP拦截**: RateLimitAspect拦截带有@RateLimit注解的方法
3. **键解析**: 解析SpEL表达式生成限流键
4. **限流判断**: 调用对应的限流器进行限流判断
5. **缓存操作**: 使用Caffeine进行本地缓存操作
6. **结果处理**: 根据限流结果决定是否允许请求通过
7. **异常处理**: 如果限流失败，抛出RateLimitExceededException
8. **响应返回**: 返回限流结果或业务结果

## 限流算法对比

| 算法 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 令牌桶 | 允许突发流量，平滑限流 | 实现相对复杂 | 需要平滑限流的场景 |
| 滑动窗口 | 精确控制，实时统计 | 内存占用较大 | 需要精确限流的场景 |
| 固定窗口 | 简单高效，内存占用小 | 精度较低，边界问题 | 对精度要求不高的场景 |

## 扩展点

1. **自定义限流算法**: 实现RateLimiter接口
2. **自定义限流键生成器**: 扩展SpEL表达式支持
3. **分布式限流**: 集成Redis实现分布式限流
4. **监控集成**: 集成Micrometer等监控框架
5. **配置热更新**: 支持运行时配置更新

## 性能特点

- **高性能**: 使用Caffeine本地缓存，避免频繁计算
- **低延迟**: AOP切面开销极小
- **内存友好**: 支持键过期和最大数量限制
- **线程安全**: 所有算法实现都是线程安全的
- **可扩展**: 支持自定义算法和配置