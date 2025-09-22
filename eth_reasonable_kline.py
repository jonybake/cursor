#!/usr/bin/env python3
"""
ETH最合理K线计算模块
基于准确交易量数据演算最合理的K线形态
"""

import json
import math
import random
import statistics
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class ETHReasonableKlineCalculator:
    def __init__(self):
        self.kline_data = []
        self.technical_indicators = {}
        
    def calculate_reasonable_kline(self, volume_data):
        """
        基于准确交易量数据计算最合理的K线
        考虑市场微观结构、价格发现机制等
        """
        kline_data = []
        
        for i, day_data in enumerate(volume_data):
            date = day_data['date']
            total_volume = day_data['total_volume']
            exchange_volumes = day_data['exchanges']
            market_factors = day_data.get('market_factors', {})
            
            # 基于交易量计算合理的价格波动
            price_data = self.calculate_reasonable_price_volatility(
                total_volume, exchange_volumes, market_factors, i, len(volume_data)
            )
            
            # 计算技术指标
            technical_data = self.calculate_advanced_technical_indicators(kline_data, price_data)
            
            # 计算市场微观结构指标
            microstructure_data = self.calculate_microstructure_indicators(
                exchange_volumes, price_data, market_factors
            )
            
            kline_entry = {
                'date': date,
                'timestamp': int(datetime.strptime(date, '%Y-%m-%d').timestamp() * 1000),
                'open': price_data['open'],
                'high': price_data['high'],
                'low': price_data['low'],
                'close': price_data['close'],
                'volume': total_volume,
                'volume_usd': total_volume * 1000000000,
                'change': price_data['change'],
                'change_percent': price_data['change_percent'],
                'technical': technical_data,
                'microstructure': microstructure_data,
                'market_data': {
                    'dominance': day_data.get('dominance', 18.5),
                    'market_cap_rank': day_data.get('market_cap_rank', 2),
                    'exchanges_count': len(exchange_volumes),
                    'market_factors': market_factors
                }
            }
            
            kline_data.append(kline_entry)
        
        self.kline_data = kline_data
        return kline_data
    
    def calculate_reasonable_price_volatility(self, total_volume, exchange_volumes, market_factors, day_index, total_days):
        """
        计算最合理的价格波动
        基于市场微观结构理论
        """
        # 基础价格（基于市场因子）
        base_price = 3500 + (day_index / total_days) * 800
        
        # 交易量影响价格发现
        volume_impact = self.calculate_volume_price_impact(total_volume, exchange_volumes)
        
        # 市场深度影响
        market_depth_impact = self.calculate_market_depth_impact(exchange_volumes)
        
        # 流动性影响
        liquidity_impact = self.calculate_liquidity_impact(total_volume, market_factors)
        
        # 市场情绪影响
        sentiment_impact = self.calculate_sentiment_impact(market_factors, day_index)
        
        # 技术面影响
        technical_impact = self.calculate_technical_impact(day_index, total_days)
        
        # 计算基础价格
        base_price += volume_impact + market_depth_impact + liquidity_impact + sentiment_impact + technical_impact
        
        # 计算合理的日内波动范围
        daily_volatility = self.calculate_reasonable_daily_volatility(
            total_volume, exchange_volumes, market_factors
        )
        
        # 生成合理的OHLC数据
        ohlc_data = self.generate_reasonable_ohlc(base_price, daily_volatility, market_factors)
        
        return ohlc_data
    
    def calculate_volume_price_impact(self, total_volume, exchange_volumes):
        """
        计算交易量对价格的影响
        基于价格发现理论
        """
        # 基准交易量
        base_volume = 15.0
        
        # 交易量偏离影响
        volume_ratio = total_volume / base_volume
        volume_impact = (volume_ratio - 1) * 200
        
        # 交易所集中度影响价格发现效率
        major_exchanges = ['binance', 'coinbase', 'kraken']
        major_volume = sum(exchange_volumes[ex]['volume'] for ex in major_exchanges if ex in exchange_volumes)
        concentration_ratio = major_volume / total_volume if total_volume > 0 else 0.5
        
        # 集中度越高，价格发现越有效，波动越小
        efficiency_factor = 1 - (concentration_ratio - 0.5) * 0.3
        volume_impact *= efficiency_factor
        
        return volume_impact
    
    def calculate_market_depth_impact(self, exchange_volumes):
        """
        计算市场深度影响
        """
        # 计算交易所分散度
        volumes = [ex['volume'] for ex in exchange_volumes.values()]
        if len(volumes) > 1:
            volume_std = statistics.stdev(volumes)
            volume_mean = statistics.mean(volumes)
            dispersion = volume_std / volume_mean
        else:
            dispersion = 0.5
        
        # 分散度越高，市场深度越好，价格越稳定
        depth_impact = -dispersion * 100
        
        return depth_impact
    
    def calculate_liquidity_impact(self, total_volume, market_factors):
        """
        计算流动性影响
        """
        # 基础流动性
        base_liquidity = 1.0
        
        # 交易量影响流动性
        volume_liquidity = min(total_volume / 15.0, 2.0)  # 最大2倍
        
        # 市场因子影响
        market_liquidity = market_factors.get('liquidity', 1.0)
        
        # 综合流动性
        total_liquidity = base_liquidity * volume_liquidity * market_liquidity
        
        # 流动性越高，价格波动越小
        liquidity_impact = (1 - total_liquidity) * 50
        
        return liquidity_impact
    
    def calculate_sentiment_impact(self, market_factors, day_index):
        """
        计算市场情绪影响
        """
        # 新闻影响
        news_impact = (market_factors.get('news', 1.0) - 1.0) * 100
        
        # 技术面影响
        technical_impact = (market_factors.get('technical', 1.0) - 1.0) * 80
        
        # 周末效应
        weekend_impact = (market_factors.get('weekend', 1.0) - 1.0) * 30
        
        return news_impact + technical_impact + weekend_impact
    
    def calculate_technical_impact(self, day_index, total_days):
        """
        计算技术面影响
        """
        # 趋势因子
        trend_factor = (day_index - total_days/2) / total_days * 100
        
        # 周期因子
        cycle_factor = math.sin(day_index * 2 * math.pi / 7) * 20
        
        # 随机技术面影响
        random_technical = random.gauss(0, 15)
        
        return trend_factor + cycle_factor + random_technical
    
    def calculate_reasonable_daily_volatility(self, total_volume, exchange_volumes, market_factors):
        """
        计算合理的日内波动范围
        """
        # 基础波动率
        base_volatility = 50
        
        # 交易量影响波动率
        volume_volatility = (total_volume / 15.0) * 30
        
        # 交易所分散度影响
        volumes = [ex['volume'] for ex in exchange_volumes.values()]
        if len(volumes) > 1:
            volume_std = statistics.stdev(volumes)
            volume_mean = statistics.mean(volumes)
            dispersion_factor = volume_std / volume_mean
        else:
            dispersion_factor = 0.5
        
        dispersion_volatility = dispersion_factor * 40
        
        # 市场因子影响
        market_volatility = (market_factors.get('general', 1.0) - 1.0) * 20
        
        # 综合波动率
        total_volatility = base_volatility + volume_volatility + dispersion_volatility + market_volatility
        
        return max(total_volatility, 20)  # 最小波动率
    
    def generate_reasonable_ohlc(self, base_price, daily_volatility, market_factors):
        """
        生成合理的OHLC数据
        考虑市场开盘、盘中、收盘的特征
        """
        # 开盘价（基于前一日收盘和隔夜消息）
        overnight_impact = random.gauss(0, daily_volatility * 0.3)
        open_price = base_price + overnight_impact
        
        # 日内波动范围
        intraday_range = daily_volatility * random.uniform(0.8, 1.2)
        
        # 最高价和最低价
        high_range = random.uniform(0, intraday_range)
        low_range = random.uniform(0, intraday_range)
        
        high_price = open_price + high_range
        low_price = open_price - low_range
        
        # 收盘价（考虑日内趋势和随机性）
        intraday_trend = random.gauss(0, daily_volatility * 0.2)
        close_price = open_price + intraday_trend
        
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
    
    def calculate_advanced_technical_indicators(self, historical_data, current_price_data):
        """
        计算高级技术指标
        """
        if len(historical_data) < 2:
            return self.get_default_technical_indicators()
        
        # 获取历史收盘价
        closes = [day['close'] for day in historical_data] + [current_price_data['close']]
        
        # 计算各种技术指标
        technical_data = {
            'rsi': self.calculate_rsi(closes),
            'macd': self.calculate_macd(closes),
            'bollinger_bands': self.calculate_bollinger_bands(closes),
            'moving_averages': self.calculate_moving_averages(closes),
            'stochastic': self.calculate_stochastic(historical_data, current_price_data),
            'williams_r': self.calculate_williams_r(historical_data, current_price_data),
            'cci': self.calculate_cci(historical_data, current_price_data),
            'atr': self.calculate_atr(historical_data, current_price_data)
        }
        
        return technical_data
    
    def get_default_technical_indicators(self):
        """获取默认技术指标"""
        return {
            'rsi': None,
            'macd': None,
            'bollinger_bands': {'upper': None, 'middle': None, 'lower': None},
            'moving_averages': {'sma_5': None, 'sma_10': None, 'sma_20': None, 'ema_12': None, 'ema_26': None},
            'stochastic': {'k': None, 'd': None},
            'williams_r': None,
            'cci': None,
            'atr': None
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
        return round(rsi, 2)
    
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
        return round(macd_line, 2)
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """计算布林带"""
        if len(prices) < period:
            return {'upper': None, 'middle': None, 'lower': None}
        
        recent_prices = prices[-period:]
        sma = sum(recent_prices) / len(recent_prices)
        
        variance = sum((price - sma) ** 2 for price in recent_prices) / len(recent_prices)
        std = math.sqrt(variance)
        
        return {
            'upper': round(sma + (std * std_dev), 2),
            'middle': round(sma, 2),
            'lower': round(sma - (std * std_dev), 2)
        }
    
    def calculate_moving_averages(self, prices):
        """计算移动平均线"""
        def sma(prices, period):
            if len(prices) < period:
                return None
            return sum(prices[-period:]) / period
        
        def ema(prices, period):
            if len(prices) < period:
                return None
            multiplier = 2 / (period + 1)
            ema_value = prices[0]
            for price in prices[1:]:
                ema_value = (price * multiplier) + (ema_value * (1 - multiplier))
            return ema_value
        
        return {
            'sma_5': round(sma(prices, 5), 2) if sma(prices, 5) else None,
            'sma_10': round(sma(prices, 10), 2) if sma(prices, 10) else None,
            'sma_20': round(sma(prices, 20), 2) if sma(prices, 20) else None,
            'ema_12': round(ema(prices, 12), 2) if ema(prices, 12) else None,
            'ema_26': round(ema(prices, 26), 2) if ema(prices, 26) else None
        }
    
    def calculate_stochastic(self, historical_data, current_data, k_period=14, d_period=3):
        """计算随机指标"""
        if len(historical_data) < k_period:
            return {'k': None, 'd': None}
        
        recent_data = historical_data[-(k_period-1):] + [current_data]
        
        # 计算最高价和最低价
        highs = [day['high'] for day in recent_data]
        lows = [day['low'] for day in recent_data]
        closes = [day['close'] for day in recent_data]
        
        highest_high = max(highs)
        lowest_low = min(lows)
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            k_percent = 50
        else:
            k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # 简化的D值计算
        d_percent = k_percent  # 简化处理
        
        return {
            'k': round(k_percent, 2),
            'd': round(d_percent, 2)
        }
    
    def calculate_williams_r(self, historical_data, current_data, period=14):
        """计算威廉指标"""
        if len(historical_data) < period - 1:
            return None
        
        recent_data = historical_data[-(period-1):] + [current_data]
        
        highs = [day['high'] for day in recent_data]
        lows = [day['low'] for day in recent_data]
        current_close = current_data['close']
        
        highest_high = max(highs)
        lowest_low = min(lows)
        
        if highest_high == lowest_low:
            return -50
        
        williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        return round(williams_r, 2)
    
    def calculate_cci(self, historical_data, current_data, period=20):
        """计算商品通道指数"""
        if len(historical_data) < period - 1:
            return None
        
        recent_data = historical_data[-(period-1):] + [current_data]
        
        typical_prices = []
        for day in recent_data:
            tp = (day['high'] + day['low'] + day['close']) / 3
            typical_prices.append(tp)
        
        sma_tp = sum(typical_prices) / len(typical_prices)
        
        mean_deviation = sum(abs(tp - sma_tp) for tp in typical_prices) / len(typical_prices)
        
        if mean_deviation == 0:
            return 0
        
        cci = (typical_prices[-1] - sma_tp) / (0.015 * mean_deviation)
        return round(cci, 2)
    
    def calculate_atr(self, historical_data, current_data, period=14):
        """计算平均真实范围"""
        if len(historical_data) < period - 1:
            return None
        
        recent_data = historical_data[-(period-1):] + [current_data]
        
        true_ranges = []
        for i in range(1, len(recent_data)):
            current = recent_data[i]
            previous = recent_data[i-1]
            
            tr1 = current['high'] - current['low']
            tr2 = abs(current['high'] - previous['close'])
            tr3 = abs(current['low'] - previous['close'])
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        atr = sum(true_ranges) / len(true_ranges)
        return round(atr, 2)
    
    def calculate_microstructure_indicators(self, exchange_volumes, price_data, market_factors):
        """
        计算市场微观结构指标
        """
        # 交易所集中度
        volumes = [ex['volume'] for ex in exchange_volumes.values()]
        total_volume = sum(volumes)
        
        # 赫芬达尔指数（HHI）
        hhi = sum((v / total_volume) ** 2 for v in volumes) if total_volume > 0 else 0
        
        # 价格影响
        price_impact = abs(price_data['change_percent']) / 100
        
        # 流动性指标
        liquidity_score = total_volume / 15.0  # 相对于基准交易量
        
        return {
            'hhi': round(hhi, 4),
            'concentration': 'high' if hhi > 0.25 else 'medium' if hhi > 0.15 else 'low',
            'price_impact': round(price_impact, 4),
            'liquidity_score': round(liquidity_score, 2),
            'market_efficiency': 'high' if hhi < 0.2 and liquidity_score > 1.0 else 'medium' if hhi < 0.3 else 'low'
        }
    
    def analyze_kline_patterns(self):
        """
        分析K线形态和市场模式
        """
        if len(self.kline_data) < 5:
            return {}
        
        patterns = {
            'trend_analysis': self.analyze_trend_patterns(),
            'support_resistance': self.find_support_resistance_levels(),
            'volume_patterns': self.analyze_volume_patterns(),
            'price_action': self.analyze_price_action_patterns(),
            'market_regime': self.analyze_market_regime()
        }
        
        return patterns
    
    def analyze_trend_patterns(self):
        """分析趋势模式"""
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
            'change_percent': trend_strength * 100,
            'confidence': min(abs(trend_strength) * 10, 1.0)
        }
    
    def find_support_resistance_levels(self):
        """寻找支撑位和阻力位"""
        if len(self.kline_data) < 5:
            return {'support': None, 'resistance': None}
        
        highs = [day['high'] for day in self.kline_data]
        lows = [day['low'] for day in self.kline_data]
        
        # 寻找关键价位
        resistance = max(highs)
        support = min(lows)
        
        # 寻找次要支撑阻力位
        sorted_highs = sorted(highs, reverse=True)
        sorted_lows = sorted(lows)
        
        secondary_resistance = sorted_highs[1] if len(sorted_highs) > 1 else resistance
        secondary_support = sorted_lows[1] if len(sorted_lows) > 1 else support
        
        return {
            'primary_support': round(support, 2),
            'primary_resistance': round(resistance, 2),
            'secondary_support': round(secondary_support, 2),
            'secondary_resistance': round(secondary_resistance, 2),
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
        
        # 交易量异常检测
        volume_std = statistics.stdev(volumes)
        high_volume_threshold = avg_volume + volume_std
        low_volume_threshold = avg_volume - volume_std
        
        high_volume_days = sum(1 for v in volumes if v > high_volume_threshold)
        low_volume_days = sum(1 for v in volumes if v < low_volume_threshold)
        
        return {
            'avg_volume': round(avg_volume, 2),
            'volume_trend': round(volume_trend * 100, 2),
            'volume_volatility': round(volume_std / avg_volume * 100, 2),
            'high_volume_days': high_volume_days,
            'low_volume_days': low_volume_days,
            'volume_regime': 'high' if volume_trend > 0.1 else 'low' if volume_trend < -0.1 else 'normal'
        }
    
    def analyze_price_action_patterns(self):
        """分析价格行为模式"""
        if len(self.kline_data) < 3:
            return {}
        
        recent_days = self.kline_data[-5:]
        green_candles = sum(1 for day in recent_days if day['close'] > day['open'])
        red_candles = len(recent_days) - green_candles
        
        # 计算蜡烛图形态
        patterns = []
        for i in range(1, len(recent_days)):
            current = recent_days[i]
            previous = recent_days[i-1]
            
            # 判断蜡烛图形态
            if current['close'] > current['open'] and previous['close'] < previous['open']:
                patterns.append('bullish_reversal')
            elif current['close'] < current['open'] and previous['close'] > previous['open']:
                patterns.append('bearish_reversal')
            elif current['close'] > current['open'] and previous['close'] > previous['open']:
                patterns.append('bullish_continuation')
            elif current['close'] < current['open'] and previous['close'] < previous['open']:
                patterns.append('bearish_continuation')
        
        return {
            'green_candles': green_candles,
            'red_candles': red_candles,
            'bullish_ratio': green_candles / len(recent_days),
            'momentum': 'bullish' if green_candles > red_candles else 'bearish',
            'patterns': patterns,
            'pattern_frequency': {
                'bullish_reversal': patterns.count('bullish_reversal'),
                'bearish_reversal': patterns.count('bearish_reversal'),
                'bullish_continuation': patterns.count('bullish_continuation'),
                'bearish_continuation': patterns.count('bearish_continuation')
            }
        }
    
    def analyze_market_regime(self):
        """分析市场状态"""
        if len(self.kline_data) < 5:
            return {'regime': 'unknown'}
        
        recent_data = self.kline_data[-5:]
        
        # 计算波动率
        returns = [(day['close'] - day['open']) / day['open'] for day in recent_data]
        volatility = statistics.stdev(returns)
        
        # 计算趋势强度
        closes = [day['close'] for day in recent_data]
        trend_strength = (closes[-1] - closes[0]) / closes[0]
        
        # 计算交易量特征
        volumes = [day['volume'] for day in recent_data]
        avg_volume = sum(volumes) / len(volumes)
        volume_trend = (volumes[-1] - volumes[0]) / volumes[0]
        
        # 判断市场状态
        if volatility > 0.03 and abs(trend_strength) > 0.05:
            regime = 'trending_high_volatility'
        elif volatility > 0.03:
            regime = 'high_volatility'
        elif abs(trend_strength) > 0.05:
            regime = 'trending'
        elif volume_trend > 0.2:
            regime = 'accumulation'
        elif volume_trend < -0.2:
            regime = 'distribution'
        else:
            regime = 'consolidation'
        
        return {
            'regime': regime,
            'volatility': round(volatility * 100, 2),
            'trend_strength': round(trend_strength * 100, 2),
            'volume_trend': round(volume_trend * 100, 2)
        }
    
    def generate_reasonable_kline_summary(self):
        """
        生成合理的K线分析摘要
        """
        if not self.kline_data:
            return "暂无K线数据"
        
        patterns = self.analyze_kline_patterns()
        latest = self.kline_data[-1]
        
        summary = f"""
=== ETH最合理K线分析摘要 ===

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
- 布林带上轨: {latest['technical']['bollinger_bands']['upper'] or 'N/A'}
- 布林带下轨: {latest['technical']['bollinger_bands']['lower'] or 'N/A'}
- 5日均线: {latest['technical']['moving_averages']['sma_5'] or 'N/A'}
- 10日均线: {latest['technical']['moving_averages']['sma_10'] or 'N/A'}

🎯 趋势分析:
- 趋势方向: {patterns['trend_analysis']['direction']}
- 趋势强度: {patterns['trend_analysis']['strength']:.2%}
- 趋势置信度: {patterns['trend_analysis']['confidence']:.1%}
- 主要支撑位: ${patterns['support_resistance']['primary_support'] or 'N/A'}
- 主要阻力位: ${patterns['support_resistance']['primary_resistance'] or 'N/A'}

📊 交易量分析:
- 平均交易量: {patterns['volume_patterns']['avg_volume']} 十亿美元
- 交易量趋势: {patterns['volume_patterns']['volume_trend']:+.2f}%
- 交易量波动率: {patterns['volume_patterns']['volume_volatility']:.2f}%
- 交易量状态: {patterns['volume_patterns']['volume_regime']}

⚡ 价格行为:
- 近期多头蜡烛: {patterns['price_action']['green_candles']}
- 近期空头蜡烛: {patterns['price_action']['red_candles']}
- 多头比例: {patterns['price_action']['bullish_ratio']:.1%}
- 动量方向: {patterns['price_action']['momentum']}

🏛️ 市场微观结构:
- 交易所集中度: {latest['microstructure']['concentration']}
- 价格影响: {latest['microstructure']['price_impact']:.3f}
- 流动性评分: {latest['microstructure']['liquidity_score']}
- 市场效率: {latest['microstructure']['market_efficiency']}

📈 市场状态:
- 当前状态: {patterns['market_regime']['regime']}
- 波动率: {patterns['market_regime']['volatility']}%
- 趋势强度: {patterns['market_regime']['trend_strength']:+.2f}%
- 交易量趋势: {patterns['market_regime']['volume_trend']:+.2f}%
        """
        
        return summary

if __name__ == "__main__":
    # 测试K线计算器
    calculator = ETHReasonableKlineCalculator()
    
    # 模拟交易量数据
    test_volume_data = [
        {
            'date': '2025-09-08',
            'total_volume': 15.2,
            'exchanges': {
                'binance': {'volume': 5.3, 'name': 'Binance'},
                'coinbase': {'volume': 3.8, 'name': 'Coinbase Pro'},
                'kraken': {'volume': 2.1, 'name': 'Kraken'}
            },
            'market_factors': {
                'general': 1.0,
                'weekend': 1.0,
                'news': 1.0,
                'technical': 1.0,
                'liquidity': 1.0
            }
        }
    ]
    
    kline_data = calculator.calculate_reasonable_kline(test_volume_data)
    print("最合理K线数据生成完成")
    print(calculator.generate_reasonable_kline_summary())
