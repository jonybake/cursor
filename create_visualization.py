#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建ETH交易数据可视化图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def create_visualizations():
    """创建可视化图表"""
    print("📈 创建可视化图表...")
    
    # 读取数据
    volume_data = pd.read_csv('/workspace/eth_volume_data.csv')
    price_data = pd.read_csv('/workspace/eth_price_data.csv')
    predictions = pd.read_csv('/workspace/eth_kline_predictions.csv')
    
    # 转换日期格式
    volume_data['Date'] = pd.to_datetime(volume_data['Date'])
    price_data['Date'] = pd.to_datetime(price_data['Date'])
    predictions['Date'] = pd.to_datetime(predictions['Date'])
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('ETH 9月交易数据分析和预测', fontsize=16, fontweight='bold')
    
    # 1. 各交易所交易量对比
    ax1 = axes[0, 0]
    exchange_volumes = volume_data.groupby('Exchange')['Volume_USD_Millions'].sum().sort_values(ascending=True)
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    exchange_volumes.plot(kind='barh', ax=ax1, color=colors)
    ax1.set_title('各交易所9月1-24日ETH交易量总计', fontweight='bold')
    ax1.set_xlabel('交易量 (百万美元)')
    ax1.grid(True, alpha=0.3)
    
    # 2. 每日总交易量趋势
    ax2 = axes[0, 1]
    daily_volume = volume_data.groupby('Date')['Volume_USD_Millions'].sum()
    daily_volume.plot(ax=ax2, marker='o', linewidth=2, markersize=6, color='#FF6B6B')
    ax2.set_title('每日ETH总交易量趋势', fontweight='bold')
    ax2.set_ylabel('交易量 (百万美元)')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    # 3. 价格走势和预测
    ax3 = axes[1, 0]
    ax3.plot(price_data['Date'], price_data['Close'], linewidth=2, color='#2E86AB', label='历史价格')
    ax3.plot(predictions['Date'], predictions['Close'], linewidth=2, color='#E17055', linestyle='--', label='预测价格')
    ax3.fill_between(price_data['Date'], price_data['Low'], price_data['High'], 
                    alpha=0.3, color='#2E86AB', label='历史价格区间')
    ax3.fill_between(predictions['Date'], predictions['Low'], predictions['High'], 
                    alpha=0.3, color='#E17055', label='预测价格区间')
    ax3.set_title('ETH价格走势和预测 (9月1-29日)', fontweight='bold')
    ax3.set_ylabel('价格 (USD)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    # 4. 交易量vs价格相关性
    ax4 = axes[1, 1]
    daily_summary = volume_data.groupby('Date')['Volume_USD_Millions'].sum()
    price_volume = pd.merge(price_data[['Date', 'Close']], 
                           daily_summary.reset_index(), on='Date')
    ax4.scatter(price_volume['Volume_USD_Millions'], price_volume['Close'], 
               alpha=0.7, s=60, color='#E17055')
    ax4.set_title('交易量与价格相关性', fontweight='bold')
    ax4.set_xlabel('日交易量 (百万美元)')
    ax4.set_ylabel('ETH价格 (USD)')
    ax4.grid(True, alpha=0.3)
    
    # 计算相关系数
    correlation = price_volume['Volume_USD_Millions'].corr(price_volume['Close'])
    ax4.text(0.05, 0.95, f'相关系数: {correlation:.3f}', 
            transform=ax4.transAxes, bbox=dict(boxstyle="round", facecolor='wheat'))
    
    plt.tight_layout()
    plt.savefig('/workspace/eth_analysis_charts.png', dpi=300, bbox_inches='tight')
    print("✅ 图表已保存为 eth_analysis_charts.png")
    
    # 创建单独的K线预测图表
    fig2, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 绘制历史价格
    ax.plot(price_data['Date'], price_data['Close'], linewidth=2, color='#2E86AB', label='历史价格')
    ax.fill_between(price_data['Date'], price_data['Low'], price_data['High'], 
                   alpha=0.3, color='#2E86AB', label='历史价格区间')
    
    # 绘制预测价格
    ax.plot(predictions['Date'], predictions['Close'], linewidth=3, color='#E17055', 
           linestyle='--', marker='o', markersize=8, label='预测价格')
    ax.fill_between(predictions['Date'], predictions['Low'], predictions['High'], 
                   alpha=0.3, color='#E17055', label='预测价格区间')
    
    # 添加预测信心标注
    for i, row in predictions.iterrows():
        ax.annotate(f'{row["Prediction_Confidence"]:.0f}%', 
                   xy=(row['Date'], row['Close']), 
                   xytext=(5, 5), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                   fontsize=8)
    
    ax.set_title('ETH价格走势和9月25-29日K线预测', fontsize=14, fontweight='bold')
    ax.set_xlabel('日期')
    ax.set_ylabel('价格 (USD)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    plt.tight_layout()
    plt.savefig('/workspace/eth_kline_prediction.png', dpi=300, bbox_inches='tight')
    print("✅ K线预测图表已保存为 eth_kline_prediction.png")

if __name__ == "__main__":
    create_visualizations()