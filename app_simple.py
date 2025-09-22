#!/usr/bin/env python3
"""
简化的ETH数据分析Web应用
使用内置库和简单的HTTP服务器
"""

import json
import http.server
import socketserver
import urllib.parse
import os
from datetime import datetime

class ETHDataHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/index.html':
            self.serve_index()
        elif path == '/api/data':
            self.serve_api_data()
        elif path == '/api/historical':
            self.serve_api_historical()
        elif path == '/api/prediction':
            self.serve_api_prediction()
        elif path == '/api/exchanges':
            self.serve_api_exchanges()
        else:
            super().do_GET()
    
    def serve_index(self):
        """提供主页面"""
        try:
            with open('/workspace/templates/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "页面未找到")
    
    def serve_api_data(self):
        """提供所有数据API"""
        try:
            with open('/workspace/eth_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "数据文件未找到")
    
    def serve_api_historical(self):
        """提供历史数据API"""
        try:
            with open('/workspace/eth_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            historical_data = data.get('historical_kline', [])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(historical_data, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "历史数据未找到")
    
    def serve_api_prediction(self):
        """提供预测数据API"""
        try:
            with open('/workspace/eth_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            prediction_data = data.get('future_kline', [])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(prediction_data, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "预测数据未找到")
    
    def serve_api_exchanges(self):
        """提供交易所数据API"""
        try:
            with open('/workspace/eth_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            exchange_data = data.get('exchange_volumes', [])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(exchange_data, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "交易所数据未找到")

def main():
    """启动服务器"""
    PORT = 8000
    
    # 确保数据文件存在
    if not os.path.exists('/workspace/eth_data.json'):
        print("数据文件不存在，请先运行 python3 eth_data_simple.py")
        return
    
    print(f"🚀 ETH数据分析服务器启动中...")
    print(f"📡 服务器地址: http://localhost:{PORT}")
    print(f"🌐 在浏览器中打开: http://localhost:{PORT}")
    print("按 Ctrl+C 停止服务器")
    
    with socketserver.TCPServer(("", PORT), ETHDataHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == "__main__":
    main()