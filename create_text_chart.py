#!/usr/bin/env python3
"""
创建文本图表来可视化ETH预测结果
"""

import json
import math

def create_text_chart():
    """创建文本图表"""
    
    # 读取预测结果
    try:
        with open('/workspace/eth_prediction_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("找不到预测结果文件")
        return
    
    historical = data['historical_data']
    predictions = data['predictions']
    
    # 合并数据用于显示
    all_data = historical + predictions
    all_prices = [d['close'] for d in all_data]
    all_volumes = [d['volume'] for d in all_data]
    
    # 计算价格范围
    min_price = min(all_prices)
    max_price = max(all_prices)
    price_range = max_price - min_price
    
    # 计算成交量范围
    min_volume = min(all_volumes)
    max_volume = max(all_volumes)
    volume_range = max_volume - min_volume
    
    print("\n" + "="*80)
    print("ETH价格预测可视化图表")
    print("="*80)
    
    # 创建价格图表
    print("\n价格走势图 (H=历史数据, P=预测数据):")
    print("-" * 60)
    
    # 简化显示：每6小时显示一个点
    chart_data = []
    for i in range(0, len(all_data), 6):
        chart_data.append(all_data[i])
    
    # 创建价格图表
    chart_height = 20
    for row in range(chart_height):
        price_level = max_price - (price_range * row / chart_height)
        line = f"{price_level:8.0f} |"
        
        for i, point in enumerate(chart_data):
            if i >= 50:  # 限制显示长度
                break
                
            if point['close'] >= price_level:
                if i < len(historical):
                    line += "H"
                else:
                    line += "P"
            else:
                line += " "
        
        print(line)
    
    print("         " + "-" * 50)
    print("         历史数据(H) -> 预测数据(P)")
    
    # 创建成交量图表
    print(f"\n成交量图表 (每6小时一个点):")
    print("-" * 60)
    
    volume_chart_height = 15
    for row in range(volume_chart_height):
        volume_level = max_volume - (volume_range * row / volume_chart_height)
        line = f"{volume_level:8.0f} |"
        
        for i, point in enumerate(chart_data):
            if i >= 50:
                break
                
            if point['volume'] >= volume_level:
                if i < len(historical):
                    line += "█"
                else:
                    line += "▓"
            else:
                line += " "
        
        print(line)
    
    print("         " + "-" * 50)
    print("         历史成交量(█) -> 预测成交量(▓)")
    
    # 显示关键统计信息
    print(f"\n关键统计信息:")
    print(f"历史数据点数: {len(historical)}")
    print(f"预测数据点数: {len(predictions)}")
    print(f"历史价格范围: ${min(historical, key=lambda x: x['close'])['close']:.2f} - ${max(historical, key=lambda x: x['close'])['close']:.2f}")
    print(f"预测价格范围: ${min(predictions, key=lambda x: x['close'])['close']:.2f} - ${max(predictions, key=lambda x: x['close'])['close']:.2f}")
    
    # 显示预测趋势
    if len(predictions) >= 24:
        first_day_avg = sum(p['close'] for p in predictions[:24]) / 24
        second_day_avg = sum(p['close'] for p in predictions[24:48]) / 24
        third_day_avg = sum(p['close'] for p in predictions[48:72]) / 24
        
        print(f"\n预测趋势分析:")
        print(f"第1天平均价: ${first_day_avg:.2f}")
        print(f"第2天平均价: ${second_day_avg:.2f}")
        print(f"第3天平均价: ${third_day_avg:.2f}")
        
        trend = "上涨" if third_day_avg > first_day_avg else "下跌"
        change_pct = ((third_day_avg - first_day_avg) / first_day_avg) * 100
        print(f"3天趋势: {trend} {abs(change_pct):.2f}%")

if __name__ == "__main__":
    create_text_chart()