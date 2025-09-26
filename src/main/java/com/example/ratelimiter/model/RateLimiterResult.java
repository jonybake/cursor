package com.example.ratelimiter.model;

/**
 * 限流结果
 * 
 * @author Rate Limiter Framework
 */
public class RateLimiterResult {

    /**
     * 是否允许通过
     */
    private final boolean allowed;

    /**
     * 剩余许可数
     */
    private final long remainingPermits;

    /**
     * 重置时间（毫秒）
     */
    private final long resetTime;

    /**
     * 错误信息
     */
    private final String message;

    public RateLimiterResult(boolean allowed, long remainingPermits, long resetTime, String message) {
        this.allowed = allowed;
        this.remainingPermits = remainingPermits;
        this.resetTime = resetTime;
        this.message = message;
    }

    public static RateLimiterResult success(long remainingPermits, long resetTime) {
        return new RateLimiterResult(true, remainingPermits, resetTime, null);
    }

    public static RateLimiterResult failure(long remainingPermits, long resetTime, String message) {
        return new RateLimiterResult(false, remainingPermits, resetTime, message);
    }

    public boolean isAllowed() {
        return allowed;
    }

    public long getRemainingPermits() {
        return remainingPermits;
    }

    public long getResetTime() {
        return resetTime;
    }

    public String getMessage() {
        return message;
    }

    @Override
    public String toString() {
        return "RateLimiterResult{" +
                "allowed=" + allowed +
                ", remainingPermits=" + remainingPermits +
                ", resetTime=" + resetTime +
                ", message='" + message + '\'' +
                '}';
    }
}