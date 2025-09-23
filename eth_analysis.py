#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
以太坊(ETH)交易量分析和K线走势预测
Ethereum Trading Volume Analysis and K-line Trend Prediction
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class EthereumAnalyzer:
    def __init__(self):
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_eth_historical_data(self, days=15):
        """获取ETH历史数据"""
        try:
            # 获取过去15天的数据
            url = f"{self.coingecko_base_url}/coins/ethereum/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 处理数据
            prices = data['prices']
            volumes = data['total_volumes']
            market_caps = data['market_caps']
            
            # 创建DataFrame
            df = pd.DataFrame({
                'timestamp': [datetime.fromtimestamp(price[0]/1000) for price in prices],
                'price': [price[1] for price in prices],
                'volume': [vol[1] for vol in volumes],
                'market_cap': [cap[1] for cap in market_caps]
            })
            
            # 计算OHLC数据（简化版，使用收盘价作为OHLC）
            df['open'] = df['price'].shift(1)
            df['high'] = df['price'] * (1 + np.random.uniform(0, 0.05, len(df)))  # 模拟最高价
            df['low'] = df['price'] * (1 - np.random.uniform(0, 0.05, len(df)))   # 模拟最低价
            df['close'] = df['price']
            
            return df.dropna()
            
        except Exception as e:
            print(f"获取数据时出错: {e}")
            return self.generate_mock_data(days)
    
    def generate_mock_data(self, days=15):
        """生成模拟数据（当API不可用时）"""
        print("使用模拟数据进行演示...")
        
        # 基于当前ETH价格生成模拟数据
        base_price = 4170.79
        dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
        
        # 生成价格数据（带趋势和随机波动）
        trend = np.linspace(0, 0.1, days)  # 轻微上升趋势
        noise = np.random.normal(0, 0.02, days)  # 2%的随机波动
        prices = base_price * (1 + trend + noise)
        
        # 生成交易量数据
        base_volume = 15_000_000_000  # 150亿美元基础交易量
        volume_noise = np.random.uniform(0.5, 2.0, days)
        volumes = base_volume * volume_noise
        
        df = pd.DataFrame({
            'timestamp': dates,
            'price': prices,
            'volume': volumes,
            'market_cap': prices * 120_000_000,  # 假设1.2亿ETH流通量
            'open': np.roll(prices, 1),
            'high': prices * (1 + np.random.uniform(0, 0.03, days)),
            'low': prices * (1 - np.random.uniform(0, 0.03, days)),
            'close': prices
        })
        
        df['open'].iloc[0] = df['close'].iloc[0]  # 第一天开盘价等于收盘价
        
        return df
    
    def calculate_technical_indicators(self, df):
        """计算技术指标"""
        # 移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # 布林带
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        return df
    
    def predict_future_trend(self, df, days=5):
        """预测未来K线走势"""
        # 使用多种方法进行预测
        
        # 1. 基于移动平均的趋势
        recent_ma5 = df['MA5'].iloc[-1]
        recent_ma10 = df['MA10'].iloc[-1]
        recent_ma20 = df['MA20'].iloc[-1]
        
        # 2. 基于RSI的超买超卖判断
        current_rsi = df['RSI'].iloc[-1]
        
        # 3. 基于MACD的趋势判断
        current_macd = df['MACD'].iloc[-1]
        current_macd_signal = df['MACD_signal'].iloc[-1]
        
        # 4. 基于布林带的位置
        current_price = df['close'].iloc[-1]
        bb_upper = df['BB_upper'].iloc[-1]
        bb_lower = df['BB_lower'].iloc[-1]
        bb_middle = df['BB_middle'].iloc[-1]
        
        # 计算趋势强度
        trend_strength = 0
        
        # MA趋势判断
        if recent_ma5 > recent_ma10 > recent_ma20:
            trend_strength += 1
        elif recent_ma5 < recent_ma10 < recent_ma20:
            trend_strength -= 1
        
        # RSI判断
        if current_rsi < 30:  # 超卖
            trend_strength += 0.5
        elif current_rsi > 70:  # 超买
            trend_strength -= 0.5
        
        # MACD判断
        if current_macd > current_macd_signal:
            trend_strength += 0.5
        else:
            trend_strength -= 0.5
        
        # 布林带位置判断
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        if bb_position < 0.2:  # 接近下轨
            trend_strength += 0.3
        elif bb_position > 0.8:  # 接近上轨
            trend_strength -= 0.3
        
        # 生成未来5天的预测
        future_dates = [datetime.now() + timedelta(days=i+1) for i in range(days)]
        predictions = []
        
        # 基础价格变化率
        base_change_rate = 0.001  # 0.1%的基础变化率
        
        for i in range(days):
            # 根据趋势强度调整变化率
            if trend_strength > 0:
                change_rate = base_change_rate + trend_strength * 0.002
            else:
                change_rate = base_change_rate + trend_strength * 0.002
            
            # 添加随机波动
            random_factor = np.random.normal(0, 0.02)
            change_rate += random_factor
            
            # 计算预测价格
            if i == 0:
                pred_price = current_price * (1 + change_rate)
            else:
                pred_price = predictions[-1]['close'] * (1 + change_rate)
            
            # 生成OHLC数据
            volatility = 0.02  # 2%的日内波动
            high = pred_price * (1 + np.random.uniform(0, volatility))
            low = pred_price * (1 - np.random.uniform(0, volatility))
            open_price = predictions[-1]['close'] if i > 0 else current_price
            
            predictions.append({
                'timestamp': future_dates[i],
                'open': open_price,
                'high': high,
                'low': low,
                'close': pred_price,
                'volume': np.random.uniform(10_000_000_000, 25_000_000_000)  # 模拟交易量
            })
        
        return pd.DataFrame(predictions)
    
    def plot_analysis(self, historical_df, predictions_df):
        """绘制分析图表"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 价格和移动平均线
        ax1.plot(historical_df['timestamp'], historical_df['close'], label='收盘价', linewidth=2)
        ax1.plot(historical_df['timestamp'], historical_df['MA5'], label='MA5', alpha=0.7)
        ax1.plot(historical_df['timestamp'], historical_df['MA10'], label='MA10', alpha=0.7)
        ax1.plot(historical_df['timestamp'], historical_df['MA20'], label='MA20', alpha=0.7)
        
        # 预测数据
        ax1.plot(predictions_df['timestamp'], predictions_df['close'], 
                label='预测价格', linewidth=2, linestyle='--', color='red')
        
        ax1.set_title('ETH价格走势和移动平均线', fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格 (USD)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 交易量
        ax2.bar(historical_df['timestamp'], historical_df['volume']/1e9, 
               alpha=0.7, label='历史交易量')
        ax2.bar(predictions_df['timestamp'], predictions_df['volume']/1e9, 
               alpha=0.7, color='red', label='预测交易量')
        
        ax2.set_title('ETH交易量 (过去15天 + 未来5天预测)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('交易量 (十亿美元)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. RSI指标
        ax3.plot(historical_df['timestamp'], historical_df['RSI'], label='RSI', color='purple')
        ax3.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='超买线(70)')
        ax3.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='超卖线(30)')
        ax3.axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='中线(50)')
        
        ax3.set_title('RSI相对强弱指标', fontsize=14, fontweight='bold')
        ax3.set_ylabel('RSI')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. MACD指标
        ax4.plot(historical_df['timestamp'], historical_df['MACD'], label='MACD', color='blue')
        ax4.plot(historical_df['timestamp'], historical_df['MACD_signal'], label='MACD信号线', color='red')
        ax4.bar(historical_df['timestamp'], historical_df['MACD_histogram'], 
               label='MACD柱状图', alpha=0.6, color='gray')
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        ax4.set_title('MACD指标', fontsize=14, fontweight='bold')
        ax4.set_ylabel('MACD')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 设置x轴日期格式
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig('/workspace/eth_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_analysis_summary(self, historical_df, predictions_df):
        """打印分析摘要"""
        print("=" * 60)
        print("以太坊(ETH)交易量分析和K线走势预测")
        print("=" * 60)
        
        # 过去15天交易量统计
        print("\n📊 过去15天交易量统计:")
        print(f"平均日交易量: ${historical_df['volume'].mean()/1e9:.2f} 十亿美元")
        print(f"最高日交易量: ${historical_df['volume'].max()/1e9:.2f} 十亿美元")
        print(f"最低日交易量: ${historical_df['volume'].min()/1e9:.2f} 十亿美元")
        print(f"交易量标准差: ${historical_df['volume'].std()/1e9:.2f} 十亿美元")
        
        # 价格统计
        print(f"\n💰 价格统计:")
        print(f"当前价格: ${historical_df['close'].iloc[-1]:.2f}")
        print(f"15天最高价: ${historical_df['close'].max():.2f}")
        print(f"15天最低价: ${historical_df['close'].min():.2f}")
        print(f"15天涨跌幅: {((historical_df['close'].iloc[-1] / historical_df['close'].iloc[0]) - 1) * 100:.2f}%")
        
        # 技术指标
        print(f"\n📈 技术指标分析:")
        print(f"当前RSI: {historical_df['RSI'].iloc[-1]:.2f}")
        print(f"当前MACD: {historical_df['MACD'].iloc[-1]:.4f}")
        print(f"MA5: ${historical_df['MA5'].iloc[-1]:.2f}")
        print(f"MA10: ${historical_df['MA10'].iloc[-1]:.2f}")
        print(f"MA20: ${historical_df['MA20'].iloc[-1]:.2f}")
        
        # 未来5天预测
        print(f"\n🔮 未来5天K线走势预测:")
        for i, row in predictions_df.iterrows():
            change_pct = ((row['close'] / historical_df['close'].iloc[-1]) - 1) * 100
            print(f"第{i+1}天 ({row['timestamp'].strftime('%m-%d')}): "
                  f"开盘${row['open']:.2f} 最高${row['high']:.2f} "
                  f"最低${row['low']:.2f} 收盘${row['close']:.2f} "
                  f"({change_pct:+.2f}%)")
        
        # 趋势判断
        print(f"\n🎯 趋势判断:")
        current_rsi = historical_df['RSI'].iloc[-1]
        current_macd = historical_df['MACD'].iloc[-1]
        current_macd_signal = historical_df['MACD_signal'].iloc[-1]
        
        if current_rsi < 30:
            print("RSI显示超卖状态，可能存在反弹机会")
        elif current_rsi > 70:
            print("RSI显示超买状态，需要谨慎")
        else:
            print("RSI处于正常区间")
        
        if current_macd > current_macd_signal:
            print("MACD显示上升趋势")
        else:
            print("MACD显示下降趋势")
        
        print(f"\n⚠️  风险提示:")
        print("1. 加密货币市场波动性极大，预测仅供参考")
        print("2. 技术分析不能保证未来走势的准确性")
        print("3. 投资有风险，请根据自身风险承受能力谨慎决策")
        print("4. 建议结合基本面分析和市场消息进行综合判断")

def main():
    """主函数"""
    analyzer = EthereumAnalyzer()
    
    print("正在获取ETH历史数据...")
    historical_data = analyzer.get_eth_historical_data(15)
    
    print("正在计算技术指标...")
    historical_data = analyzer.calculate_technical_indicators(historical_data)
    
    print("正在预测未来5天走势...")
    predictions = analyzer.predict_future_trend(historical_data, 5)
    
    print("正在生成分析图表...")
    analyzer.plot_analysis(historical_data, predictions)
    
    print("正在生成分析报告...")
    analyzer.print_analysis_summary(historical_data, predictions)
    
    # 保存数据到CSV
    historical_data.to_csv('/workspace/eth_historical_data.csv', index=False)
    predictions.to_csv('/workspace/eth_predictions.csv', index=False)
    print(f"\n数据已保存到:")
    print(f"- 历史数据: /workspace/eth_historical_data.csv")
    print(f"- 预测数据: /workspace/eth_predictions.csv")
    print(f"- 分析图表: /workspace/eth_analysis.png")

if __name__ == "__main__":
    main()