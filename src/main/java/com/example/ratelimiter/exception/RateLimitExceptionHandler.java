package com.example.ratelimiter.exception;

import com.example.ratelimiter.model.RateLimitResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 限流异常处理器
 * 
 * @author Rate Limiter Framework
 */
@RestControllerAdvice
public class RateLimitExceptionHandler {
    
    private static final Logger logger = LoggerFactory.getLogger(RateLimitExceptionHandler.class);
    
    @ExceptionHandler(RateLimitExceededException.class)
    public ResponseEntity<RateLimitResponse> handleRateLimitExceeded(RateLimitExceededException ex) {
        logger.warn("Rate limit exceeded: {}", ex.getMessage());
        
        RateLimitResponse response = RateLimitResponse.builder()
                .success(false)
                .message("Rate limit exceeded")
                .key(ex.getKey())
                .availablePermits(ex.getAvailablePermits())
                .retryAfter(ex.getRetryAfter())
                .build();
        
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .header("Retry-After", String.valueOf(ex.getRetryAfter() / 1000))
                .body(response);
    }
    
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<RateLimitResponse> handleIllegalArgument(IllegalArgumentException ex) {
        logger.error("Invalid argument: {}", ex.getMessage());
        
        RateLimitResponse response = RateLimitResponse.builder()
                .success(false)
                .message("Invalid argument: " + ex.getMessage())
                .build();
        
        return ResponseEntity.badRequest().body(response);
    }
}