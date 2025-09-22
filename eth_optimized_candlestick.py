#!/usr/bin/env python3
"""
优化的ETH K线图生成器
基于真实市场规律生成更合理的K线图
"""

import math
import random
from datetime import datetime, timedelta
import json

class OptimizedETHCandlestickGenerator:
    def __init__(self):
        self.volume_data = []
        self.candlesticks = []
        
    def generate_realistic_volume_pattern(self, days=7):
        """生成更真实的成交量模式"""
        print("生成符合真实ETH交易模式的成交量数据...")
        
        random.seed(42)
        
        # 基于真实ETH交易模式的参数
        base_volume = 800000
        peak_volume = 2500000
        low_volume = 300000
        
        hours = days * 24
        current_time = datetime.now() - timedelta(days=days)
        
        for hour in range(hours):
            hour_of_day = hour % 24
            day_of_week = (hour // 24) % 7
            
            # 更精确的时段成交量模式
            if 0 <= hour_of_day < 6:  # 深夜亚洲时段
                volume_multiplier = 0.4 + random.uniform(-0.1, 0.2)
            elif 6 <= hour_of_day < 12:  # 亚洲上午
                volume_multiplier = 0.8 + random.uniform(-0.2, 0.3)
            elif 12 <= hour_of_day < 16:  # 欧洲时段
                volume_multiplier = 1.2 + random.uniform(-0.3, 0.4)
            elif 16 <= hour_of_day < 20:  # 美洲开盘
                volume_multiplier = 1.5 + random.uniform(-0.2, 0.5)
            else:  # 美洲下午
                volume_multiplier = 1.0 + random.uniform(-0.3, 0.3)
            
            # 周末效应
            if day_of_week in [5, 6]:
                volume_multiplier *= 0.6
            
            # 添加市场事件影响（模拟）
            if random.random() < 0.05:  # 5%概率出现高成交量事件
                volume_multiplier *= random.uniform(2.0, 4.0)
            
            # 计算成交量
            volume = int(base_volume * volume_multiplier)
            volume = max(low_volume, min(volume, peak_volume))
            
            self.volume_data.append({
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'volume': volume,
                'hour_of_day': hour_of_day,
                'day_of_week': day_of_week,
                'volume_multiplier': volume_multiplier
            })
            
            current_time += timedelta(hours=1)
        
        print(f"生成了 {len(self.volume_data)} 小时的成交量数据")
    
    def generate_realistic_price_movement(self):
        """生成更真实的价格走势"""
        print("基于成交量生成真实的价格走势...")
        
        if not self.volume_data:
            print("没有成交量数据")
            return
        
        # 初始价格
        base_price = 3200.0
        current_price = base_price
        
        # 计算成交量统计
        volumes = [d['volume'] for d in self.volume_data]
        avg_volume = sum(volumes) / len(volumes)
        high_volume_threshold = avg_volume * 1.8
        low_volume_threshold = avg_volume * 0.5
        
        # 价格趋势参数
        trend_direction = 0  # -1下跌, 0横盘, 1上涨
        trend_strength = 0.0
        trend_duration = 0
        
        for i, vol_data in enumerate(self.volume_data):
            volume = vol_data['volume']
            hour_of_day = vol_data['hour_of_day']
            
            # 更新趋势
            if trend_duration <= 0:
                # 随机选择新趋势
                trend_direction = random.choice([-1, 0, 1])
                trend_strength = random.uniform(0.3, 1.0)
                trend_duration = random.randint(4, 24)  # 4-24小时趋势
            
            trend_duration -= 1
            
            # 基础波动率
            if volume > high_volume_threshold:
                base_volatility = 0.025  # 高成交量时波动更大
            elif volume < low_volume_threshold:
                base_volatility = 0.008  # 低成交量时波动较小
            else:
                base_volatility = 0.015  # 正常波动
            
            # 时段调整
            if 8 <= hour_of_day < 16:  # 欧洲时段
                base_volatility *= 1.3
            elif 16 <= hour_of_day < 24:  # 美洲时段
                base_volatility *= 1.5
            
            # 趋势影响
            trend_impact = trend_direction * trend_strength * base_volatility * 0.5
            
            # 随机波动
            random_volatility = random.gauss(0, base_volatility)
            
            # 成交量影响
            volume_impact = 0
            if volume > high_volume_threshold:
                # 高成交量时更可能推动趋势
                volume_impact = trend_direction * random.uniform(0.01, 0.03)
            elif volume < low_volume_threshold:
                # 低成交量时价格变化较小
                volume_impact = random.gauss(0, base_volatility * 0.5)
            
            # 计算价格变化
            total_change = trend_impact + random_volatility + volume_impact
            new_price = current_price * (1 + total_change)
            
            # 生成OHLC
            open_price = current_price
            close_price = new_price
            
            # 根据成交量和波动性确定高低价
            price_range_base = abs(close_price - open_price)
            
            if volume > high_volume_threshold:
                # 高成交量：更大的价格区间
                range_multiplier = random.uniform(1.5, 3.0)
            elif volume < low_volume_threshold:
                # 低成交量：较小的价格区间
                range_multiplier = random.uniform(0.5, 1.2)
            else:
                # 正常成交量
                range_multiplier = random.uniform(1.0, 2.0)
            
            price_range = price_range_base * range_multiplier
            
            # 生成高低价
            if close_price > open_price:  # 阳线
                high_price = close_price + price_range * random.uniform(0.3, 0.8)
                low_price = open_price - price_range * random.uniform(0.2, 0.6)
            else:  # 阴线
                high_price = open_price + price_range * random.uniform(0.2, 0.6)
                low_price = close_price - price_range * random.uniform(0.3, 0.8)
            
            # 确保价格逻辑正确
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # 计算K线特征
            body_size = abs(close_price - open_price)
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price
            total_range = high_price - low_price
            
            # 生成更真实的K线形态
            self.candlesticks.append({
                'timestamp': vol_data['timestamp'],
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'body_size': round(body_size, 2),
                'upper_shadow': round(upper_shadow, 2),
                'lower_shadow': round(lower_shadow, 2),
                'total_range': round(total_range, 2),
                'is_bullish': close_price > open_price,
                'volume_ratio': round(volume / avg_volume, 2),
                'hour_of_day': hour_of_day,
                'day_of_week': vol_data['day_of_week']
            })
            
            current_price = close_price
    
    def analyze_generated_data(self):
        """分析生成的数据"""
        print("\n=== 生成数据分析 ===")
        
        if not self.candlesticks:
            print("没有K线数据")
            return
        
        # 基本统计
        prices = [c['close'] for c in self.candlesticks]
        volumes = [c['volume'] for c in self.candlesticks]
        
        print(f"总K线数: {len(self.candlesticks)}")
        print(f"价格范围: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"平均价格: ${sum(prices)/len(prices):.2f}")
        print(f"成交量范围: {min(volumes):,} - {max(volumes):,}")
        print(f"平均成交量: {sum(volumes)/len(volumes):,.0f}")
        
        # 阳线阴线统计
        bullish = [c for c in self.candlesticks if c['is_bullish']]
        bearish = [c for c in self.candlesticks if not c['is_bullish']]
        
        print(f"阳线: {len(bullish)} ({len(bullish)/len(self.candlesticks)*100:.1f}%)")
        print(f"阴线: {len(bearish)} ({len(bearish)/len(self.candlesticks)*100:.1f}%)")
        
        # 成交量分析
        high_volume = [c for c in self.candlesticks if c['volume_ratio'] > 1.5]
        low_volume = [c for c in self.candlesticks if c['volume_ratio'] < 0.7]
        
        print(f"高成交量K线: {len(high_volume)} ({len(high_volume)/len(self.candlesticks)*100:.1f}%)")
        print(f"低成交量K线: {len(low_volume)} ({len(low_volume)/len(self.candlesticks)*100:.1f}%)")
        
        # 波动性分析
        volatilities = [c['total_range'] / c['open'] for c in self.candlesticks]
        avg_volatility = sum(volatilities) / len(volatilities)
        print(f"平均波动率: {avg_volatility:.3f} ({avg_volatility*100:.2f}%)")
    
    def create_enhanced_text_chart(self):
        """创建增强的文本K线图"""
        print("\n=== 增强K线图可视化 ===")
        
        if not self.candlesticks:
            print("没有K线数据")
            return
        
        # 选择显示的数据点
        display_data = self.candlesticks[::3]  # 每3小时显示一个点
        
        # 计算价格范围
        all_highs = [c['high'] for c in display_data]
        all_lows = [c['low'] for c in display_data]
        max_price = max(all_highs)
        min_price = min(all_lows)
        price_range = max_price - min_price
        
        # 创建图表
        chart_height = 25
        chart_width = min(60, len(display_data))
        
        print(f"\nK线图 (每3小时一根K线):")
        print("=" * (chart_width + 15))
        
        for row in range(chart_height):
            price_level = max_price - (price_range * row / chart_height)
            line = f"{price_level:8.0f} |"
            
            for i, candle in enumerate(display_data[:chart_width]):
                if candle['high'] >= price_level >= candle['low']:
                    if candle['is_bullish']:
                        if candle['close'] >= price_level >= candle['open']:
                            # 阳线实体
                            if candle['volume_ratio'] > 1.5:
                                line += "█"  # 高成交量阳线
                            else:
                                line += "▄"  # 普通阳线
                        else:
                            line += "│"  # 阳线影线
                    else:
                        if candle['open'] >= price_level >= candle['close']:
                            # 阴线实体
                            if candle['volume_ratio'] > 1.5:
                                line += "▓"  # 高成交量阴线
                            else:
                                line += "▀"  # 普通阴线
                        else:
                            line += "│"  # 阴线影线
                else:
                    line += " "
            
            print(line)
        
        print("         " + "-" * chart_width)
        print("         时间轴 ->")
        
        # 显示图例
        print("\n图例:")
        print("█ = 高成交量阳线  ▄ = 普通阳线")
        print("▓ = 高成交量阴线  ▀ = 普通阴线")
        print("│ = 影线")
    
    def save_results(self):
        """保存结果"""
        results = {
            'volume_data': self.volume_data,
            'candlesticks': self.candlesticks,
            'analysis_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_candles': len(self.candlesticks),
                'bullish_candles': len([c for c in self.candlesticks if c['is_bullish']]),
                'bearish_candles': len([c for c in self.candlesticks if not c['is_bullish']]),
                'high_volume_candles': len([c for c in self.candlesticks if c['volume_ratio'] > 1.5]),
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
        
        with open('/workspace/eth_optimized_candlestick_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n优化K线数据已保存到 eth_optimized_candlestick_data.json")
    
    def run_generation(self):
        """运行完整的优化K线生成"""
        print("开始生成优化的ETH K线图...")
        
        # 生成成交量数据
        self.generate_realistic_volume_pattern(days=7)
        
        # 生成价格走势
        self.generate_realistic_price_movement()
        
        # 分析数据
        self.analyze_generated_data()
        
        # 创建可视化
        self.create_enhanced_text_chart()
        
        # 保存结果
        self.save_results()
        
        print("\n优化K线图生成完成！")

if __name__ == "__main__":
    generator = OptimizedETHCandlestickGenerator()
    generator.run_generation()