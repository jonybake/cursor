#!/usr/bin/env python3
"""
ETH未来5天K线预测模块
基于历史数据演算出未来5天最合理的K线预测
"""

import json
import math
import random
import statistics
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class ETHFutureKlinePredictor:
    def __init__(self):
        self.historical_data = []
        self.forecast_data = []
        self.prediction_models = {}
        
    def predict_future_5days_kline(self, historical_data):
        """
        基于历史数据预测未来5天最合理的K线
        使用多种预测模型和算法
        """
        self.historical_data = historical_data
        forecast_data = []
        
        # 分析历史数据模式
        historical_patterns = self.analyze_historical_patterns(historical_data)
        
        # 计算预测参数
        prediction_params = self.calculate_prediction_parameters(historical_data, historical_patterns)
        
        # 生成未来5天预测
        for day in range(5):
            forecast_date = datetime.now() + timedelta(days=day+1)
            date_str = forecast_date.strftime('%Y-%m-%d')
            
            # 使用多种模型预测
            price_prediction = self.predict_price_using_multiple_models(
                historical_data, forecast_data, day, prediction_params
            )
            
            # 预测交易量
            volume_prediction = self.predict_volume(
                historical_data, forecast_data, day, prediction_params
            )
            
            # 预测技术指标
            technical_prediction = self.predict_technical_indicators(
                historical_data, forecast_data, day
            )
            
            # 计算预测置信度
            confidence = self.calculate_prediction_confidence(
                historical_patterns, day, prediction_params
            )
            
            # 生成预测K线数据
            kline_prediction = {
                'date': date_str,
                'timestamp': int(forecast_date.timestamp() * 1000),
                'open': price_prediction['open'],
                'high': price_prediction['high'],
                'low': price_prediction['low'],
                'close': price_prediction['close'],
                'volume': volume_prediction['volume'],
                'volume_usd': volume_prediction['volume'] * 1000000000,
                'change': price_prediction['change'],
                'change_percent': price_prediction['change_percent'],
                'technical': technical_prediction,
                'confidence': confidence,
                'prediction_models': {
                    'trend_model': price_prediction['trend_model'],
                    'volume_model': volume_prediction['volume_model'],
                    'volatility_model': price_prediction['volatility_model']
                }
            }
            
            forecast_data.append(kline_prediction)
        
        self.forecast_data = forecast_data
        return forecast_data
    
    def analyze_historical_patterns(self, historical_data):
        """
        分析历史数据模式
        """
        if len(historical_data) < 5:
            return {}
        
        # 价格模式分析
        prices = [day['price']['close'] for day in historical_data]
        price_changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # 交易量模式分析
        volumes = [day['total_volume'] for day in historical_data]
        volume_changes = [(volumes[i] - volumes[i-1]) / volumes[i-1] for i in range(1, len(volumes))]
        
        # 趋势分析
        recent_trend = self.calculate_trend_strength(prices[-7:]) if len(prices) >= 7 else 0
        volume_trend = self.calculate_trend_strength(volumes[-7:]) if len(volumes) >= 7 else 0
        
        # 波动率分析
        price_volatility = statistics.stdev(price_changes) if len(price_changes) > 1 else 0
        volume_volatility = statistics.stdev(volume_changes) if len(volume_changes) > 1 else 0
        
        # 周期性分析
        price_cycle = self.detect_price_cycle(prices)
        volume_cycle = self.detect_volume_cycle(volumes)
        
        # 市场状态分析
        market_state = self.analyze_market_state(historical_data)
        
        return {
            'price_trend': recent_trend,
            'volume_trend': volume_trend,
            'price_volatility': price_volatility,
            'volume_volatility': volume_volatility,
            'price_cycle': price_cycle,
            'volume_cycle': volume_cycle,
            'market_state': market_state,
            'avg_price': statistics.mean(prices),
            'avg_volume': statistics.mean(volumes),
            'price_range': max(prices) - min(prices),
            'volume_range': max(volumes) - min(volumes)
        }
    
    def calculate_trend_strength(self, data):
        """
        计算趋势强度
        """
        if len(data) < 2:
            return 0
        
        # 线性回归斜率
        n = len(data)
        x = list(range(n))
        y = data
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # 标准化斜率
        mean_y = sum_y / n
        normalized_slope = slope / mean_y if mean_y != 0 else 0
        
        return normalized_slope
    
    def detect_price_cycle(self, prices):
        """
        检测价格周期
        """
        if len(prices) < 7:
            return {'period': 0, 'strength': 0}
        
        # 简化的周期检测
        n = len(prices)
        best_period = 0
        best_correlation = 0
        
        for period in range(3, min(n//2, 10)):
            if n >= 2 * period:
                # 计算自相关
                correlation = self.calculate_autocorrelation(prices, period)
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_period = period
        
        return {
            'period': best_period,
            'strength': best_correlation
        }
    
    def detect_volume_cycle(self, volumes):
        """
        检测交易量周期
        """
        return self.detect_price_cycle(volumes)
    
    def calculate_autocorrelation(self, data, lag):
        """
        计算自相关
        """
        n = len(data)
        if n <= lag:
            return 0
        
        mean = statistics.mean(data)
        
        # 计算协方差
        covariance = sum((data[i] - mean) * (data[i + lag] - mean) 
                        for i in range(n - lag)) / (n - lag)
        
        # 计算方差
        variance = sum((data[i] - mean) ** 2 for i in range(n)) / n
        
        if variance == 0:
            return 0
        
        return covariance / variance
    
    def analyze_market_state(self, historical_data):
        """
        分析市场状态
        """
        if len(historical_data) < 5:
            return 'unknown'
        
        recent_data = historical_data[-5:]
        
        # 计算波动率
        prices = [day['price']['close'] for day in recent_data]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0
        
        # 计算趋势强度
        trend_strength = self.calculate_trend_strength(prices)
        
        # 计算交易量特征
        volumes = [day['total_volume'] for day in recent_data]
        volume_trend = self.calculate_trend_strength(volumes)
        
        # 判断市场状态
        if volatility > 0.03 and abs(trend_strength) > 0.05:
            return 'trending_high_volatility'
        elif volatility > 0.03:
            return 'high_volatility'
        elif abs(trend_strength) > 0.05:
            return 'trending'
        elif volume_trend > 0.2:
            return 'accumulation'
        elif volume_trend < -0.2:
            return 'distribution'
        else:
            return 'consolidation'
    
    def calculate_prediction_parameters(self, historical_data, patterns):
        """
        计算预测参数
        """
        # 基础参数
        base_price = patterns['avg_price']
        base_volume = patterns['avg_volume']
        
        # 趋势参数
        trend_factor = 1 + patterns['price_trend'] * 0.5
        volume_trend_factor = 1 + patterns['volume_trend'] * 0.3
        
        # 波动率参数
        volatility_factor = patterns['price_volatility'] * 2
        volume_volatility_factor = patterns['volume_volatility'] * 1.5
        
        # 周期性参数
        cycle_factor = patterns['price_cycle']['strength']
        volume_cycle_factor = patterns['volume_cycle']['strength']
        
        # 市场状态参数
        market_state = patterns['market_state']
        state_multiplier = self.get_market_state_multiplier(market_state)
        
        return {
            'base_price': base_price,
            'base_volume': base_volume,
            'trend_factor': trend_factor,
            'volume_trend_factor': volume_trend_factor,
            'volatility_factor': volatility_factor,
            'volume_volatility_factor': volume_volatility_factor,
            'cycle_factor': cycle_factor,
            'volume_cycle_factor': volume_cycle_factor,
            'state_multiplier': state_multiplier
        }
    
    def get_market_state_multiplier(self, market_state):
        """
        获取市场状态乘数
        """
        multipliers = {
            'trending_high_volatility': 1.2,
            'high_volatility': 1.1,
            'trending': 1.0,
            'accumulation': 0.9,
            'distribution': 0.8,
            'consolidation': 0.95
        }
        return multipliers.get(market_state, 1.0)
    
    def predict_price_using_multiple_models(self, historical_data, forecast_data, day, params):
        """
        使用多种模型预测价格
        """
        # 趋势模型
        trend_price = self.predict_trend_model(historical_data, forecast_data, day, params)
        
        # 均值回归模型
        mean_reversion_price = self.predict_mean_reversion_model(historical_data, forecast_data, day, params)
        
        # 周期模型
        cycle_price = self.predict_cycle_model(historical_data, forecast_data, day, params)
        
        # 随机游走模型
        random_walk_price = self.predict_random_walk_model(historical_data, forecast_data, day, params)
        
        # 组合预测
        weights = [0.4, 0.2, 0.2, 0.2]  # 趋势模型权重最高
        models = [trend_price, mean_reversion_price, cycle_price, random_walk_price]
        
        combined_price = sum(w * m['close'] for w, m in zip(weights, models))
        
        # 计算波动率
        volatility = self.calculate_prediction_volatility(historical_data, forecast_data, day, params)
        
        # 生成OHLC数据
        ohlc_data = self.generate_prediction_ohlc(combined_price, volatility, day, params)
        
        return {
            'open': ohlc_data['open'],
            'high': ohlc_data['high'],
            'low': ohlc_data['low'],
            'close': ohlc_data['close'],
            'change': ohlc_data['change'],
            'change_percent': ohlc_data['change_percent'],
            'trend_model': trend_price,
            'volatility_model': volatility
        }
    
    def predict_trend_model(self, historical_data, forecast_data, day, params):
        """
        趋势模型预测
        """
        if not historical_data:
            return {'close': params['base_price']}
        
        # 获取最近价格
        recent_prices = [d['price']['close'] for d in historical_data[-5:]]
        if forecast_data:
            recent_prices.extend([d['close'] for d in forecast_data])
        
        # 计算趋势
        trend = self.calculate_trend_strength(recent_prices)
        
        # 预测价格
        last_price = recent_prices[-1]
        predicted_price = last_price * (1 + trend * (day + 1))
        
        return {'close': predicted_price}
    
    def predict_mean_reversion_model(self, historical_data, forecast_data, day, params):
        """
        均值回归模型预测
        """
        if not historical_data:
            return {'close': params['base_price']}
        
        # 计算长期均值
        all_prices = [d['price']['close'] for d in historical_data]
        if forecast_data:
            all_prices.extend([d['close'] for d in forecast_data])
        
        long_term_mean = statistics.mean(all_prices)
        
        # 获取当前价格
        current_price = all_prices[-1]
        
        # 均值回归速度
        reversion_speed = 0.1
        
        # 预测价格
        predicted_price = current_price + (long_term_mean - current_price) * reversion_speed
        
        return {'close': predicted_price}
    
    def predict_cycle_model(self, historical_data, forecast_data, day, params):
        """
        周期模型预测
        """
        if not historical_data:
            return {'close': params['base_price']}
        
        # 获取价格数据
        prices = [d['price']['close'] for d in historical_data]
        if forecast_data:
            prices.extend([d['close'] for d in forecast_data])
        
        # 检测周期
        cycle_info = self.detect_price_cycle(prices)
        
        if cycle_info['period'] > 0 and cycle_info['strength'] > 0.3:
            # 使用周期预测
            period = cycle_info['period']
            cycle_position = (len(prices) + day) % period
            cycle_prices = prices[-period:] if len(prices) >= period else prices
            
            if len(cycle_prices) > cycle_position:
                predicted_price = cycle_prices[cycle_position]
            else:
                predicted_price = statistics.mean(cycle_prices)
        else:
            # 无显著周期，使用趋势
            predicted_price = prices[-1] * (1 + params['trend_factor'] * 0.01)
        
        return {'close': predicted_price}
    
    def predict_random_walk_model(self, historical_data, forecast_data, day, params):
        """
        随机游走模型预测
        """
        if not historical_data:
            return {'close': params['base_price']}
        
        # 获取价格变化
        prices = [d['price']['close'] for d in historical_data]
        if forecast_data:
            prices.extend([d['close'] for d in forecast_data])
        
        if len(prices) < 2:
            return {'close': prices[-1]}
        
        # 计算价格变化
        price_changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # 计算变化均值和标准差
        mean_change = statistics.mean(price_changes)
        std_change = statistics.stdev(price_changes) if len(price_changes) > 1 else 0
        
        # 随机游走预测
        random_change = random.gauss(mean_change, std_change)
        predicted_price = prices[-1] * (1 + random_change)
        
        return {'close': predicted_price}
    
    def calculate_prediction_volatility(self, historical_data, forecast_data, day, params):
        """
        计算预测波动率
        """
        # 基础波动率
        base_volatility = params['volatility_factor'] * 50
        
        # 时间衰减
        time_decay = 1 - (day / 5) * 0.2
        
        # 市场状态影响
        state_impact = params['state_multiplier']
        
        # 随机波动
        random_volatility = random.uniform(0.8, 1.2)
        
        total_volatility = base_volatility * time_decay * state_impact * random_volatility
        
        return max(total_volatility, 20)  # 最小波动率
    
    def generate_prediction_ohlc(self, predicted_price, volatility, day, params):
        """
        生成预测OHLC数据
        """
        # 开盘价（基于前一日收盘）
        if day == 0:
            # 第一天，基于历史数据
            last_price = params['base_price']
        else:
            # 后续天数，基于前一日预测
            last_price = predicted_price
        
        # 隔夜影响
        overnight_impact = random.gauss(0, volatility * 0.3)
        open_price = last_price + overnight_impact
        
        # 日内波动
        intraday_volatility = volatility * random.uniform(0.8, 1.2)
        
        # 最高价和最低价
        high_range = random.uniform(0, intraday_volatility)
        low_range = random.uniform(0, intraday_volatility)
        
        high_price = open_price + high_range
        low_price = open_price - low_range
        
        # 收盘价
        close_impact = random.gauss(0, intraday_volatility * 0.5)
        close_price = open_price + close_impact
        
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
    
    def predict_volume(self, historical_data, forecast_data, day, params):
        """
        预测交易量
        """
        # 基础交易量
        base_volume = params['base_volume']
        
        # 趋势影响
        trend_impact = params['volume_trend_factor'] ** (day + 1)
        
        # 周期性影响
        cycle_impact = 1 + math.sin(day * 0.5) * 0.2
        
        # 市场状态影响
        state_impact = params['state_multiplier']
        
        # 随机波动
        random_impact = random.uniform(0.9, 1.1)
        
        # 预测交易量
        predicted_volume = base_volume * trend_impact * cycle_impact * state_impact * random_impact
        
        return {
            'volume': round(predicted_volume, 2),
            'volume_model': 'trend_cycle_state'
        }
    
    def predict_technical_indicators(self, historical_data, forecast_data, day):
        """
        预测技术指标
        """
        # 获取历史价格数据
        all_prices = [d['price']['close'] for d in historical_data]
        if forecast_data:
            all_prices.extend([d['close'] for d in forecast_data])
        
        if len(all_prices) < 2:
            return self.get_default_technical_indicators()
        
        # 计算技术指标
        technical_data = {
            'rsi': self.calculate_rsi(all_prices),
            'macd': self.calculate_macd(all_prices),
            'bollinger_bands': self.calculate_bollinger_bands(all_prices),
            'moving_averages': self.calculate_moving_averages(all_prices),
            'stochastic': self.calculate_stochastic(historical_data, forecast_data, day),
            'williams_r': self.calculate_williams_r(historical_data, forecast_data, day),
            'cci': self.calculate_cci(historical_data, forecast_data, day),
            'atr': self.calculate_atr(historical_data, forecast_data, day)
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
    
    def calculate_stochastic(self, historical_data, forecast_data, day, k_period=14, d_period=3):
        """计算随机指标"""
        # 获取最近数据
        recent_data = historical_data[-k_period:] if len(historical_data) >= k_period else historical_data
        if forecast_data:
            recent_data.extend(forecast_data)
        
        if len(recent_data) < 2:
            return {'k': None, 'd': None}
        
        # 计算最高价和最低价
        highs = [d['price']['high'] if 'price' in d else d['high'] for d in recent_data]
        lows = [d['price']['low'] if 'price' in d else d['low'] for d in recent_data]
        closes = [d['price']['close'] if 'price' in d else d['close'] for d in recent_data]
        
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
    
    def calculate_williams_r(self, historical_data, forecast_data, day, period=14):
        """计算威廉指标"""
        # 获取最近数据
        recent_data = historical_data[-period:] if len(historical_data) >= period else historical_data
        if forecast_data:
            recent_data.extend(forecast_data)
        
        if len(recent_data) < 2:
            return None
        
        highs = [d['price']['high'] if 'price' in d else d['high'] for d in recent_data]
        lows = [d['price']['low'] if 'price' in d else d['low'] for d in recent_data]
        current_close = recent_data[-1]['price']['close'] if 'price' in recent_data[-1] else recent_data[-1]['close']
        
        highest_high = max(highs)
        lowest_low = min(lows)
        
        if highest_high == lowest_low:
            return -50
        
        williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        return round(williams_r, 2)
    
    def calculate_cci(self, historical_data, forecast_data, day, period=20):
        """计算商品通道指数"""
        # 获取最近数据
        recent_data = historical_data[-period:] if len(historical_data) >= period else historical_data
        if forecast_data:
            recent_data.extend(forecast_data)
        
        if len(recent_data) < 2:
            return None
        
        # 计算典型价格
        typical_prices = []
        for d in recent_data:
            if 'price' in d:
                tp = (d['price']['high'] + d['price']['low'] + d['price']['close']) / 3
            else:
                tp = (d['high'] + d['low'] + d['close']) / 3
            typical_prices.append(tp)
        
        sma_tp = sum(typical_prices) / len(typical_prices)
        
        mean_deviation = sum(abs(tp - sma_tp) for tp in typical_prices) / len(typical_prices)
        
        if mean_deviation == 0:
            return 0
        
        cci = (typical_prices[-1] - sma_tp) / (0.015 * mean_deviation)
        return round(cci, 2)
    
    def calculate_atr(self, historical_data, forecast_data, day, period=14):
        """计算平均真实范围"""
        # 获取最近数据
        recent_data = historical_data[-(period+1):] if len(historical_data) >= period+1 else historical_data
        if forecast_data:
            recent_data.extend(forecast_data)
        
        if len(recent_data) < 2:
            return None
        
        true_ranges = []
        for i in range(1, len(recent_data)):
            current = recent_data[i]
            previous = recent_data[i-1]
            
            if 'price' in current:
                current_high = current['price']['high']
                current_low = current['price']['low']
                current_close = current['price']['close']
                previous_close = previous['price']['close']
            else:
                current_high = current['high']
                current_low = current['low']
                current_close = current['close']
                previous_close = previous['close']
            
            tr1 = current_high - current_low
            tr2 = abs(current_high - previous_close)
            tr3 = abs(current_low - previous_close)
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        atr = sum(true_ranges) / len(true_ranges)
        return round(atr, 2)
    
    def calculate_prediction_confidence(self, patterns, day, params):
        """
        计算预测置信度
        """
        # 基础置信度
        base_confidence = 0.8
        
        # 趋势强度影响
        trend_confidence = min(abs(patterns['price_trend']) * 2, 0.2)
        
        # 波动率影响（波动率越低，置信度越高）
        volatility_confidence = max(0.1 - patterns['price_volatility'] * 5, 0)
        
        # 周期性影响
        cycle_confidence = patterns['price_cycle']['strength'] * 0.1
        
        # 时间衰减（越远置信度越低）
        time_confidence = max(0.1 - day * 0.02, 0)
        
        # 市场状态影响
        state_confidence = 0.05 if patterns['market_state'] in ['trending', 'consolidation'] else 0
        
        total_confidence = (base_confidence + trend_confidence + volatility_confidence + 
                           cycle_confidence + time_confidence + state_confidence)
        
        return min(total_confidence, 0.95)
    
    def generate_prediction_summary(self):
        """
        生成预测摘要
        """
        if not self.forecast_data:
            return "暂无预测数据"
        
        summary = f"""
=== ETH未来5天K线预测摘要 ===

📊 预测概览:
- 预测天数: 5天
- 预测起始: {self.forecast_data[0]['date']}
- 预测结束: {self.forecast_data[-1]['date']}

📈 价格预测:
"""
        
        for i, day in enumerate(self.forecast_data):
            confidence_level = "高" if day['confidence'] > 0.8 else "中" if day['confidence'] > 0.6 else "低"
            summary += f"""
第{i+1}天 ({day['date']}):
- 开盘: ${day['open']:,.2f}
- 最高: ${day['high']:,.2f}
- 最低: ${day['low']:,.2f}
- 收盘: ${day['close']:,.2f}
- 涨跌: {day['change']:+.2f} ({day['change_percent']:+.2f}%)
- 交易量: {day['volume']:.2f} 十亿美元
- 置信度: {day['confidence']:.1%} ({confidence_level})
"""
        
        # 计算总体预测
        first_price = self.forecast_data[0]['open']
        last_price = self.forecast_data[-1]['close']
        total_change = (last_price - first_price) / first_price * 100
        
        avg_confidence = statistics.mean([d['confidence'] for d in self.forecast_data])
        
        summary += f"""

📊 预测总结:
- 预测总涨幅: {total_change:+.2f}%
- 平均置信度: {avg_confidence:.1%}
- 预测价格区间: ${min([d['low'] for d in self.forecast_data]):,.2f} - ${max([d['high'] for d in self.forecast_data]):,.2f}
- 平均日交易量: {statistics.mean([d['volume'] for d in self.forecast_data]):.2f} 十亿美元

⚠️ 风险提示:
- 预测基于历史数据模式，实际市场可能偏离预测
- 建议结合实时市场消息和基本面分析
- 设置合理的止损和止盈位
- 预测置信度仅供参考，不构成投资建议
        """
        
        return summary

if __name__ == "__main__":
    # 测试预测器
    predictor = ETHFutureKlinePredictor()
    
    # 模拟历史数据
    test_historical_data = [
        {
            'date': '2025-09-08',
            'total_volume': 15.2,
            'price': {'open': 3500, 'high': 3550, 'low': 3480, 'close': 3520}
        },
        {
            'date': '2025-09-09',
            'total_volume': 16.1,
            'price': {'open': 3520, 'high': 3580, 'low': 3510, 'close': 3560}
        }
    ]
    
    forecast_data = predictor.predict_future_5days_kline(test_historical_data)
    print("未来5天K线预测完成")
    print(predictor.generate_prediction_summary())
