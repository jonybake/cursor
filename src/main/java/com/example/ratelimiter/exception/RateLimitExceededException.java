package com.example.ratelimiter.exception;

/**
 * 限流异常
 * 
 * @author Rate Limiter Framework
 */
public class RateLimitExceededException extends RuntimeException {
    
    private final String key;
    private final long availablePermits;
    private final long retryAfter;
    
    public RateLimitExceededException(String key, long availablePermits, long retryAfter) {
        super(String.format("Rate limit exceeded for key: %s, available permits: %d, retry after: %d ms", 
                key, availablePermits, retryAfter));
        this.key = key;
        this.availablePermits = availablePermits;
        this.retryAfter = retryAfter;
    }
    
    public RateLimitExceededException(String key, long availablePermits, long retryAfter, Throwable cause) {
        super(String.format("Rate limit exceeded for key: %s, available permits: %d, retry after: %d ms", 
                key, availablePermits, retryAfter), cause);
        this.key = key;
        this.availablePermits = availablePermits;
        this.retryAfter = retryAfter;
    }
    
    public String getKey() {
        return key;
    }
    
    public long getAvailablePermits() {
        return availablePermits;
    }
    
    public long getRetryAfter() {
        return retryAfter;
    }
}