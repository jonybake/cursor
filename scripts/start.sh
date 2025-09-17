#!/bin/bash

echo "启动RocketMQ消息去重示例..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker"
    exit 1
fi

# 启动依赖服务
echo "启动Redis和RocketMQ服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 启动应用
echo "启动Spring Boot应用..."
mvn spring-boot:run

echo "应用启动完成！"
echo "访问 http://localhost:8080 查看API文档"
echo "使用以下命令测试去重功能："
echo "curl -X POST 'http://localhost:8080/api/message/batch-test?count=5'"