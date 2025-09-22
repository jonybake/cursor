#!/usr/bin/env python3
"""
ETH K线图合理性分析
验证生成的K线图是否符合真实市场规律
"""

import json
import math
from datetime import datetime

class CandlestickAnalyzer:
    def __init__(self):
        self.data = None
        
    def load_data(self):
        """加载K线数据"""
        try:
            with open('/workspace/eth_candlestick_data.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print("成功加载K线数据")
        except FileNotFoundError:
            print("找不到K线数据文件")
            return False
        return True
    
    def analyze_volume_price_correlation(self):
        """分析成交量与价格的相关性"""
        print("\n=== 成交量与价格相关性分析 ===")
        
        if not self.data or 'candlesticks' not in self.data:
            print("没有K线数据")
            return
        
        candles = self.data['candlesticks']
        
        # 计算价格变化
        price_changes = []
        volume_ratios = []
        
        for i in range(1, len(candles)):
            prev_close = candles[i-1]['close']
            curr_close = candles[i]['close']
            price_change = (curr_close - prev_close) / prev_close
            
            price_changes.append(price_change)
            volume_ratios.append(candles[i]['volume_ratio'])
        
        # 计算相关性
        if len(price_changes) > 1:
            correlation = self.calculate_correlation(price_changes, volume_ratios)
            print(f"价格变化与成交量相关性: {correlation:.3f}")
            
            # 分析高成交量时的价格变化
            high_volume_changes = [price_changes[i] for i, vr in enumerate(volume_ratios) if vr > 1.5]
            low_volume_changes = [price_changes[i] for i, vr in enumerate(volume_ratios) if vr < 0.7]
            
            if high_volume_changes:
                avg_high_vol_change = sum(high_volume_changes) / len(high_volume_changes)
                print(f"高成交量时平均价格变化: {avg_high_vol_change:.3f} ({avg_high_vol_change*100:.2f}%)")
            
            if low_volume_changes:
                avg_low_vol_change = sum(low_volume_changes) / len(low_volume_changes)
                print(f"低成交量时平均价格变化: {avg_low_vol_change:.3f} ({avg_low_vol_change*100:.2f}%)")
    
    def calculate_correlation(self, x, y):
        """计算两个序列的相关系数"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi**2 for xi in x)
        sum_y2 = sum(yi**2 for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def analyze_candlestick_patterns(self):
        """分析K线形态模式"""
        print("\n=== K线形态分析 ===")
        
        if not self.data or 'candlesticks' not in self.data:
            print("没有K线数据")
            return
        
        candles = self.data['candlesticks']
        
        # 统计不同形态的K线
        doji_count = 0  # 十字星
        hammer_count = 0  # 锤子线
        shooting_star_count = 0  # 流星线
        long_body_count = 0  # 长实体
        short_body_count = 0  # 短实体
        
        for candle in candles:
            body_size = candle['body_size']
            upper_shadow = candle['upper_shadow']
            lower_shadow = candle['lower_shadow']
            total_range = candle['high'] - candle['low']
            
            # 十字星：实体很小
            if body_size < total_range * 0.1:
                doji_count += 1
            
            # 锤子线：下影线长，上影线短，实体小
            elif lower_shadow > body_size * 2 and upper_shadow < body_size and body_size < total_range * 0.3:
                hammer_count += 1
            
            # 流星线：上影线长，下影线短，实体小
            elif upper_shadow > body_size * 2 and lower_shadow < body_size and body_size < total_range * 0.3:
                shooting_star_count += 1
            
            # 长实体
            elif body_size > total_range * 0.7:
                long_body_count += 1
            
            # 短实体
            elif body_size < total_range * 0.3:
                short_body_count += 1
        
        print(f"十字星: {doji_count} ({doji_count/len(candles)*100:.1f}%)")
        print(f"锤子线: {hammer_count} ({hammer_count/len(candles)*100:.1f}%)")
        print(f"流星线: {shooting_star_count} ({shooting_star_count/len(candles)*100:.1f}%)")
        print(f"长实体: {long_body_count} ({long_body_count/len(candles)*100:.1f}%)")
        print(f"短实体: {short_body_count} ({short_body_count/len(candles)*100:.1f}%)")
    
    def analyze_volatility_patterns(self):
        """分析波动性模式"""
        print("\n=== 波动性分析 ===")
        
        if not self.data or 'candlesticks' not in self.data:
            print("没有K线数据")
            return
        
        candles = self.data['candlesticks']
        
        # 计算每小时波动率
        volatilities = []
        for candle in candles:
            total_range = candle['high'] - candle['low']
            volatility = total_range / candle['open']
            volatilities.append(volatility)
        
        avg_volatility = sum(volatilities) / len(volatilities)
        max_volatility = max(volatilities)
        min_volatility = min(volatilities)
        
        print(f"平均波动率: {avg_volatility:.3f} ({avg_volatility*100:.2f}%)")
        print(f"最大波动率: {max_volatility:.3f} ({max_volatility*100:.2f}%)")
        print(f"最小波动率: {min_volatility:.3f} ({min_volatility*100:.2f}%)")
        
        # 分析不同时段的波动性
        asian_vol = []
        european_vol = []
        american_vol = []
        
        for i, candle in enumerate(candles):
            hour = i % 24
            volatility = volatilities[i]
            
            if 0 <= hour < 8:  # 亚洲时段
                asian_vol.append(volatility)
            elif 8 <= hour < 16:  # 欧洲时段
                european_vol.append(volatility)
            else:  # 美洲时段
                american_vol.append(volatility)
        
        if asian_vol:
            print(f"亚洲时段平均波动率: {sum(asian_vol)/len(asian_vol)*100:.2f}%")
        if european_vol:
            print(f"欧洲时段平均波动率: {sum(european_vol)/len(european_vol)*100:.2f}%")
        if american_vol:
            print(f"美洲时段平均波动率: {sum(american_vol)/len(american_vol)*100:.2f}%")
    
    def analyze_trend_consistency(self):
        """分析趋势一致性"""
        print("\n=== 趋势一致性分析 ===")
        
        if not self.data or 'candlesticks' not in self.data:
            print("没有K线数据")
            return
        
        candles = self.data['candlesticks']
        
        # 计算连续同向K线
        consecutive_bullish = 0
        consecutive_bearish = 0
        max_consecutive_bullish = 0
        max_consecutive_bearish = 0
        
        for candle in candles:
            if candle['is_bullish']:
                consecutive_bullish += 1
                consecutive_bearish = 0
                max_consecutive_bullish = max(max_consecutive_bullish, consecutive_bullish)
            else:
                consecutive_bearish += 1
                consecutive_bullish = 0
                max_consecutive_bearish = max(max_consecutive_bearish, consecutive_bearish)
        
        print(f"最长连续阳线: {max_consecutive_bullish}")
        print(f"最长连续阴线: {max_consecutive_bearish}")
        
        # 分析趋势强度
        price_changes = []
        for i in range(1, len(candles)):
            change = (candles[i]['close'] - candles[i-1]['close']) / candles[i-1]['close']
            price_changes.append(change)
        
        if price_changes:
            avg_change = sum(price_changes) / len(price_changes)
            volatility = math.sqrt(sum((c - avg_change)**2 for c in price_changes) / len(price_changes))
            print(f"平均价格变化: {avg_change:.4f} ({avg_change*100:.2f}%)")
            print(f"价格变化标准差: {volatility:.4f} ({volatility*100:.2f}%)")
    
    def validate_market_realism(self):
        """验证市场真实性"""
        print("\n=== 市场真实性验证 ===")
        
        if not self.data or 'candlesticks' not in self.data:
            print("没有K线数据")
            return
        
        candles = self.data['candlesticks']
        
        # 检查价格跳跃的合理性
        large_jumps = 0
        for i in range(1, len(candles)):
            prev_close = candles[i-1]['close']
            curr_open = candles[i]['open']
            jump = abs(curr_open - prev_close) / prev_close
            
            if jump > 0.1:  # 超过10%的跳跃
                large_jumps += 1
        
        print(f"异常价格跳跃次数: {large_jumps} ({large_jumps/len(candles)*100:.1f}%)")
        
        # 检查成交量分布
        volumes = [c['volume'] for c in candles]
        avg_volume = sum(volumes) / len(volumes)
        high_volume_count = len([v for v in volumes if v > avg_volume * 2])
        low_volume_count = len([v for v in volumes if v < avg_volume * 0.5])
        
        print(f"高成交量时段: {high_volume_count} ({high_volume_count/len(candles)*100:.1f}%)")
        print(f"低成交量时段: {low_volume_count} ({low_volume_count/len(candles)*100:.1f}%)")
        
        # 检查价格范围合理性
        prices = [c['close'] for c in candles]
        price_range = max(prices) - min(prices)
        avg_price = sum(prices) / len(prices)
        range_ratio = price_range / avg_price
        
        print(f"价格波动范围: {range_ratio:.3f} ({range_ratio*100:.1f}%)")
        
        # 评估真实性
        realism_score = 0
        if large_jumps / len(candles) < 0.05:  # 异常跳跃少于5%
            realism_score += 25
        if 0.1 < range_ratio < 0.5:  # 合理的价格波动范围
            realism_score += 25
        if 0.15 < high_volume_count / len(candles) < 0.35:  # 合理的高成交量比例
            realism_score += 25
        if 0.1 < low_volume_count / len(candles) < 0.3:  # 合理的低成交量比例
            realism_score += 25
        
        print(f"\n市场真实性评分: {realism_score}/100")
        
        if realism_score >= 75:
            print("✅ K线图高度符合真实市场特征")
        elif realism_score >= 50:
            print("⚠️ K线图基本符合市场特征，但存在一些异常")
        else:
            print("❌ K线图存在较多不符合市场规律的特征")
    
    def run_analysis(self):
        """运行完整分析"""
        print("开始K线图合理性分析...")
        
        if not self.load_data():
            return
        
        self.analyze_volume_price_correlation()
        self.analyze_candlestick_patterns()
        self.analyze_volatility_patterns()
        self.analyze_trend_consistency()
        self.validate_market_realism()
        
        print("\n分析完成！")

if __name__ == "__main__":
    analyzer = CandlestickAnalyzer()
    analyzer.run_analysis()