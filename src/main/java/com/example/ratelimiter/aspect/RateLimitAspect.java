package com.example.ratelimiter.aspect;

import com.example.ratelimiter.annotation.RateLimit;
import com.example.ratelimiter.core.RateLimiter;
import com.example.ratelimiter.core.RateLimiterType;
import com.example.ratelimiter.exception.RateLimitExceededException;
import com.example.ratelimiter.manager.RateLimiterManager;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.annotation.Order;
import org.springframework.expression.EvaluationContext;
import org.springframework.expression.Expression;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;

/**
 * 限流切面
 * 
 * @author Rate Limiter Framework
 */
@Aspect
@Component
@Order(1)
public class RateLimitAspect {
    
    private static final Logger logger = LoggerFactory.getLogger(RateLimitAspect.class);
    
    @Autowired
    private RateLimiterManager rateLimiterManager;
    
    private final ExpressionParser parser = new SpelExpressionParser();
    
    @Around("@annotation(rateLimit)")
    public Object around(ProceedingJoinPoint joinPoint, RateLimit rateLimit) throws Throwable {
        String key = resolveKey(joinPoint, rateLimit);
        RateLimiter rateLimiter = rateLimiterManager.getRateLimiter(rateLimit.type());
        
        boolean acquired;
        if (rateLimit.blocking()) {
            acquired = rateLimiter.acquire(key, rateLimit.permits());
        } else {
            acquired = rateLimiter.tryAcquire(key, rateLimit.permits());
        }
        
        if (!acquired) {
            long availablePermits = rateLimiter.getAvailablePermits(key);
            long retryAfter = calculateRetryAfter(rateLimit);
            
            logger.warn("Rate limit exceeded for key: {}, available permits: {}", key, availablePermits);
            throw new RateLimitExceededException(key, availablePermits, retryAfter);
        }
        
        try {
            return joinPoint.proceed();
        } catch (Exception e) {
            logger.error("Error in rate limited method", e);
            throw e;
        }
    }
    
    /**
     * 解析限流键
     */
    private String resolveKey(ProceedingJoinPoint joinPoint, RateLimit rateLimit) {
        String keyExpression = rateLimit.key();
        
        if (keyExpression.isEmpty()) {
            // 默认使用类名+方法名作为键
            MethodSignature signature = (MethodSignature) joinPoint.getSignature();
            Method method = signature.getMethod();
            return method.getDeclaringClass().getSimpleName() + "." + method.getName();
        }
        
        try {
            // 解析SpEL表达式
            Expression expression = parser.parseExpression(keyExpression);
            EvaluationContext context = new StandardEvaluationContext();
            
            // 设置方法参数
            MethodSignature signature = (MethodSignature) joinPoint.getSignature();
            String[] paramNames = signature.getParameterNames();
            Object[] args = joinPoint.getArgs();
            
            for (int i = 0; i < paramNames.length; i++) {
                context.setVariable(paramNames[i], args[i]);
            }
            
            // 设置方法名和类名
            context.setVariable("methodName", signature.getMethod().getName());
            context.setVariable("className", signature.getMethod().getDeclaringClass().getSimpleName());
            
            Object result = expression.getValue(context);
            return result != null ? result.toString() : keyExpression;
        } catch (Exception e) {
            logger.warn("Failed to parse key expression: {}, using default", keyExpression, e);
            return keyExpression;
        }
    }
    
    /**
     * 计算重试时间
     */
    private long calculateRetryAfter(RateLimit rateLimit) {
        if (rateLimit.type() == RateLimiterType.TOKEN_BUCKET) {
            return rateLimit.refillPeriod();
        } else {
            return rateLimit.windowSize();
        }
    }
}