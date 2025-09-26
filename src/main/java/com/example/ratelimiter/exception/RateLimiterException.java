package com.example.ratelimiter.exception;

/**
 * 限流异常
 * 
 * @author Rate Limiter Framework
 */
public class RateLimiterException extends RuntimeException {

    private final long remainingPermits;
    private final long resetTime;

    public RateLimiterException(String message, long remainingPermits, long resetTime) {
        super(message);
        this.remainingPermits = remainingPermits;
        this.resetTime = resetTime;
    }

    public RateLimiterException(String message, Throwable cause, long remainingPermits, long resetTime) {
        super(message, cause);
        this.remainingPermits = remainingPermits;
        this.resetTime = resetTime;
    }

    public long getRemainingPermits() {
        return remainingPermits;
    }

    public long getResetTime() {
        return resetTime;
    }
}