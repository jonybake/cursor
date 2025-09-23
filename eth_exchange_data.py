#!/usr/bin/env python3
"""
ETH各大交易所交易量数据获取模块
模拟获取Binance、Coinbase、Kraken等主要交易所的ETH交易量数据
"""

import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import requests
import time

class ETHExchangeDataCollector:
    def __init__(self):
        self.exchanges = {
            'binance': {'name': 'Binance', 'weight': 0.35},
            'coinbase': {'name': 'Coinbase Pro', 'weight': 0.25},
            'kraken': {'name': 'Kraken', 'weight': 0.15},
            'huobi': {'name': 'Huobi', 'weight': 0.10},
            'okx': {'name': 'OKX', 'weight': 0.10},
            'kucoin': {'name': 'KuCoin', 'weight': 0.05}
        }
        self.total_daily_volume = 15.0  # 总日交易量约150亿美元
        
    def generate_realistic_volume_data(self, days=15):
        """
        生成基于真实市场特征的ETH交易量数据
        考虑周末效应、市场波动、交易所权重等因素
        """
        volume_data = []
        base_date = datetime.now() - timedelta(days=days-1)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 周末效应（交易量通常较低）
            weekend_factor = 0.7 if current_date.weekday() >= 5 else 1.0
            
            # 市场波动因子（模拟真实市场波动）
            volatility_factor = random.uniform(0.8, 1.3)
            
            # 趋势因子（模拟市场趋势变化）
            trend_factor = 1 + math.sin(i * 0.2) * 0.2 + random.uniform(-0.1, 0.1)
            
            # 计算总交易量
            total_volume = self.total_daily_volume * weekend_factor * volatility_factor * trend_factor
            
            # 按交易所权重分配交易量
            exchange_volumes = {}
            for exchange_id, exchange_info in self.exchanges.items():
                # 添加随机波动
                exchange_volatility = random.uniform(0.9, 1.1)
                exchange_volume = total_volume * exchange_info['weight'] * exchange_volatility
                
                exchange_volumes[exchange_id] = {
                    'name': exchange_info['name'],
                    'volume': round(exchange_volume, 2),
                    'percentage': round(exchange_volume / total_volume * 100, 2)
                }
            
            # 计算价格数据（基于交易量影响）
            price_data = self.calculate_price_from_volume(total_volume, i, days)
            
            volume_data.append({
                'date': date_str,
                'total_volume': round(total_volume, 2),
                'exchanges': exchange_volumes,
                'price': price_data,
                'market_cap_rank': 2,  # ETH排名
                'dominance': round(random.uniform(18.5, 19.5), 2)  # 市场主导地位
            })
        
        return volume_data
    
    def calculate_price_from_volume(self, volume, day_index, total_days):
        """
        基于交易量计算ETH价格
        考虑交易量与价格的相关性
        """
        # 基础价格（模拟ETH价格范围）
        base_price = 3500 + (day_index / total_days) * 1000  # 从3500涨到4500
        
        # 交易量对价格的影响
        volume_impact = (volume - self.total_daily_volume) / self.total_daily_volume * 200
        
        # 随机波动
        random_volatility = random.uniform(-100, 100)
        
        # 日内价格波动
        daily_volatility = random.uniform(50, 150)
        
        # 计算OHLC价格
        open_price = base_price + volume_impact + random_volatility
        high_price = open_price + random.uniform(0, daily_volatility)
        low_price = open_price - random.uniform(0, daily_volatility)
        close_price = open_price + random.uniform(-daily_volatility/2, daily_volatility/2)
        
        return {
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'change': round(close_price - open_price, 2),
            'change_percent': round((close_price - open_price) / open_price * 100, 2)
        }
    
    def analyze_volume_trends(self, volume_data):
        """
        分析交易量趋势
        """
        total_volumes = [day['total_volume'] for day in volume_data]
        prices = [day['price']['close'] for day in volume_data]
        
        # 计算趋势指标
        avg_volume = sum(total_volumes) / len(total_volumes)
        volume_volatility = math.sqrt(sum((v - avg_volume) ** 2 for v in total_volumes) / len(total_volumes))
        
        # 价格趋势
        price_trend = (prices[-1] - prices[0]) / prices[0] * 100
        
        # 交易量趋势
        recent_volume = sum(total_volumes[-5:]) / 5
        early_volume = sum(total_volumes[:5]) / 5
        volume_trend = (recent_volume - early_volume) / early_volume * 100
        
        # 交易所排名变化
        exchange_rankings = self.calculate_exchange_rankings(volume_data)
        
        return {
            'avg_daily_volume': round(avg_volume, 2),
            'volume_volatility': round(volume_volatility, 2),
            'price_trend_percent': round(price_trend, 2),
            'volume_trend_percent': round(volume_trend, 2),
            'exchange_rankings': exchange_rankings,
            'analysis_period': f"{volume_data[0]['date']} 至 {volume_data[-1]['date']}"
        }
    
    def calculate_exchange_rankings(self, volume_data):
        """
        计算各交易所排名
        """
        exchange_totals = {}
        
        for exchange_id in self.exchanges.keys():
            total_volume = sum(day['exchanges'][exchange_id]['volume'] for day in volume_data)
            exchange_totals[exchange_id] = {
                'name': self.exchanges[exchange_id]['name'],
                'total_volume': round(total_volume, 2),
                'avg_daily_volume': round(total_volume / len(volume_data), 2)
            }
        
        # 按总交易量排序
        sorted_exchanges = sorted(exchange_totals.items(), 
                                key=lambda x: x[1]['total_volume'], 
                                reverse=True)
        
        rankings = []
        for i, (exchange_id, data) in enumerate(sorted_exchanges):
            rankings.append({
                'rank': i + 1,
                'exchange': exchange_id,
                'name': data['name'],
                'total_volume': data['total_volume'],
                'avg_daily_volume': data['avg_daily_volume'],
                'market_share': round(data['total_volume'] / sum(ex['total_volume'] for ex in exchange_totals.values()) * 100, 2)
            })
        
        return rankings
    
    def generate_kline_data(self, volume_data):
        """
        基于交易量数据生成K线数据
        """
        kline_data = []
        
        for day_data in volume_data:
            price = day_data['price']
            volume = day_data['total_volume']
            
            # 计算技术指标
            rsi = self.calculate_rsi([d['price']['close'] for d in volume_data[:volume_data.index(day_data)+1]])
            macd = self.calculate_macd([d['price']['close'] for d in volume_data[:volume_data.index(day_data)+1]])
            
            kline_data.append({
                'date': day_data['date'],
                'open': price['open'],
                'high': price['high'],
                'low': price['low'],
                'close': price['close'],
                'volume': volume,
                'change': price['change'],
                'change_percent': price['change_percent'],
                'rsi': round(rsi, 2) if rsi else None,
                'macd': round(macd, 2) if macd else None
            })
        
        return kline_data
    
    def calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return None
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        if len(prices) < slow:
            return None
        
        def ema(prices, period):
            if len(prices) < period:
                return None
            multiplier = 2 / (period + 1)
            ema_value = prices[0]
            for price in prices[1:]:
                ema_value = (price * multiplier) + (ema_value * (1 - multiplier))
            return ema_value
        
        fast_ema = ema(prices, fast)
        slow_ema = ema(prices, slow)
        
        if fast_ema is None or slow_ema is None:
            return None
        
        macd_line = fast_ema - slow_ema
        return macd_line
    
    def run_analysis(self):
        """
        运行完整的分析
        """
        print("🚀 开始获取ETH各大交易所交易量数据...")
        
        # 生成交易量数据
        volume_data = self.generate_realistic_volume_data(15)
        print("✅ 交易量数据生成完成")
        
        # 分析趋势
        trends = self.analyze_volume_trends(volume_data)
        print("✅ 趋势分析完成")
        
        # 生成K线数据
        kline_data = self.generate_kline_data(volume_data)
        print("✅ K线数据生成完成")
        
        # 保存数据
        complete_data = {
            'volume_data': volume_data,
            'kline_data': kline_data,
            'trend_analysis': trends,
            'generated_at': datetime.now().isoformat(),
            'analysis_period': f"{volume_data[0]['date']} 至 {volume_data[-1]['date']}"
        }
        
        with open('eth_exchange_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        print("✅ 数据已保存为 eth_exchange_analysis.json")
        
        return complete_data

if __name__ == "__main__":
    collector = ETHExchangeDataCollector()
    data = collector.run_analysis()
    
    print("\n📊 分析结果摘要:")
    print(f"分析周期: {data['analysis_period']}")
    print(f"平均日交易量: {data['trend_analysis']['avg_daily_volume']} 十亿美元")
    print(f"价格趋势: {data['trend_analysis']['price_trend_percent']:+.2f}%")
    print(f"交易量趋势: {data['trend_analysis']['volume_trend_percent']:+.2f}%")
    
    print("\n🏆 交易所排名:")
    for ranking in data['trend_analysis']['exchange_rankings']:
        print(f"{ranking['rank']}. {ranking['name']}: {ranking['total_volume']} 十亿美元 ({ranking['market_share']}%)")
