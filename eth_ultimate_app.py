#!/usr/bin/env python3
"""
ETH终极分析Web应用
集成最准确的交易量数据和最合理的K线分析
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
from eth_accurate_data import ETHAccurateDataCollector
from eth_reasonable_kline import ETHReasonableKlineCalculator

app = Flask(__name__)

class ETHUltimateApp:
    def __init__(self):
        self.accurate_collector = ETHAccurateDataCollector()
        self.kline_calculator = ETHReasonableKlineCalculator()
        self.current_data = None
        self.kline_data = None
        
    def load_or_generate_ultimate_data(self):
        """加载或生成终极数据"""
        try:
            # 尝试加载现有数据
            if os.path.exists('eth_accurate_analysis.json'):
                with open('eth_accurate_analysis.json', 'r', encoding='utf-8') as f:
                    self.current_data = json.load(f)
                print("✅ 已加载准确数据")
            else:
                # 生成新数据
                print("🔄 生成最准确的ETH数据...")
                self.current_data = self.accurate_collector.run_accurate_analysis()
            
            # 生成最合理的K线数据
            if self.current_data and 'volume_data' in self.current_data:
                self.kline_data = self.kline_calculator.calculate_reasonable_kline(
                    self.current_data['volume_data']
                )
                print("✅ 最合理K线数据生成完成")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            # 生成默认数据
            self.current_data = self.accurate_collector.run_accurate_analysis()
            self.kline_data = self.kline_calculator.calculate_reasonable_kline(
                self.current_data['volume_data']
            )

# 创建应用实例
eth_ultimate = ETHUltimateApp()
eth_ultimate.load_or_generate_ultimate_data()

@app.route('/')
def index():
    """主页面"""
    return render_template('ultimate_index.html')

@app.route('/api/ultimate_data')
def get_ultimate_data():
    """获取终极数据"""
    return jsonify({
        'accurate_data': eth_ultimate.current_data,
        'kline_data': eth_ultimate.kline_data,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/volume_analysis')
def get_volume_analysis():
    """获取交易量分析"""
    if not eth_ultimate.current_data:
        return jsonify({'error': 'No data available'})
    
    return jsonify({
        'volume_data': eth_ultimate.current_data.get('volume_data', []),
        'trend_analysis': eth_ultimate.current_data.get('trend_analysis', {}),
        'exchange_rankings': eth_ultimate.current_data.get('trend_analysis', {}).get('exchange_rankings', [])
    })

@app.route('/api/kline_analysis')
def get_kline_analysis():
    """获取K线分析"""
    if not eth_ultimate.kline_data:
        return jsonify({'error': 'No K-line data available'})
    
    patterns = eth_ultimate.kline_calculator.analyze_kline_patterns()
    
    return jsonify({
        'kline_data': eth_ultimate.kline_data,
        'patterns': patterns,
        'summary': eth_ultimate.kline_calculator.generate_reasonable_kline_summary()
    })

@app.route('/api/technical_indicators')
def get_technical_indicators():
    """获取技术指标"""
    if not eth_ultimate.kline_data:
        return jsonify({'error': 'No data available'})
    
    technical_data = []
    for day in eth_ultimate.kline_data:
        technical_data.append({
            'date': day['date'],
            'close': day['close'],
            'volume': day['volume'],
            'rsi': day['technical']['rsi'],
            'macd': day['technical']['macd'],
            'bollinger_upper': day['technical']['bollinger_bands']['upper'],
            'bollinger_lower': day['technical']['bollinger_bands']['lower'],
            'sma_5': day['technical']['moving_averages']['sma_5'],
            'sma_10': day['technical']['moving_averages']['sma_10'],
            'sma_20': day['technical']['moving_averages']['sma_20'],
            'ema_12': day['technical']['moving_averages']['ema_12'],
            'ema_26': day['technical']['moving_averages']['ema_26'],
            'stochastic_k': day['technical']['stochastic']['k'],
            'stochastic_d': day['technical']['stochastic']['d'],
            'williams_r': day['technical']['williams_r'],
            'cci': day['technical']['cci'],
            'atr': day['technical']['atr']
        })
    
    return jsonify(technical_data)

@app.route('/api/microstructure')
def get_microstructure_data():
    """获取市场微观结构数据"""
    if not eth_ultimate.kline_data:
        return jsonify({'error': 'No data available'})
    
    microstructure_data = []
    for day in eth_ultimate.kline_data:
        microstructure_data.append({
            'date': day['date'],
            'hhi': day['microstructure']['hhi'],
            'concentration': day['microstructure']['concentration'],
            'price_impact': day['microstructure']['price_impact'],
            'liquidity_score': day['microstructure']['liquidity_score'],
            'market_efficiency': day['microstructure']['market_efficiency']
        })
    
    return jsonify(microstructure_data)

@app.route('/api/market_regime')
def get_market_regime():
    """获取市场状态分析"""
    if not eth_ultimate.kline_data:
        return jsonify({'error': 'No data available'})
    
    patterns = eth_ultimate.kline_calculator.analyze_kline_patterns()
    
    return jsonify({
        'market_regime': patterns.get('market_regime', {}),
        'trend_analysis': patterns.get('trend_analysis', {}),
        'volume_patterns': patterns.get('volume_patterns', {}),
        'price_action': patterns.get('price_action', {}),
        'support_resistance': patterns.get('support_resistance', {})
    })

@app.route('/api/exchanges')
def get_exchange_data():
    """获取交易所数据"""
    if not eth_ultimate.current_data:
        return jsonify({'error': 'No data available'})
    
    exchange_data = []
    for day in eth_ultimate.current_data.get('volume_data', []):
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
            'exchanges': day_exchanges,
            'market_factors': day.get('market_factors', {})
        })
    
    return jsonify(exchange_data)

@app.route('/api/refresh_ultimate')
def refresh_ultimate_data():
    """刷新终极数据"""
    try:
        print("🔄 正在刷新最准确的ETH数据...")
        eth_ultimate.current_data = eth_ultimate.accurate_collector.run_accurate_analysis()
        eth_ultimate.kline_data = eth_ultimate.kline_calculator.calculate_reasonable_kline(
            eth_ultimate.current_data['volume_data']
        )
        print("✅ 终极数据刷新完成")
        return jsonify({'status': 'success', 'message': '最准确数据已刷新'})
    except Exception as e:
        print(f"❌ 数据刷新失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/summary_ultimate')
def get_ultimate_summary():
    """获取终极分析摘要"""
    if not eth_ultimate.current_data or not eth_ultimate.kline_data:
        return jsonify({'error': 'No data available'})
    
    # 计算摘要数据
    latest_kline = eth_ultimate.kline_data[-1]
    patterns = eth_ultimate.kline_calculator.analyze_kline_patterns()
    trend_analysis = eth_ultimate.current_data.get('trend_analysis', {})
    
    summary = {
        'latest_price': {
            'close': latest_kline['close'],
            'change': latest_kline['change'],
            'change_percent': latest_kline['change_percent'],
            'volume': latest_kline['volume']
        },
        'trend': {
            'direction': patterns.get('trend_analysis', {}).get('direction', 'neutral'),
            'strength': patterns.get('trend_analysis', {}).get('strength', 0),
            'confidence': patterns.get('trend_analysis', {}).get('confidence', 0),
            'support': patterns.get('support_resistance', {}).get('primary_support'),
            'resistance': patterns.get('support_resistance', {}).get('primary_resistance')
        },
        'volume_analysis': {
            'avg_daily_volume': trend_analysis.get('avg_daily_volume', 0),
            'volume_trend': trend_analysis.get('volume_trend_percent', 0),
            'price_trend': trend_analysis.get('price_trend_percent', 0),
            'volume_volatility': trend_analysis.get('volume_volatility', 0)
        },
        'technical_indicators': {
            'rsi': latest_kline['technical']['rsi'],
            'macd': latest_kline['technical']['macd'],
            'sma_5': latest_kline['technical']['moving_averages']['sma_5'],
            'sma_10': latest_kline['technical']['moving_averages']['sma_10'],
            'bollinger_upper': latest_kline['technical']['bollinger_bands']['upper'],
            'bollinger_lower': latest_kline['technical']['bollinger_bands']['lower']
        },
        'microstructure': {
            'concentration': latest_kline['microstructure']['concentration'],
            'liquidity_score': latest_kline['microstructure']['liquidity_score'],
            'market_efficiency': latest_kline['microstructure']['market_efficiency'],
            'price_impact': latest_kline['microstructure']['price_impact']
        },
        'market_regime': {
            'regime': patterns.get('market_regime', {}).get('regime', 'unknown'),
            'volatility': patterns.get('market_regime', {}).get('volatility', 0),
            'trend_strength': patterns.get('market_regime', {}).get('trend_strength', 0)
        },
        'market_data': {
            'analysis_period': trend_analysis.get('analysis_period', ''),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_accuracy': 'ultimate'
        }
    }
    
    return jsonify(summary)

if __name__ == '__main__':
    print("🚀 启动ETH终极分析Web应用...")
    print("📊 访问地址: http://localhost:5000")
    print("🔄 按 Ctrl+C 停止服务")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
