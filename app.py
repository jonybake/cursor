#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETH交易量和凯利指数分析Web应用
Ethereum Trading Volume and Kelly Index Analysis Web Application
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import requests
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

class ETHAnalyzer:
    def __init__(self):
        self.exchanges = {
            'Binance': {'color': '#F0B90B', 'api_url': 'https://api.binance.com/api/v3/klines'},
            'Coinbase': {'color': '#0052FF', 'api_url': 'https://api.exchange.coinbase.com/products/ETH-USD/candles'},
            'Kraken': {'color': '#4C4C4C', 'api_url': 'https://api.kraken.com/0/public/OHLC'},
            'OKX': {'color': '#000000', 'api_url': 'https://www.okx.com/api/v5/market/history-candles'}
        }
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    def generate_mock_data(self, days=15):
        """生成模拟数据"""
        all_data = []
        
        for exchange, config in self.exchanges.items():
            # 基础价格和交易量
            base_prices = {'Binance': 4170, 'Coinbase': 4175, 'Kraken': 4168, 'OKX': 4172}
            base_volumes = {'Binance': 500000, 'Coinbase': 200000, 'Kraken': 150000, 'OKX': 300000}
            
            dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
            
            # 生成价格数据
            base_price = base_prices[exchange]
            trend = np.linspace(0, 0.05, days)
            noise = np.random.normal(0, 0.02, days)
            prices = base_price * (1 + trend + noise)
            
            # 生成交易量数据
            base_volume = base_volumes[exchange]
            volume_noise = np.random.uniform(0.5, 2.0, days)
            volumes = base_volume * volume_noise
            
            df = pd.DataFrame({
                'timestamp': dates,
                'close': prices,
                'volume': volumes,
                'exchange': exchange
            })
            
            all_data.append(df)
        
        return pd.concat(all_data, ignore_index=True)
    
    def calculate_kelly_index(self, df):
        """计算凯利指数"""
        df['price_change'] = df.groupby('exchange')['close'].pct_change()
        df['is_up'] = df['price_change'] > 0
        
        exchange_stats = {}
        
        for exchange in df['exchange'].unique():
            exchange_data = df[df['exchange'] == exchange].dropna()
            
            if len(exchange_data) < 2:
                continue
                
            total_days = len(exchange_data)
            up_days = exchange_data['is_up'].sum()
            down_days = total_days - up_days
            
            p_win = up_days / total_days
            p_loss = down_days / total_days
            
            up_returns = exchange_data[exchange_data['is_up']]['price_change'].mean()
            down_returns = exchange_data[~exchange_data['is_up']]['price_change'].mean()
            
            if abs(down_returns) > 0:
                b = abs(up_returns / down_returns)
            else:
                b = 1.0
            
            kelly_fraction = (b * p_win - p_loss) / b
            risk_adjusted_kelly = max(0, min(kelly_fraction, 0.25))
            
            exchange_stats[exchange] = {
                'total_days': total_days,
                'up_days': up_days,
                'down_days': down_days,
                'p_win': p_win,
                'p_loss': p_loss,
                'avg_up_return': up_returns,
                'avg_down_return': down_returns,
                'odds_ratio': b,
                'kelly_fraction': kelly_fraction,
                'risk_adjusted_kelly': risk_adjusted_kelly,
                'avg_volume': exchange_data['volume'].mean(),
                'volume_std': exchange_data['volume'].std(),
                'color': self.exchanges[exchange]['color']
            }
        
        return exchange_stats

# 全局分析器实例
analyzer = ETHAnalyzer()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/exchange-data')
def get_exchange_data():
    """获取交易所数据API"""
    try:
        # 生成模拟数据
        exchange_data = analyzer.generate_mock_data(15)
        
        # 转换为JSON格式
        data = []
        for _, row in exchange_data.iterrows():
            data.append({
                'timestamp': row['timestamp'].strftime('%Y-%m-%d'),
                'close': round(row['close'], 2),
                'volume': round(row['volume'], 0),
                'exchange': row['exchange']
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'exchanges': list(exchange_data['exchange'].unique())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/kelly-index')
def get_kelly_index():
    """获取凯利指数数据API"""
    try:
        # 生成数据并计算凯利指数
        exchange_data = analyzer.generate_mock_data(15)
        kelly_stats = analyzer.calculate_kelly_index(exchange_data)
        
        # 转换为JSON格式
        data = []
        for exchange, stats in kelly_stats.items():
            data.append({
                'exchange': exchange,
                'kelly_index': round(stats['risk_adjusted_kelly'], 3),
                'win_probability': round(stats['p_win'], 3),
                'loss_probability': round(stats['p_loss'], 3),
                'odds_ratio': round(stats['odds_ratio'], 3),
                'avg_volume': round(stats['avg_volume'], 0),
                'color': stats['color'],
                'recommendation': get_recommendation(stats['risk_adjusted_kelly'])
            })
        
        # 按凯利指数排序
        data.sort(key=lambda x: x['kelly_index'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/volume-stats')
def get_volume_stats():
    """获取交易量统计API"""
    try:
        exchange_data = analyzer.generate_mock_data(15)
        
        stats = []
        for exchange in exchange_data['exchange'].unique():
            exchange_data_subset = exchange_data[exchange_data['exchange'] == exchange]
            
            stats.append({
                'exchange': exchange,
                'avg_volume': round(exchange_data_subset['volume'].mean(), 0),
                'max_volume': round(exchange_data_subset['volume'].max(), 0),
                'min_volume': round(exchange_data_subset['volume'].min(), 0),
                'total_volume': round(exchange_data_subset['volume'].sum(), 0),
                'color': analyzer.exchanges[exchange]['color']
            })
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/price-trend')
def get_price_trend():
    """获取价格趋势数据API"""
    try:
        exchange_data = analyzer.generate_mock_data(15)
        
        # 按交易所分组
        trend_data = {}
        for exchange in exchange_data['exchange'].unique():
            exchange_data_subset = exchange_data[exchange_data['exchange'] == exchange]
            trend_data[exchange] = {
                'timestamps': [d.strftime('%Y-%m-%d') for d in exchange_data_subset['timestamp']],
                'prices': [round(p, 2) for p in exchange_data_subset['close']],
                'volumes': [round(v, 0) for v in exchange_data_subset['volume']],
                'color': analyzer.exchanges[exchange]['color']
            }
        
        return jsonify({
            'success': True,
            'data': trend_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_recommendation(kelly_index):
    """根据凯利指数获取投资建议"""
    if kelly_index > 0.15:
        return "强烈建议投资"
    elif kelly_index > 0.10:
        return "建议投资"
    elif kelly_index > 0.05:
        return "谨慎投资"
    elif kelly_index > 0:
        return "少量投资"
    else:
        return "不建议投资"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)