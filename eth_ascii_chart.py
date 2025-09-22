#!/usr/bin/env python3
"""
生成ETH预测K线图的ASCII艺术表示
"""

import json
from datetime import datetime, timedelta

def create_ascii_kline_chart():
    """创建ASCII格式的K线图"""
    
    # 读取预测数据
    with open('/workspace/eth_forecast_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    historical_data = data['historical_data']
    forecast_data = data['forecast_data']
    
    # 合并数据
    all_data = historical_data + forecast_data
    
    # 找到价格范围
    all_prices = []
    for day in all_data:
        all_prices.extend([day['open'], day['high'], day['low'], day['close']])
    
    min_price = min(all_prices)
    max_price = max(all_prices)
    price_range = max_price - min_price
    
    # 创建ASCII图表
    chart_height = 20
    chart_width = len(all_data) * 4
    
    print("=" * 80)
    print("ETH未来3天K线预测 - ASCII图表")
    print("=" * 80)
    print()
    
    # 绘制价格线
    print("价格走势图:")
    print(f"最高价: ${max_price:,.2f}")
    print(f"最低价: ${min_price:,.2f}")
    print()
    
    # 创建网格
    grid = [[' ' for _ in range(chart_width)] for _ in range(chart_height)]
    
    # 绘制价格线
    for i, day in enumerate(all_data):
        x = i * 4 + 2
        
        # 计算价格在网格中的位置
        price_y = int((day['close'] - min_price) / price_range * (chart_height - 1))
        price_y = chart_height - 1 - price_y  # 翻转Y轴
        
        # 绘制价格点
        if 0 <= price_y < chart_height and 0 <= x < chart_width:
            if i < len(historical_data):
                grid[price_y][x] = '●'  # 历史数据用实心圆
            else:
                grid[price_y][x] = '○'  # 预测数据用空心圆
    
    # 绘制网格
    for row in grid:
        print(''.join(row))
    
    print()
    print("图例: ● 历史数据  ○ 预测数据")
    print()
    
    # 绘制K线图
    print("K线图 (简化版):")
    print("-" * 80)
    
    for i, day in enumerate(all_data):
        date_str = day['date'][5:]  # 只显示月-日
        data_type = "历史" if i < len(historical_data) else "预测"
        
        # 简化的K线表示
        open_price = day['open']
        close_price = day['close']
        high_price = day['high']
        low_price = day['low']
        
        # 判断涨跌
        if close_price >= open_price:
            color = "📈"  # 上涨
        else:
            color = "📉"  # 下跌
        
        print(f"{date_str} {data_type:2} {color} 开盘:${open_price:7.2f} 收盘:${close_price:7.2f} 最高:${high_price:7.2f} 最低:${low_price:7.2f}")
    
    print("-" * 80)
    print()
    
    # 预测摘要
    print("🔮 预测摘要:")
    print(f"预测期间: {forecast_data[0]['date']} 至 {forecast_data[-1]['date']}")
    print(f"起始价格: ${historical_data[-1]['close']:,.2f}")
    print(f"结束价格: ${forecast_data[-1]['close']:,.2f}")
    
    total_change = (forecast_data[-1]['close'] - historical_data[-1]['close']) / historical_data[-1]['close']
    print(f"总变化: {total_change:+.1%}")
    
    # 计算每日变化
    print("\n每日预测变化:")
    prev_price = historical_data[-1]['close']
    for i, day in enumerate(forecast_data):
        daily_change = (day['close'] - prev_price) / prev_price
        print(f"第{i+1}天: {day['date']} {daily_change:+.1%} (${day['close']:,.2f})")
        prev_price = day['close']
    
    print()
    print("⚠️  风险提示: 预测基于历史数据，实际结果可能不同")
    print("=" * 80)

if __name__ == "__main__":
    create_ascii_kline_chart()