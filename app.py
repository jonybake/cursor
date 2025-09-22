#!/usr/bin/env python3
"""
ETH数据分析Web应用
展示ETH交易量数据和K线预测
"""

from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

def load_data():
    """加载ETH数据"""
    try:
        with open('/workspace/eth_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    """API端点：返回所有数据"""
    data = load_data()
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': '数据未找到'}), 404

@app.route('/api/historical')
def api_historical():
    """API端点：返回历史K线数据"""
    data = load_data()
    if data and 'historical_kline' in data:
        return jsonify(data['historical_kline'])
    else:
        return jsonify({'error': '历史数据未找到'}), 404

@app.route('/api/prediction')
def api_prediction():
    """API端点：返回预测K线数据"""
    data = load_data()
    if data and 'future_kline' in data:
        return jsonify(data['future_kline'])
    else:
        return jsonify({'error': '预测数据未找到'}), 404

@app.route('/api/exchanges')
def api_exchanges():
    """API端点：返回交易所数据"""
    data = load_data()
    if data and 'exchange_volumes' in data:
        return jsonify(data['exchange_volumes'])
    else:
        return jsonify({'error': '交易所数据未找到'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)