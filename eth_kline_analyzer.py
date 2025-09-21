#!/usr/bin/env python3
"""
ETH交易量分析与K线图推算工具
基于ETH一周交易量数据，推算最合理的K线图周期
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import seaborn as sns
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ETHKlineAnalyzer:
    def __init__(self):
        self.eth_data = None
        self.volume_data = None
        
    def generate_realistic_eth_data(self) -> pd.DataFrame:
        """
        基于实际ETH价格和交易量特征生成模拟数据
        价格范围: 3000-4500 USD
        交易量范围: 10-50亿美元/天
        """
        # 生成过去7天的数据
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), 
                             end=datetime.now(), freq='D')
        
        # 基础价格趋势（从3000上涨到4500）
        base_prices = np.linspace(3000, 4500, len(dates))
        
        # 添加随机波动
        price_volatility = np.random.normal(0, 50, len(dates))
        prices = base_prices + price_volatility
        
        # 生成OHLC数据
        data = []
        for i, (date, base_price) in enumerate(zip(dates, prices)):
            # 日内波动范围
            daily_range = np.random.uniform(20, 100)
            
            # 开盘价
            open_price = base_price + np.random.uniform(-daily_range/2, daily_range/2)
            
            # 最高价和最低价
            high_price = open_price + np.random.uniform(0, daily_range)
            low_price = open_price - np.random.uniform(0, daily_range)
            
            # 收盘价（基于趋势）
            close_price = open_price + np.random.uniform(-daily_range/2, daily_range/2)
            
            # 交易量（与价格波动相关）
            volume_base = np.random.uniform(1.5, 4.5)  # 15-45亿美元
            price_change_pct = abs(close_price - open_price) / open_price
            volume_multiplier = 1 + price_change_pct * 2  # 价格变化越大，交易量越大
            volume = volume_base * volume_multiplier
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': round(volume, 2)
            })
        
        return pd.DataFrame(data)
    
    def calculate_optimal_timeframe(self, data: pd.DataFrame) -> Dict:
        """
        基于交易量分析计算最优K线图时间周期
        """
        # 计算价格波动率
        data['price_change'] = data['close'].pct_change()
        data['volatility'] = data['price_change'].rolling(window=2).std()
        
        # 计算交易量特征
        avg_volume = data['volume'].mean()
        volume_std = data['volume'].std()
        volume_cv = volume_std / avg_volume  # 变异系数
        
        # 计算价格趋势强度
        price_trend = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]
        
        # 基于交易量特征推荐时间周期
        recommendations = {}
        
        if volume_cv < 0.3:  # 交易量稳定
            if abs(price_trend) > 0.1:  # 强趋势
                recommendations['primary'] = '4H'
                recommendations['secondary'] = '1D'
                recommendations['reason'] = '交易量稳定且趋势明显，适合4小时和日线图'
            else:
                recommendations['primary'] = '1H'
                recommendations['secondary'] = '4H'
                recommendations['reason'] = '交易量稳定但趋势平缓，适合小时图'
        elif volume_cv < 0.6:  # 交易量中等波动
            recommendations['primary'] = '1H'
            recommendations['secondary'] = '4H'
            recommendations['reason'] = '交易量中等波动，小时图能更好捕捉机会'
        else:  # 交易量高波动
            recommendations['primary'] = '15M'
            recommendations['secondary'] = '1H'
            recommendations['reason'] = '交易量波动较大，短周期图更适合'
        
        # 添加分析指标
        analysis = {
            'avg_volume': round(avg_volume, 2),
            'volume_volatility': round(volume_cv, 3),
            'price_trend': round(price_trend * 100, 2),
            'recommendations': recommendations
        }
        
        return analysis
    
    def plot_kline_chart(self, data: pd.DataFrame, timeframe: str = '1D'):
        """
        绘制K线图
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), 
                                      gridspec_kw={'height_ratios': [3, 1]})
        
        # K线图
        for i, row in data.iterrows():
            color = 'red' if row['close'] >= row['open'] else 'green'
            
            # 绘制影线
            ax1.plot([i, i], [row['low'], row['high']], color='black', linewidth=1)
            
            # 绘制实体
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['open'], row['close'])
            
            rect = plt.Rectangle((i-0.3, body_bottom), 0.6, body_height, 
                               facecolor=color, alpha=0.7, edgecolor='black')
            ax1.add_patch(rect)
        
        ax1.set_title(f'ETH K线图 - {timeframe}周期', fontsize=16, fontweight='bold')
        ax1.set_ylabel('价格 (USD)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 设置x轴标签
        ax1.set_xticks(range(len(data)))
        ax1.set_xticklabels([d.strftime('%m-%d') for d in data['date']], rotation=45)
        
        # 交易量图
        ax2.bar(range(len(data)), data['volume'], color='skyblue', alpha=0.7)
        ax2.set_title('交易量 (十亿美元)', fontsize=12)
        ax2.set_ylabel('交易量', fontsize=10)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 设置x轴标签
        ax2.set_xticks(range(len(data)))
        ax2.set_xticklabels([d.strftime('%m-%d') for d in data['date']], rotation=45)
        
        plt.tight_layout()
        return fig
    
    def generate_analysis_report(self, data: pd.DataFrame) -> str:
        """
        生成分析报告
        """
        analysis = self.calculate_optimal_timeframe(data)
        
        report = f"""
=== ETH交易量分析与K线图周期推荐报告 ===

📊 数据概览:
- 分析周期: 7天
- 平均日交易量: {analysis['avg_volume']} 十亿美元
- 交易量波动率: {analysis['volume_volatility']:.1%}
- 价格趋势: {analysis['price_trend']:+.1f}%

🎯 推荐K线图周期:
- 主要周期: {analysis['recommendations']['primary']}
- 辅助周期: {analysis['recommendations']['secondary']}
- 推荐理由: {analysis['recommendations']['reason']}

📈 技术分析建议:
1. 基于当前交易量特征，建议使用{analysis['recommendations']['primary']}周期进行主要分析
2. 结合{analysis['recommendations']['secondary']}周期确认趋势方向
3. 交易量波动率{analysis['volume_volatility']:.1%}，市场活跃度{'较高' if analysis['volume_volatility'] > 0.4 else '适中'}

⚠️ 风险提示:
- 加密货币市场波动性较大，请谨慎投资
- 建议结合基本面分析和技术指标
- 设置合理的止损和止盈位
        """
        
        return report
    
    def run_analysis(self):
        """
        运行完整分析
        """
        print("🚀 开始ETH交易量分析...")
        
        # 生成数据
        self.eth_data = self.generate_realistic_eth_data()
        print("✅ 数据生成完成")
        
        # 计算最优时间周期
        analysis = self.calculate_optimal_timeframe(self.eth_data)
        print("✅ 时间周期分析完成")
        
        # 生成报告
        report = self.generate_analysis_report(self.eth_data)
        print(report)
        
        # 绘制图表
        fig = self.plot_kline_chart(self.eth_data, analysis['recommendations']['primary'])
        plt.savefig('/workspace/eth_kline_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ 图表已保存为 eth_kline_analysis.png")
        
        return self.eth_data, analysis

if __name__ == "__main__":
    analyzer = ETHKlineAnalyzer()
    data, analysis = analyzer.run_analysis()