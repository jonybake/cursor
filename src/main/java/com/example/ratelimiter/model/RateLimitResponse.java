package com.example.ratelimiter.model;

import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * 限流响应模型
 * 
 * @author Rate Limiter Framework
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class RateLimitResponse {
    
    private boolean success;
    private String message;
    private String key;
    private Long availablePermits;
    private Long retryAfter;
    private Long timestamp;
    
    public RateLimitResponse() {
        this.timestamp = System.currentTimeMillis();
    }
    
    public static Builder builder() {
        return new Builder();
    }
    
    // Getters and Setters
    public boolean isSuccess() {
        return success;
    }
    
    public void setSuccess(boolean success) {
        this.success = success;
    }
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public String getKey() {
        return key;
    }
    
    public void setKey(String key) {
        this.key = key;
    }
    
    public Long getAvailablePermits() {
        return availablePermits;
    }
    
    public void setAvailablePermits(Long availablePermits) {
        this.availablePermits = availablePermits;
    }
    
    public Long getRetryAfter() {
        return retryAfter;
    }
    
    public void setRetryAfter(Long retryAfter) {
        this.retryAfter = retryAfter;
    }
    
    public Long getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }
    
    public static class Builder {
        private final RateLimitResponse response = new RateLimitResponse();
        
        public Builder success(boolean success) {
            response.success = success;
            return this;
        }
        
        public Builder message(String message) {
            response.message = message;
            return this;
        }
        
        public Builder key(String key) {
            response.key = key;
            return this;
        }
        
        public Builder availablePermits(Long availablePermits) {
            response.availablePermits = availablePermits;
            return this;
        }
        
        public Builder retryAfter(Long retryAfter) {
            response.retryAfter = retryAfter;
            return this;
        }
        
        public RateLimitResponse build() {
            return response;
        }
    }
}