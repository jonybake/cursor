#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
凯利指数详细分析报告
Kelly Index Detailed Analysis Report
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_detailed_kelly_report():
    """创建详细的凯利指数分析报告"""
    
    # 读取数据
    exchange_data = pd.read_csv('/workspace/eth_exchange_data.csv')
    kelly_data = pd.read_csv('/workspace/eth_kelly_index.csv', index_col=0)
    
    print("=" * 100)
    print("ETH各大交易所凯利指数详细分析报告")
    print("=" * 100)
    
    # 1. 凯利公式理论基础
    print("\n📚 凯利公式理论基础:")
    print("-" * 50)
    print("凯利公式: f* = (bp - q) / b")
    print("其中:")
    print("  f* = 建议的资金投入比例")
    print("  b  = 赔率 (平均盈利/平均亏损)")
    print("  p  = 获胜概率 (上涨概率)")
    print("  q  = 失败概率 (下跌概率) = 1 - p")
    print("\n凯利公式的意义:")
    print("• 当 f* > 0 时，建议投资")
    print("• 当 f* = 0 时，盈亏平衡")
    print("• 当 f* < 0 时，不建议投资")
    print("• f* 值越大，投资价值越高")
    
    # 2. 各交易所详细分析
    print(f"\n📊 各交易所详细凯利指数分析:")
    print("-" * 50)
    
    for exchange in kelly_data.index:
        stats = kelly_data.loc[exchange]
        
        print(f"\n🔸 {exchange} 交易所:")
        print(f"  数据期间: 14个交易日")
        print(f"  上涨天数: {int(stats['up_days'])} 天 ({stats['p_win']:.1%})")
        print(f"  下跌天数: {int(stats['down_days'])} 天 ({stats['p_loss']:.1%})")
        print(f"  平均上涨幅度: {stats['avg_up_return']:.2%}")
        print(f"  平均下跌幅度: {stats['avg_down_return']:.2%}")
        print(f"  赔率 (b): {stats['odds_ratio']:.3f}")
        print(f"  原始凯利指数: {stats['kelly_fraction']:.3f}")
        print(f"  风险调整凯利指数: {stats['risk_adjusted_kelly']:.3f}")
        
        # 凯利指数解释
        kelly_val = stats['risk_adjusted_kelly']
        if kelly_val > 0.15:
            interpretation = "极佳投资机会"
            recommendation = "强烈建议投资"
        elif kelly_val > 0.10:
            interpretation = "良好投资机会"
            recommendation = "建议投资"
        elif kelly_val > 0.05:
            interpretation = "一般投资机会"
            recommendation = "谨慎投资"
        elif kelly_val > 0:
            interpretation = "微弱投资机会"
            recommendation = "少量投资"
        else:
            interpretation = "无投资价值"
            recommendation = "不建议投资"
        
        print(f"  投资价值评估: {interpretation}")
        print(f"  投资建议: {recommendation}")
        
        # 风险分析
        if stats['odds_ratio'] > 1.2:
            risk_level = "低风险"
        elif stats['odds_ratio'] > 0.8:
            risk_level = "中等风险"
        else:
            risk_level = "高风险"
        
        print(f"  风险等级: {risk_level}")
        print(f"  建议投注比例: {kelly_val:.1%}")
    
    # 3. 综合对比分析
    print(f"\n📈 综合对比分析:")
    print("-" * 50)
    
    # 按凯利指数排序
    sorted_exchanges = kelly_data.sort_values('risk_adjusted_kelly', ascending=False)
    
    print("按凯利指数排序的投资优先级:")
    for i, (exchange, stats) in enumerate(sorted_exchanges.iterrows(), 1):
        print(f"  {i}. {exchange}: {stats['risk_adjusted_kelly']:.3f}")
    
    # 最佳和最差选择
    best = sorted_exchanges.iloc[0]
    worst = sorted_exchanges.iloc[-1]
    
    print(f"\n🏆 最佳投资选择: {best.name}")
    print(f"   凯利指数: {best['risk_adjusted_kelly']:.3f}")
    print(f"   上涨概率: {best['p_win']:.1%}")
    print(f"   赔率: {best['odds_ratio']:.2f}")
    
    print(f"\n⚠️  风险最高选择: {worst.name}")
    print(f"   凯利指数: {worst['risk_adjusted_kelly']:.3f}")
    print(f"   上涨概率: {worst['p_win']:.1%}")
    print(f"   赔率: {worst['odds_ratio']:.2f}")
    
    # 4. 市场整体分析
    print(f"\n🌍 市场整体分析:")
    print("-" * 50)
    
    avg_kelly = kelly_data['risk_adjusted_kelly'].mean()
    median_kelly = kelly_data['risk_adjusted_kelly'].median()
    std_kelly = kelly_data['risk_adjusted_kelly'].std()
    
    print(f"平均凯利指数: {avg_kelly:.3f}")
    print(f"中位数凯利指数: {median_kelly:.3f}")
    print(f"凯利指数标准差: {std_kelly:.3f}")
    
    # 市场整体评估
    if avg_kelly > 0.10:
        market_sentiment = "积极"
        market_recommendation = "市场整体投资机会良好"
    elif avg_kelly > 0.05:
        market_sentiment = "中性"
        market_recommendation = "市场整体投资机会一般"
    else:
        market_sentiment = "消极"
        market_recommendation = "市场整体投资风险较高"
    
    print(f"市场整体情绪: {market_sentiment}")
    print(f"市场整体建议: {market_recommendation}")
    
    # 5. 投资策略建议
    print(f"\n💡 投资策略建议:")
    print("-" * 50)
    
    print("基于凯利指数的投资策略:")
    print("1. 资金分配策略:")
    print(f"   • 将总资金的 {best['risk_adjusted_kelly']:.1%} 投资于 {best.name}")
    
    # 计算其他交易所的投资比例
    other_exchanges = sorted_exchanges[sorted_exchanges['risk_adjusted_kelly'] > 0]
    if len(other_exchanges) > 1:
        remaining_capital = 1 - best['risk_adjusted_kelly']
        other_avg_kelly = other_exchanges.iloc[1:]['risk_adjusted_kelly'].mean()
        other_allocation = min(remaining_capital * 0.5, other_avg_kelly)
        print(f"   • 将总资金的 {other_allocation:.1%} 分散投资于其他交易所")
    
    print("2. 风险控制策略:")
    print("   • 使用分数凯利 (如1/2凯利) 来降低风险")
    print("   • 设置止损点，避免过度损失")
    print("   • 定期重新评估凯利指数")
    
    print("3. 监控指标:")
    print("   • 密切关注上涨概率变化")
    print("   • 监控赔率变化")
    print("   • 观察交易量变化趋势")
    
    # 6. 风险提示
    print(f"\n⚠️  重要风险提示:")
    print("-" * 50)
    print("1. 凯利指数基于历史数据，不保证未来表现")
    print("2. 加密货币市场波动性极大，存在重大损失风险")
    print("3. 建议使用保守的凯利分数 (如1/2或1/3凯利)")
    print("4. 投资前请充分了解相关风险")
    print("5. 建议咨询专业投资顾问")
    print("6. 不要投入超过承受能力的资金")
    
    # 7. 技术说明
    print(f"\n🔧 技术说明:")
    print("-" * 50)
    print("• 数据来源: 模拟数据 (基于真实市场特征)")
    print("• 计算期间: 过去14个交易日")
    print("• 风险调整: 将凯利指数限制在0-25%之间")
    print("• 更新频率: 建议每日更新")
    print("• 计算方法: 标准凯利公式")
    
    print("\n" + "=" * 100)
    print("报告生成时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 100)

def create_kelly_visualization():
    """创建凯利指数可视化图表"""
    
    # 读取数据
    kelly_data = pd.read_csv('/workspace/eth_kelly_index.csv', index_col=0)
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 凯利指数对比
    exchanges = kelly_data.index
    kelly_values = kelly_data['risk_adjusted_kelly']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    bars = ax1.bar(exchanges, kelly_values, color=colors, alpha=0.8)
    ax1.set_title('各交易所凯利指数对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('凯利指数')
    ax1.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bar, value in zip(bars, kelly_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. 涨跌概率对比
    win_probs = kelly_data['p_win']
    loss_probs = kelly_data['p_loss']
    
    x = np.arange(len(exchanges))
    width = 0.35
    
    ax2.bar(x - width/2, win_probs, width, label='上涨概率', alpha=0.8, color='#2ECC71')
    ax2.bar(x + width/2, loss_probs, width, label='下跌概率', alpha=0.8, color='#E74C3C')
    
    ax2.set_title('各交易所涨跌概率对比', fontsize=14, fontweight='bold')
    ax2.set_ylabel('概率')
    ax2.set_xticks(x)
    ax2.set_xticklabels(exchanges)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 赔率对比
    odds_ratios = kelly_data['odds_ratio']
    bars = ax3.bar(exchanges, odds_ratios, color=colors, alpha=0.8)
    ax3.set_title('各交易所赔率对比', fontsize=14, fontweight='bold')
    ax3.set_ylabel('赔率 (平均盈利/平均亏损)')
    ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='盈亏平衡线')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bar, value in zip(bars, odds_ratios):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 4. 投资建议雷达图
    categories = ['凯利指数', '上涨概率', '赔率', '风险控制']
    
    # 标准化数据用于雷达图
    kelly_norm = kelly_values / kelly_values.max()
    win_prob_norm = win_probs
    odds_norm = odds_ratios / odds_ratios.max()
    risk_norm = 1 - (kelly_data['volume_std'] / kelly_data['volume_std'].max())
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合图形
    
    ax4 = plt.subplot(2, 2, 4, projection='polar')
    
    for i, exchange in enumerate(exchanges):
        values = [kelly_norm.iloc[i], win_prob_norm.iloc[i], odds_norm.iloc[i], risk_norm.iloc[i]]
        values += values[:1]  # 闭合图形
        
        ax4.plot(angles, values, 'o-', linewidth=2, label=exchange, color=colors[i])
        ax4.fill(angles, values, alpha=0.25, color=colors[i])
    
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(categories)
    ax4.set_title('综合投资评估雷达图', fontsize=14, fontweight='bold', pad=20)
    ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig('/workspace/kelly_detailed_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    create_detailed_kelly_report()
    create_kelly_visualization()