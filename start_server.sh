#!/bin/bash

echo "🚀 ETH数据分析仪表板启动脚本"
echo "=================================="

# 检查数据文件是否存在
if [ ! -f "/workspace/eth_data.json" ]; then
    echo "📊 正在生成ETH数据..."
    python3 eth_data_simple.py
fi

echo "🌐 启动Web服务器..."
echo "📡 服务器地址: http://localhost:8000"
echo "🔗 在浏览器中打开上述地址查看仪表板"
echo "按 Ctrl+C 停止服务器"
echo ""

python3 app_simple.py