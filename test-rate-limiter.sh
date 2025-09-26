#!/bin/bash

echo "🚀 启动Spring Boot限流框架测试..."
echo "=================================="

# 启动应用
echo "正在启动应用..."
mvn spring-boot:run &
APP_PID=$!

# 等待应用启动
echo "等待应用启动..."
sleep 15

# 测试令牌桶限流
echo ""
echo "🧪 测试令牌桶限流 (容量: 10, 补充速率: 2/秒)"
echo "----------------------------------------"
for i in {1..15}; do
    response=$(curl -s "http://localhost:8080/api/rate-limit/token-bucket?userId=123")
    echo "请求 $i: $response"
    sleep 0.5
done

echo ""
echo "🧪 测试滑动窗口限流 (容量: 5, 窗口: 10秒)"
echo "----------------------------------------"
for i in {1..8}; do
    response=$(curl -s "http://localhost:8080/api/rate-limit/sliding-window?ip=192.168.1.1")
    echo "请求 $i: $response"
    sleep 1
done

echo ""
echo "🧪 测试固定窗口限流 (容量: 3, 窗口: 5秒)"
echo "----------------------------------------"
for i in {1..6}; do
    response=$(curl -s "http://localhost:8080/api/rate-limit/fixed-window?apiKey=abc123")
    echo "请求 $i: $response"
    sleep 1
done

echo ""
echo "🧪 测试多许可消费 (容量: 20, 每次消费: 3)"
echo "----------------------------------------"
for i in {1..8}; do
    response=$(curl -s "http://localhost:8080/api/rate-limit/multi-permit?resourceId=res123")
    echo "请求 $i: $response"
    sleep 0.5
done

echo ""
echo "✅ 测试完成！"
echo "应用仍在运行，可以手动访问 http://localhost:8080/api/rate-limit/health 进行健康检查"

# 可选：停止应用
# echo "停止应用..."
# kill $APP_PID