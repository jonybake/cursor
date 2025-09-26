package com.example.ratelimiter.aspect;

import com.example.ratelimiter.annotation.RateLimiter;
import com.example.ratelimiter.exception.RateLimiterException;
import com.example.ratelimiter.model.RateLimiterResult;
import com.example.ratelimiter.service.RateLimiterService;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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
public class RateLimiterAspect {

    private static final Logger logger = LoggerFactory.getLogger(RateLimiterAspect.class);

    private final RateLimiterService rateLimiterService;
    private final ExpressionParser expressionParser = new SpelExpressionParser();

    public RateLimiterAspect(RateLimiterService rateLimiterService) {
        this.rateLimiterService = rateLimiterService;
    }

    @Around("@annotation(rateLimiter)")
    public Object around(ProceedingJoinPoint joinPoint, RateLimiter rateLimiter) throws Throwable {
        try {
            // 生成限流key
            String key = generateKey(joinPoint, rateLimiter);
            
            // 执行限流检查
            RateLimiterResult result = rateLimiterService.checkRateLimit(key, rateLimiter);
            
            if (!result.isAllowed()) {
                logger.warn("Rate limit exceeded for key: {}, remaining: {}", key, result.getRemainingPermits());
                throw new RateLimiterException(result.getMessage(), result.getRemainingPermits(), result.getResetTime());
            }
            
            logger.debug("Rate limit check passed for key: {}, remaining: {}", key, result.getRemainingPermits());
            
            // 执行目标方法
            return joinPoint.proceed();
            
        } catch (RateLimiterException e) {
            throw e;
        } catch (Exception e) {
            logger.error("Error in rate limiter aspect", e);
            throw e;
        }
    }

    @Around("@within(rateLimiter)")
    public Object aroundClass(ProceedingJoinPoint joinPoint, RateLimiter rateLimiter) throws Throwable {
        return around(joinPoint, rateLimiter);
    }

    /**
     * 生成限流key
     */
    private String generateKey(ProceedingJoinPoint joinPoint, RateLimiter rateLimiter) {
        String key = rateLimiter.key();
        
        if (key.isEmpty()) {
            // 默认key：类名.方法名
            MethodSignature signature = (MethodSignature) joinPoint.getSignature();
            String className = signature.getDeclaringType().getSimpleName();
            String methodName = signature.getMethod().getName();
            return className + "." + methodName;
        }
        
        // 解析SpEL表达式
        if (key.startsWith("#")) {
            return parseSpelExpression(key, joinPoint);
        }
        
        return key;
    }

    /**
     * 解析SpEL表达式
     */
    private String parseSpelExpression(String expression, ProceedingJoinPoint joinPoint) {
        try {
            Expression exp = expressionParser.parseExpression(expression);
            EvaluationContext context = new StandardEvaluationContext();
            
            // 设置方法参数
            MethodSignature signature = (MethodSignature) joinPoint.getSignature();
            Method method = signature.getMethod();
            String[] paramNames = signature.getParameterNames();
            Object[] args = joinPoint.getArgs();
            
            for (int i = 0; i < paramNames.length; i++) {
                context.setVariable(paramNames[i], args[i]);
            }
            
            // 设置方法名
            context.setVariable("methodName", method.getName());
            context.setVariable("className", method.getDeclaringClass().getSimpleName());
            
            Object value = exp.getValue(context);
            return value != null ? value.toString() : expression;
            
        } catch (Exception e) {
            logger.warn("Failed to parse SpEL expression: {}", expression, e);
            return expression;
        }
    }
}