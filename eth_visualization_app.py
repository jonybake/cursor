#!/usr/bin/env python3
"""
ETH交易量分析和K线可视化Web应用
提供现代化的Web界面展示ETH数据
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
from eth_exchange_data import ETHExchangeDataCollector
from eth_kline_calculator import ETHKlineCalculator

app = Flask(__name__)

class ETHVisualizationApp:
    def __init__(self):
        self.exchange_collector = ETHExchangeDataCollector()
        self.kline_calculator = ETHKlineCalculator()
        self.current_data = None
        self.kline_data = None
        
    def load_or_generate_data(self):
        """加载或生成数据"""
        try:
            # 尝试加载现有数据
            if os.path.exists('eth_exchange_analysis.json'):
                with open('eth_exchange_analysis.json', 'r', encoding='utf-8') as f:
                    self.current_data = json.load(f)
                print("✅ 已加载现有数据")
            else:
                # 生成新数据
                print("🔄 生成新的分析数据...")
                self.current_data = self.exchange_collector.run_analysis()
            
            # 生成K线数据
            if self.current_data and 'volume_data' in self.current_data:
                self.kline_data = self.kline_calculator.calculate_kline_from_volume(
                    self.current_data['volume_data']
                )
                print("✅ K线数据生成完成")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            # 生成默认数据
            self.current_data = self.exchange_collector.run_analysis()
            self.kline_data = self.kline_calculator.calculate_kline_from_volume(
                self.current_data['volume_data']
            )

# 创建应用实例
eth_app = ETHVisualizationApp()
eth_app.load_or_generate_data()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """获取所有数据"""
    return jsonify({
        'exchange_data': eth_app.current_data,
        'kline_data': eth_app.kline_data,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/volume')
def get_volume_data():
    """获取交易量数据"""
    if not eth_app.current_data:
        return jsonify({'error': 'No data available'})
    
    return jsonify({
        'volume_data': eth_app.current_data.get('volume_data', []),
        'trend_analysis': eth_app.current_data.get('trend_analysis', {}),
        'exchange_rankings': eth_app.current_data.get('trend_analysis', {}).get('exchange_rankings', [])
    })

@app.route('/api/kline')
def get_kline_data():
    """获取K线数据"""
    if not eth_app.kline_data:
        return jsonify({'error': 'No K-line data available'})
    
    return jsonify({
        'kline_data': eth_app.kline_data,
        'patterns': eth_app.kline_calculator.analyze_kline_patterns()
    })

@app.route('/api/technical')
def get_technical_indicators():
    """获取技术指标数据"""
    if not eth_app.kline_data:
        return jsonify({'error': 'No data available'})
    
    technical_data = []
    for day in eth_app.kline_data:
        technical_data.append({
            'date': day['date'],
            'close': day['close'],
            'volume': day['volume'],
            'rsi': day['technical']['rsi'],
            'macd': day['technical']['macd'],
            'sma_5': day['technical']['sma_5'],
            'sma_10': day['technical']['sma_10'],
            'bollinger_upper': day['technical']['bollinger_upper'],
            'bollinger_lower': day['technical']['bollinger_lower']
        })
    
    return jsonify(technical_data)

@app.route('/api/exchanges')
def get_exchange_data():
    """获取交易所数据"""
    if not eth_app.current_data:
        return jsonify({'error': 'No data available'})
    
    exchange_data = []
    for day in eth_app.current_data.get('volume_data', []):
        day_exchanges = []
        for exchange_id, exchange_info in day['exchanges'].items():
            day_exchanges.append({
                'id': exchange_id,
                'name': exchange_info['name'],
                'volume': exchange_info['volume'],
                'percentage': exchange_info['percentage']
            })
        
        exchange_data.append({
            'date': day['date'],
            'total_volume': day['total_volume'],
            'exchanges': day_exchanges
        })
    
    return jsonify(exchange_data)

@app.route('/api/refresh')
def refresh_data():
    """刷新数据"""
    try:
        print("🔄 正在刷新数据...")
        eth_app.current_data = eth_app.exchange_collector.run_analysis()
        eth_app.kline_data = eth_app.kline_calculator.calculate_kline_from_volume(
            eth_app.current_data['volume_data']
        )
        print("✅ 数据刷新完成")
        return jsonify({'status': 'success', 'message': '数据已刷新'})
    except Exception as e:
        print(f"❌ 数据刷新失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/summary')
def get_summary():
    """获取分析摘要"""
    if not eth_app.current_data or not eth_app.kline_data:
        return jsonify({'error': 'No data available'})
    
    # 计算摘要数据
    latest_kline = eth_app.kline_data[-1]
    patterns = eth_app.kline_calculator.analyze_kline_patterns()
    trend_analysis = eth_app.current_data.get('trend_analysis', {})
    
    summary = {
        'latest_price': {
            'close': latest_kline['close'],
            'change': latest_kline['change'],
            'change_percent': latest_kline['change_percent'],
            'volume': latest_kline['volume']
        },
        'trend': {
            'direction': patterns.get('trend', {}).get('direction', 'neutral'),
            'strength': patterns.get('trend', {}).get('strength', 0),
            'support': patterns.get('support_resistance', {}).get('support'),
            'resistance': patterns.get('support_resistance', {}).get('resistance')
        },
        'volume_analysis': {
            'avg_daily_volume': trend_analysis.get('avg_daily_volume', 0),
            'volume_trend': trend_analysis.get('volume_trend_percent', 0),
            'price_trend': trend_analysis.get('price_trend_percent', 0)
        },
        'technical_indicators': {
            'rsi': latest_kline['technical']['rsi'],
            'macd': latest_kline['technical']['macd'],
            'sma_5': latest_kline['technical']['sma_5'],
            'sma_10': latest_kline['technical']['sma_10']
        },
        'market_data': {
            'analysis_period': trend_analysis.get('analysis_period', ''),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    return jsonify(summary)

if __name__ == '__main__':
    print("🚀 启动ETH可视化分析应用...")
    print("📊 访问地址: http://localhost:5000")
    print("🔄 按 Ctrl+C 停止服务")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
