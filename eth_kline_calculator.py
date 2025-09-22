#!/usr/bin/env python3
"""
ETH K线计算模块
基于交易量数据演算ETH涨跌K线
"""

import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

class ETHKlineCalculator:
    def __init__(self):
        self.kline_data = []
        self.technical_indicators = {}
        
    def calculate_kline_from_volume(self, volume_data):
        """
        基于交易量数据计算K线
        考虑交易量与价格波动的相关性
        """
        kline_data = []
        
        for i, day_data in enumerate(volume_data):
            date = day_data['date']
            total_volume = day_data['total_volume']
            exchange_volumes = day_data['exchanges']
            
            # 基于交易量计算价格波动
            price_data = self.calculate_price_volatility(total_volume, exchange_volumes, i)
            
            # 计算技术指标
            technical_data = self.calculate_technical_indicators(kline_data, price_data)
            
            kline_entry = {
                'date': date,
                'timestamp': int(datetime.strptime(date, '%Y-%m-%d').timestamp() * 1000),
                'open': price_data['open'],
                'high': price_data['high'],
                'low': price_data['low'],
                'close': price_data['close'],
                'volume': total_volume,
                'volume_usd': total_volume * 1000000000,  # 转换为美元
                'change': price_data['change'],
                'change_percent': price_data['change_percent'],
                'technical': technical_data,
                'market_data': {
                    'dominance': day_data.get('dominance', 18.5),
                    'market_cap_rank': day_data.get('market_cap_rank', 2),
                    'exchanges_count': len(exchange_volumes)
                }
            }
            
            kline_data.append(kline_entry)
        
        self.kline_data = kline_data
        return kline_data
    
    def calculate_price_volatility(self, total_volume, exchange_volumes, day_index):
        """
        基于交易量计算价格波动
        """
        # 基础价格（模拟ETH价格走势）
        base_price = 3500 + (day_index / 14) * 1000  # 从3500涨到4500
        
        # 交易量对价格的影响
        volume_impact = self.calculate_volume_impact(total_volume, exchange_volumes)
        
        # 市场情绪因子
        sentiment_factor = self.calculate_market_sentiment(day_index)
        
        # 技术面因子
        technical_factor = self.calculate_technical_factor(day_index)
        
        # 计算开盘价
        open_price = base_price + volume_impact + sentiment_factor + technical_factor
        
        # 日内波动范围（基于交易量活跃度）
        daily_volatility = self.calculate_daily_volatility(total_volume, exchange_volumes)
        
        # 计算最高价和最低价
        high_price = open_price + random.uniform(0, daily_volatility)
        low_price = open_price - random.uniform(0, daily_volatility)
        
        # 收盘价（考虑趋势和随机性）
        trend_factor = 1 + (day_index - 7) * 0.01  # 趋势因子
        close_price = open_price * trend_factor + random.uniform(-daily_volatility/2, daily_volatility/2)
        
        # 确保价格逻辑正确
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        return {
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'change': round(close_price - open_price, 2),
            'change_percent': round((close_price - open_price) / open_price * 100, 2)
        }
    
    def calculate_volume_impact(self, total_volume, exchange_volumes):
        """
        计算交易量对价格的影响
        """
        # 基础交易量影响
        base_volume = 15.0  # 基准日交易量
        volume_ratio = total_volume / base_volume
        
        # 交易所集中度影响（主要交易所交易量占比）
        major_exchanges = ['binance', 'coinbase', 'kraken']
        major_volume = sum(exchange_volumes[ex]['volume'] for ex in major_exchanges if ex in exchange_volumes)
        concentration_ratio = major_volume / total_volume if total_volume > 0 else 0.5
        
        # 交易量影响 = 交易量比例 * 集中度 * 随机因子
        impact = (volume_ratio - 1) * 100 * concentration_ratio * random.uniform(0.8, 1.2)
        
        return impact
    
    def calculate_market_sentiment(self, day_index):
        """
        计算市场情绪因子
        """
        # 模拟市场情绪周期
        sentiment_cycle = math.sin(day_index * 0.3) * 50
        random_sentiment = random.uniform(-30, 30)
        
        return sentiment_cycle + random_sentiment
    
    def calculate_technical_factor(self, day_index):
        """
        计算技术面因子
        """
        # 模拟技术面信号
        if day_index < 5:
            return random.uniform(-20, 20)  # 前期震荡
        elif day_index < 10:
            return random.uniform(10, 50)   # 中期上涨
        else:
            return random.uniform(-10, 30)  # 后期调整
    
    def calculate_daily_volatility(self, total_volume, exchange_volumes):
        """
        计算日内波动范围
        """
        # 基础波动率
        base_volatility = 50
        
        # 交易量影响波动率
        volume_volatility = (total_volume / 15.0) * 30
        
        # 交易所分散度影响
        volumes = [ex['volume'] for ex in exchange_volumes.values()]
        if len(volumes) > 1:
            volume_std = statistics.stdev(volumes)
            dispersion_factor = volume_std / statistics.mean(volumes)
        else:
            dispersion_factor = 0.5
        
        # 总波动率
        total_volatility = base_volatility + volume_volatility + (dispersion_factor * 20)
        
        return max(total_volatility, 20)  # 最小波动率
    
    def calculate_technical_indicators(self, historical_data, current_price_data):
        """
        计算技术指标
        """
        if len(historical_data) < 2:
            return {
                'rsi': None,
                'macd': None,
                'bollinger_upper': None,
                'bollinger_lower': None,
                'sma_5': None,
                'sma_10': None,
                'ema_12': None,
                'ema_26': None
            }
        
        # 获取历史收盘价
        closes = [day['close'] for day in historical_data] + [current_price_data['close']]
        
        # 计算RSI
        rsi = self.calculate_rsi(closes)
        
        # 计算MACD
        macd = self.calculate_macd(closes)
        
        # 计算布林带
        bollinger = self.calculate_bollinger_bands(closes)
        
        # 计算移动平均线
        sma_5 = self.calculate_sma(closes, 5)
        sma_10 = self.calculate_sma(closes, 10)
        ema_12 = self.calculate_ema(closes, 12)
        ema_26 = self.calculate_ema(closes, 26)
        
        return {
            'rsi': round(rsi, 2) if rsi else None,
            'macd': round(macd, 2) if macd else None,
            'bollinger_upper': round(bollinger['upper'], 2) if bollinger['upper'] else None,
            'bollinger_lower': round(bollinger['lower'], 2) if bollinger['lower'] else None,
            'bollinger_middle': round(bollinger['middle'], 2) if bollinger['middle'] else None,
            'sma_5': round(sma_5, 2) if sma_5 else None,
            'sma_10': round(sma_10, 2) if sma_10 else None,
            'ema_12': round(ema_12, 2) if ema_12 else None,
            'ema_26': round(ema_26, 2) if ema_26 else None
        }
    
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
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """计算布林带"""
        if len(prices) < period:
            return {'upper': None, 'middle': None, 'lower': None}
        
        recent_prices = prices[-period:]
        sma = sum(recent_prices) / len(recent_prices)
        
        variance = sum((price - sma) ** 2 for price in recent_prices) / len(recent_prices)
        std = math.sqrt(variance)
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    def calculate_sma(self, prices, period):
        """计算简单移动平均线"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def calculate_ema(self, prices, period):
        """计算指数移动平均线"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema_value = prices[0]
        
        for price in prices[1:]:
            ema_value = (price * multiplier) + (ema_value * (1 - multiplier))
        
        return ema_value
    
    def analyze_kline_patterns(self):
        """
        分析K线形态
        """
        if len(self.kline_data) < 5:
            return {}
        
        patterns = {
            'trend': self.analyze_trend(),
            'support_resistance': self.find_support_resistance(),
            'volume_patterns': self.analyze_volume_patterns(),
            'price_action': self.analyze_price_action()
        }
        
        return patterns
    
    def analyze_trend(self):
        """分析趋势"""
        if len(self.kline_data) < 3:
            return {'direction': 'neutral', 'strength': 0}
        
        recent_closes = [day['close'] for day in self.kline_data[-5:]]
        early_closes = [day['close'] for day in self.kline_data[:5]]
        
        recent_avg = sum(recent_closes) / len(recent_closes)
        early_avg = sum(early_closes) / len(early_closes)
        
        trend_strength = (recent_avg - early_avg) / early_avg
        
        if trend_strength > 0.05:
            direction = 'uptrend'
        elif trend_strength < -0.05:
            direction = 'downtrend'
        else:
            direction = 'sideways'
        
        return {
            'direction': direction,
            'strength': abs(trend_strength),
            'change_percent': trend_strength * 100
        }
    
    def find_support_resistance(self):
        """寻找支撑位和阻力位"""
        if len(self.kline_data) < 5:
            return {'support': None, 'resistance': None}
        
        highs = [day['high'] for day in self.kline_data]
        lows = [day['low'] for day in self.kline_data]
        
        # 简化的支撑阻力位计算
        resistance = max(highs)
        support = min(lows)
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'range': round(resistance - support, 2)
        }
    
    def analyze_volume_patterns(self):
        """分析交易量模式"""
        if len(self.kline_data) < 5:
            return {}
        
        volumes = [day['volume'] for day in self.kline_data]
        avg_volume = sum(volumes) / len(volumes)
        
        recent_volume = sum(volumes[-3:]) / 3
        early_volume = sum(volumes[:3]) / 3
        
        volume_trend = (recent_volume - early_volume) / early_volume
        
        return {
            'avg_volume': round(avg_volume, 2),
            'volume_trend': round(volume_trend * 100, 2),
            'volume_volatility': round(statistics.stdev(volumes) / avg_volume * 100, 2)
        }
    
    def analyze_price_action(self):
        """分析价格行为"""
        if len(self.kline_data) < 3:
            return {}
        
        recent_days = self.kline_data[-3:]
        green_candles = sum(1 for day in recent_days if day['close'] > day['open'])
        red_candles = len(recent_days) - green_candles
        
        return {
            'green_candles': green_candles,
            'red_candles': red_candles,
            'bullish_ratio': green_candles / len(recent_days),
            'momentum': 'bullish' if green_candles > red_candles else 'bearish'
        }
    
    def generate_kline_summary(self):
        """
        生成K线分析摘要
        """
        if not self.kline_data:
            return "暂无K线数据"
        
        patterns = self.analyze_kline_patterns()
        latest = self.kline_data[-1]
        
        summary = f"""
=== ETH K线分析摘要 ===

📊 最新数据 ({latest['date']}):
- 开盘: ${latest['open']:,.2f}
- 最高: ${latest['high']:,.2f}
- 最低: ${latest['low']:,.2f}
- 收盘: ${latest['close']:,.2f}
- 涨跌: {latest['change']:+.2f} ({latest['change_percent']:+.2f}%)
- 交易量: {latest['volume']:.2f} 十亿美元

📈 技术指标:
- RSI: {latest['technical']['rsi'] or 'N/A'}
- MACD: {latest['technical']['macd'] or 'N/A'}
- 5日均线: {latest['technical']['sma_5'] or 'N/A'}
- 10日均线: {latest['technical']['sma_10'] or 'N/A'}

🎯 趋势分析:
- 趋势方向: {patterns['trend']['direction']}
- 趋势强度: {patterns['trend']['strength']:.2%}
- 支撑位: ${patterns['support_resistance']['support'] or 'N/A'}
- 阻力位: ${patterns['support_resistance']['resistance'] or 'N/A'}

📊 交易量分析:
- 平均交易量: {patterns['volume_patterns']['avg_volume']} 十亿美元
- 交易量趋势: {patterns['volume_patterns']['volume_trend']:+.2f}%
- 交易量波动率: {patterns['volume_patterns']['volume_volatility']:.2f}%

⚡ 价格行为:
- 近期多头蜡烛: {patterns['price_action']['green_candles']}
- 近期空头蜡烛: {patterns['price_action']['red_candles']}
- 多头比例: {patterns['price_action']['bullish_ratio']:.1%}
- 动量: {patterns['price_action']['momentum']}
        """
        
        return summary

if __name__ == "__main__":
    # 测试K线计算器
    calculator = ETHKlineCalculator()
    
    # 模拟交易量数据
    test_volume_data = [
        {
            'date': '2025-09-08',
            'total_volume': 15.2,
            'exchanges': {
                'binance': {'volume': 5.3},
                'coinbase': {'volume': 3.8},
                'kraken': {'volume': 2.1}
            }
        }
    ]
    
    kline_data = calculator.calculate_kline_from_volume(test_volume_data)
    print("K线数据生成完成")
    print(calculator.generate_kline_summary())
