#!/usr/bin/env python3
"""
ETH K线图生成器
基于一周交易量数据推算最合理的K线图
"""

import math
import random
from datetime import datetime, timedelta
import json

class ETHCandlestickGenerator:
    def __init__(self):
        self.volume_data = []
        self.price_data = []
        self.candlesticks = []
        
    def generate_realistic_volume_pattern(self, days=7):
        """生成符合ETH真实交易模式的成交量数据"""
        print("生成符合ETH真实交易模式的成交量数据...")
        
        # 设置随机种子
        random.seed(42)
        
        # ETH典型的成交量模式参数
        base_volume = 1200000  # 基础成交量
        peak_volume = 3500000  # 峰值成交量
        low_volume = 400000    # 低成交量
        
        # 生成一周的小时数据
        hours = days * 24
        current_time = datetime.now() - timedelta(days=days)
        
        for hour in range(hours):
            # 模拟日内交易模式
            hour_of_day = hour % 24
            
            # 亚洲时段 (0-8): 相对较低成交量
            if 0 <= hour_of_day < 8:
                volume_multiplier = 0.6 + random.uniform(-0.2, 0.3)
            # 欧洲时段 (8-16): 中等成交量
            elif 8 <= hour_of_day < 16:
                volume_multiplier = 1.0 + random.uniform(-0.3, 0.4)
            # 美洲时段 (16-24): 最高成交量
            else:
                volume_multiplier = 1.3 + random.uniform(-0.2, 0.5)
            
            # 模拟周末效应
            day_of_week = (hour // 24) % 7
            if day_of_week in [5, 6]:  # 周末
                volume_multiplier *= 0.7
            
            # 添加随机波动
            random_factor = random.uniform(0.5, 1.8)
            
            # 计算最终成交量
            volume = int(base_volume * volume_multiplier * random_factor)
            volume = max(low_volume, min(volume, peak_volume))
            
            self.volume_data.append({
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'volume': volume,
                'hour_of_day': hour_of_day,
                'day_of_week': day_of_week
            })
            
            current_time += timedelta(hours=1)
        
        print(f"生成了 {len(self.volume_data)} 小时的成交量数据")
    
    def calculate_volume_price_correlation(self):
        """计算成交量与价格变化的相关性"""
        # 基于真实市场观察的规律
        correlations = {
            'high_volume_up': 0.3,    # 高成交量上涨概率
            'high_volume_down': 0.2,  # 高成交量下跌概率
            'low_volume_up': 0.15,    # 低成交量上涨概率
            'low_volume_down': 0.1,   # 低成交量下跌概率
            'normal_volume_up': 0.25, # 正常成交量上涨概率
            'normal_volume_down': 0.2 # 正常成交量下跌概率
        }
        return correlations
    
    def generate_price_from_volume(self):
        """基于成交量生成合理的价格走势"""
        print("基于成交量生成价格走势...")
        
        if not self.volume_data:
            print("没有成交量数据")
            return
        
        # 初始价格
        base_price = 3200.0
        current_price = base_price
        
        # 计算成交量统计
        volumes = [d['volume'] for d in self.volume_data]
        avg_volume = sum(volumes) / len(volumes)
        high_volume_threshold = avg_volume * 1.5
        low_volume_threshold = avg_volume * 0.6
        
        correlations = self.calculate_volume_price_correlation()
        
        for i, vol_data in enumerate(self.volume_data):
            volume = vol_data['volume']
            hour_of_day = vol_data['hour_of_day']
            
            # 根据成交量确定价格变化幅度
            if volume > high_volume_threshold:
                # 高成交量：更大的价格波动
                base_volatility = 0.02
                trend_strength = 0.8
            elif volume < low_volume_threshold:
                # 低成交量：较小的价格波动
                base_volatility = 0.008
                trend_strength = 0.3
            else:
                # 正常成交量
                base_volatility = 0.015
                trend_strength = 0.5
            
            # 根据时间段调整波动性
            if 8 <= hour_of_day < 16:  # 欧洲时段
                base_volatility *= 1.2
            elif 16 <= hour_of_day < 24:  # 美洲时段
                base_volatility *= 1.5
            
            # 生成价格变化
            price_change = random.gauss(0, base_volatility)
            
            # 根据成交量方向调整趋势
            if volume > avg_volume * 1.2:
                # 高成交量倾向于推动趋势
                if random.random() < 0.6:
                    price_change = abs(price_change) * (1 if random.random() < 0.5 else -1)
            
            # 应用价格变化
            new_price = current_price * (1 + price_change)
            
            # 确保价格合理性（防止极端值）
            new_price = max(new_price, current_price * 0.95)
            new_price = min(new_price, current_price * 1.05)
            
            # 生成OHLC数据
            open_price = current_price
            close_price = new_price
            
            # 根据成交量确定高低价
            price_range = abs(close_price - open_price)
            if volume > high_volume_threshold:
                # 高成交量：更大的价格区间
                high_price = max(open_price, close_price) + price_range * random.uniform(0.5, 1.5)
                low_price = min(open_price, close_price) - price_range * random.uniform(0.5, 1.5)
            else:
                # 正常或低成交量：较小的价格区间
                high_price = max(open_price, close_price) + price_range * random.uniform(0.2, 0.8)
                low_price = min(open_price, close_price) - price_range * random.uniform(0.2, 0.8)
            
            # 确保高低价合理
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            self.price_data.append({
                'timestamp': vol_data['timestamp'],
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'hour_of_day': hour_of_day,
                'day_of_week': vol_data['day_of_week']
            })
            
            current_price = close_price
    
    def generate_candlestick_patterns(self):
        """生成符合技术分析的K线形态"""
        print("生成K线形态...")
        
        if not self.price_data:
            print("没有价格数据")
            return
        
        # 分析价格数据，生成更合理的K线形态
        for i, price_point in enumerate(self.price_data):
            open_price = price_point['open']
            high_price = price_point['high']
            low_price = price_point['low']
            close_price = price_point['close']
            volume = price_point['volume']
            
            # 计算K线特征
            body_size = abs(close_price - open_price)
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price
            total_range = high_price - low_price
            
            # 根据成交量调整K线形态
            avg_volume = sum(p['volume'] for p in self.price_data) / len(self.price_data)
            volume_ratio = volume / avg_volume
            
            # 高成交量时，K线实体通常更大
            if volume_ratio > 1.5:
                body_size *= random.uniform(1.2, 1.8)
            elif volume_ratio < 0.7:
                body_size *= random.uniform(0.5, 0.8)
            
            # 重新计算OHLC
            if close_price > open_price:  # 阳线
                new_close = open_price + body_size
                new_high = new_close + upper_shadow * random.uniform(0.5, 1.2)
                new_low = open_price - lower_shadow * random.uniform(0.5, 1.2)
            else:  # 阴线
                new_close = open_price - body_size
                new_high = open_price + upper_shadow * random.uniform(0.5, 1.2)
                new_low = new_close - lower_shadow * random.uniform(0.5, 1.2)
            
            # 确保价格逻辑正确
            new_high = max(new_high, open_price, new_close)
            new_low = min(new_low, open_price, new_close)
            
            self.candlesticks.append({
                'timestamp': price_point['timestamp'],
                'open': round(open_price, 2),
                'high': round(new_high, 2),
                'low': round(new_low, 2),
                'close': round(new_close, 2),
                'volume': volume,
                'body_size': round(body_size, 2),
                'upper_shadow': round(new_high - max(open_price, new_close), 2),
                'lower_shadow': round(min(open_price, new_close) - new_low, 2),
                'is_bullish': new_close > open_price,
                'volume_ratio': round(volume_ratio, 2)
            })
    
    def analyze_patterns(self):
        """分析生成的K线模式"""
        print("\n=== K线模式分析 ===")
        
        if not self.candlesticks:
            print("没有K线数据")
            return
        
        # 统计不同类型的K线
        bullish_candles = [c for c in self.candlesticks if c['is_bullish']]
        bearish_candles = [c for c in self.candlesticks if not c['is_bullish']]
        
        print(f"总K线数: {len(self.candlesticks)}")
        print(f"阳线数: {len(bullish_candles)} ({len(bullish_candles)/len(self.candlesticks)*100:.1f}%)")
        print(f"阴线数: {len(bearish_candles)} ({len(bearish_candles)/len(self.candlesticks)*100:.1f}%)")
        
        # 分析成交量与价格关系
        high_volume_candles = [c for c in self.candlesticks if c['volume_ratio'] > 1.5]
        high_volume_bullish = [c for c in high_volume_candles if c['is_bullish']]
        
        print(f"高成交量K线: {len(high_volume_candles)}")
        print(f"高成交量阳线: {len(high_volume_bullish)} ({len(high_volume_bullish)/len(high_volume_candles)*100:.1f}%)")
        
        # 价格统计
        prices = [c['close'] for c in self.candlesticks]
        print(f"价格范围: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"平均价格: ${sum(prices)/len(prices):.2f}")
        
        # 成交量统计
        volumes = [c['volume'] for c in self.candlesticks]
        print(f"成交量范围: {min(volumes):,} - {max(volumes):,}")
        print(f"平均成交量: {sum(volumes)/len(volumes):,.0f}")
    
    def create_text_candlestick_chart(self):
        """创建文本K线图"""
        print("\n=== K线图可视化 ===")
        
        if not self.candlesticks:
            print("没有K线数据")
            return
        
        # 选择显示的数据点（每4小时一个）
        display_data = self.candlesticks[::4]
        
        # 计算价格范围
        all_highs = [c['high'] for c in display_data]
        all_lows = [c['low'] for c in display_data]
        max_price = max(all_highs)
        min_price = min(all_lows)
        price_range = max_price - min_price
        
        # 创建图表
        chart_height = 30
        chart_width = min(80, len(display_data))
        
        print(f"\nK线图 (每4小时一根K线):")
        print("=" * (chart_width + 10))
        
        for row in range(chart_height):
            price_level = max_price - (price_range * row / chart_height)
            line = f"{price_level:8.0f} |"
            
            for i, candle in enumerate(display_data[:chart_width]):
                if candle['high'] >= price_level >= candle['low']:
                    if candle['is_bullish']:
                        if candle['close'] >= price_level >= candle['open']:
                            line += "█"  # 阳线实体
                        else:
                            line += "│"  # 阳线影线
                    else:
                        if candle['open'] >= price_level >= candle['close']:
                            line += "▓"  # 阴线实体
                        else:
                            line += "│"  # 阴线影线
                else:
                    line += " "
            
            print(line)
        
        print("         " + "-" * chart_width)
        print("         时间轴 ->")
        
        # 显示时间标签
        time_labels = []
        for i in range(0, len(display_data), 8):  # 每8个点显示一个时间
            if i < len(display_data):
                time_str = display_data[i]['timestamp'][5:16]  # 月-日 时:分
                time_labels.append(time_str)
        
        print("时间: " + " ".join(time_labels))
    
    def save_results(self):
        """保存结果"""
        results = {
            'volume_data': self.volume_data,
            'price_data': self.price_data,
            'candlesticks': self.candlesticks,
            'analysis_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_candles': len(self.candlesticks),
                'bullish_candles': len([c for c in self.candlesticks if c['is_bullish']]),
                'bearish_candles': len([c for c in self.candlesticks if not c['is_bullish']]),
                'price_range': {
                    'high': max([c['high'] for c in self.candlesticks]),
                    'low': min([c['low'] for c in self.candlesticks])
                },
                'volume_stats': {
                    'avg': sum([c['volume'] for c in self.candlesticks]) / len(self.candlesticks),
                    'max': max([c['volume'] for c in self.candlesticks]),
                    'min': min([c['volume'] for c in self.candlesticks])
                }
            }
        }
        
        with open('/workspace/eth_candlestick_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nK线数据已保存到 eth_candlestick_data.json")
    
    def run_generation(self):
        """运行完整的K线生成流程"""
        print("开始生成基于交易量的ETH K线图...")
        
        # 生成成交量数据
        self.generate_realistic_volume_pattern(days=7)
        
        # 基于成交量生成价格
        self.generate_price_from_volume()
        
        # 生成K线形态
        self.generate_candlestick_patterns()
        
        # 分析模式
        self.analyze_patterns()
        
        # 创建可视化
        self.create_text_candlestick_chart()
        
        # 保存结果
        self.save_results()
        
        print("\nK线图生成完成！")

if __name__ == "__main__":
    generator = ETHCandlestickGenerator()
    generator.run_generation()