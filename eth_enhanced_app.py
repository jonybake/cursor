#!/usr/bin/env python3
"""
ETH增强版分析Web应用
集成最准确的交易量数据、最合理的K线和未来5天预测
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
from eth_enhanced_data import ETHEnhancedDataCollector
from eth_future_kline_predictor import ETHFutureKlinePredictor

app = Flask(__name__)

class ETHEnhancedApp:
    def __init__(self):
        self.enhanced_collector = ETHEnhancedDataCollector()
        self.future_predictor = ETHFutureKlinePredictor()
        self.current_data = None
        self.forecast_data = None
        
    def load_or_generate_enhanced_data(self):
        """加载或生成增强版数据"""
        try:
            # 尝试加载现有数据
            if os.path.exists('eth_enhanced_analysis.json'):
                with open('eth_enhanced_analysis.json', 'r', encoding='utf-8') as f:
                    self.current_data = json.load(f)
                print("✅ 已加载增强版数据")
            else:
                # 生成新数据
                print("🔄 生成最准确的ETH数据...")
                self.current_data = self.enhanced_collector.run_enhanced_analysis()
            
            # 生成未来5天预测
            if self.current_data and 'volume_data' in self.current_data:
                # 准备历史数据用于预测
                historical_data = []
                for day in self.current_data['volume_data']:
                    historical_data.append({
                        'date': day['date'],
                        'total_volume': day['total_volume'],
                        'price': day['price']
                    })
                
                self.forecast_data = self.future_predictor.predict_future_5days_kline(historical_data)
                print("✅ 未来5天K线预测完成")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            # 生成默认数据
            self.current_data = self.enhanced_collector.run_enhanced_analysis()
            historical_data = []
            for day in self.current_data['volume_data']:
                historical_data.append({
                    'date': day['date'],
                    'total_volume': day['total_volume'],
                    'price': day['price']
                })
            self.forecast_data = self.future_predictor.predict_future_5days_kline(historical_data)

# 创建应用实例
eth_enhanced = ETHEnhancedApp()
eth_enhanced.load_or_generate_enhanced_data()

@app.route('/')
def index():
    """主页面"""
    return render_template('enhanced_index.html')

@app.route('/api/enhanced_data')
def get_enhanced_data():
    """获取增强版数据"""
    return jsonify({
        'enhanced_data': eth_enhanced.current_data,
        'forecast_data': eth_enhanced.forecast_data,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/volume_analysis')
def get_volume_analysis():
    """获取交易量分析"""
    if not eth_enhanced.current_data:
        return jsonify({'error': 'No data available'})
    
    return jsonify({
        'volume_data': eth_enhanced.current_data.get('volume_data', []),
        'trend_analysis': eth_enhanced.current_data.get('trend_analysis', {}),
        'exchange_rankings': eth_enhanced.current_data.get('trend_analysis', {}).get('exchange_rankings', [])
    })

@app.route('/api/forecast_analysis')
def get_forecast_analysis():
    """获取预测分析"""
    if not eth_enhanced.forecast_data:
        return jsonify({'error': 'No forecast data available'})
    
    return jsonify({
        'forecast_data': eth_enhanced.forecast_data,
        'summary': eth_enhanced.future_predictor.generate_prediction_summary()
    })

@app.route('/api/technical_indicators')
def get_technical_indicators():
    """获取技术指标"""
    if not eth_enhanced.forecast_data:
        return jsonify({'error': 'No data available'})
    
    technical_data = []
    
    # 历史数据技术指标
    for day in eth_enhanced.current_data.get('volume_data', []):
        technical_data.append({
            'date': day['date'],
            'type': 'historical',
            'close': day['price']['close'],
            'volume': day['total_volume'],
            'rsi': None,  # 简化处理
            'macd': None,
            'sma_5': None,
            'sma_10': None,
            'bollinger_upper': None,
            'bollinger_lower': None
        })
    
    # 预测数据技术指标
    for day in eth_enhanced.forecast_data:
        technical_data.append({
            'date': day['date'],
            'type': 'forecast',
            'close': day['close'],
            'volume': day['volume'],
            'rsi': day['technical']['rsi'],
            'macd': day['technical']['macd'],
            'sma_5': day['technical']['moving_averages']['sma_5'],
            'sma_10': day['technical']['moving_averages']['sma_10'],
            'bollinger_upper': day['technical']['bollinger_bands']['upper'],
            'bollinger_lower': day['technical']['bollinger_bands']['lower'],
            'confidence': day['confidence']
        })
    
    return jsonify(technical_data)

@app.route('/api/exchanges')
def get_exchange_data():
    """获取交易所数据"""
    if not eth_enhanced.current_data:
        return jsonify({'error': 'No data available'})
    
    exchange_data = []
    for day in eth_enhanced.current_data.get('volume_data', []):
        day_exchanges = []
        for exchange_id, exchange_info in day['exchanges'].items():
            day_exchanges.append({
                'id': exchange_id,
                'name': exchange_info['name'],
                'volume': exchange_info['volume'],
                'percentage': exchange_info['percentage'],
                'volatility': exchange_info.get('volatility', 0),
                'liquidity_score': exchange_info.get('liquidity_score', 0)
            })
        
        exchange_data.append({
            'date': day['date'],
            'total_volume': day['total_volume'],
            'exchanges': day_exchanges,
            'market_factors': day.get('market_factors', {}),
            'market_depth': day.get('market_depth', {}),
            'liquidity_metrics': day.get('liquidity_metrics', {})
        })
    
    return jsonify(exchange_data)

@app.route('/api/refresh_enhanced')
def refresh_enhanced_data():
    """刷新增强版数据"""
    try:
        print("🔄 正在刷新最准确的ETH数据...")
        eth_enhanced.current_data = eth_enhanced.enhanced_collector.run_enhanced_analysis()
        
        # 重新生成预测
        historical_data = []
        for day in eth_enhanced.current_data['volume_data']:
            historical_data.append({
                'date': day['date'],
                'total_volume': day['total_volume'],
                'price': day['price']
            })
        
        eth_enhanced.forecast_data = eth_enhanced.future_predictor.predict_future_5days_kline(historical_data)
        
        print("✅ 增强版数据刷新完成")
        return jsonify({'status': 'success', 'message': '最准确数据已刷新'})
    except Exception as e:
        print(f"❌ 数据刷新失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/summary_enhanced')
def get_enhanced_summary():
    """获取增强版分析摘要"""
    if not eth_enhanced.current_data or not eth_enhanced.forecast_data:
        return jsonify({'error': 'No data available'})
    
    # 计算摘要数据
    latest_historical = eth_enhanced.current_data['volume_data'][-1]
    latest_forecast = eth_enhanced.forecast_data[0]
    trend_analysis = eth_enhanced.current_data.get('trend_analysis', {})
    
    # 计算预测统计
    forecast_prices = [day['close'] for day in eth_enhanced.forecast_data]
    forecast_volumes = [day['volume'] for day in eth_enhanced.forecast_data]
    forecast_confidences = [day['confidence'] for day in eth_enhanced.forecast_data]
    
    summary = {
        'current_price': {
            'close': latest_historical['price']['close'],
            'change': latest_historical['price']['change'],
            'change_percent': latest_historical['price']['change_percent'],
            'volume': latest_historical['total_volume']
        },
        'forecast_price': {
            'close': latest_forecast['close'],
            'change': latest_forecast['change'],
            'change_percent': latest_forecast['change_percent'],
            'volume': latest_forecast['volume']
        },
        'forecast_summary': {
            'total_change': (forecast_prices[-1] - forecast_prices[0]) / forecast_prices[0] * 100,
            'avg_confidence': statistics.mean(forecast_confidences),
            'price_range': {
                'min': min(forecast_prices),
                'max': max(forecast_prices)
            },
            'avg_volume': statistics.mean(forecast_volumes)
        },
        'trend_analysis': {
            'avg_daily_volume': trend_analysis.get('avg_daily_volume', 0),
            'volume_trend': trend_analysis.get('volume_trend_percent', 0),
            'price_trend': trend_analysis.get('price_trend_percent', 0),
            'price_volatility': trend_analysis.get('price_volatility', 0)
        },
        'market_characteristics': trend_analysis.get('market_characteristics', {}),
        'exchange_rankings': trend_analysis.get('exchange_rankings', []),
        'market_data': {
            'analysis_period': trend_analysis.get('analysis_period', ''),
            'forecast_period': f"{eth_enhanced.forecast_data[0]['date']} 至 {eth_enhanced.forecast_data[-1]['date']}",
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_accuracy': 'enhanced'
        }
    }
    
    return jsonify(summary)

if __name__ == '__main__':
    print("🚀 启动ETH增强版分析Web应用...")
    print("📊 访问地址: http://localhost:5000")
    print("🔄 按 Ctrl+C 停止服务")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
