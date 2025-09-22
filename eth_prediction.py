#!/usr/bin/env python3
"""
ETH价格预测脚本
根据一周的历史交易量数据预测未来3天的K线
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ETHPredictor:
    def __init__(self):
        self.data = None
        self.predictions = None
        
    def fetch_data(self, days=7):
        """获取ETH历史数据"""
        print("正在获取ETH历史数据...")
        
        # 获取最近一周的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            # 使用yfinance获取ETH数据
            ticker = yf.Ticker("ETH-USD")
            self.data = ticker.history(start=start_date, end=end_date, interval="1h")
            
            if self.data.empty:
                print("无法获取数据，尝试使用备用方法...")
                # 备用方法：生成模拟数据
                self.generate_mock_data(days)
            else:
                print(f"成功获取 {len(self.data)} 条数据")
                
        except Exception as e:
            print(f"获取数据失败: {e}")
            print("使用模拟数据进行演示...")
            self.generate_mock_data(days)
    
    def generate_mock_data(self, days=7):
        """生成模拟的ETH数据用于演示"""
        print("生成模拟ETH数据...")
        
        # 生成时间序列
        hours = days * 24
        timestamps = pd.date_range(start=datetime.now() - timedelta(days=days), 
                                 periods=hours, freq='H')
        
        # 模拟价格数据（基于随机游走）
        np.random.seed(42)  # 确保结果可重现
        base_price = 3000  # 基础价格
        price_changes = np.random.normal(0, 0.02, hours)  # 2%的波动率
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        # 生成成交量数据
        volumes = np.random.lognormal(15, 0.5, hours)  # 对数正态分布
        
        # 计算OHLC数据
        data = []
        for i in range(0, hours, 24):  # 每天24小时
            daily_prices = prices[i:i+24]
            daily_volumes = volumes[i:i+24]
            
            for j in range(24):
                if i + j < hours:
                    # 模拟小时内的价格波动
                    hour_open = daily_prices[j]
                    hour_high = hour_open * (1 + abs(np.random.normal(0, 0.01)))
                    hour_low = hour_open * (1 - abs(np.random.normal(0, 0.01)))
                    hour_close = hour_open * (1 + np.random.normal(0, 0.005))
                    hour_volume = daily_volumes[j]
                    
                    data.append({
                        'Open': hour_open,
                        'High': hour_high,
                        'Low': hour_low,
                        'Close': hour_close,
                        'Volume': hour_volume
                    })
        
        self.data = pd.DataFrame(data, index=timestamps[:len(data)])
        print(f"生成了 {len(self.data)} 条模拟数据")
    
    def analyze_data(self):
        """分析历史数据特征"""
        print("\n=== 数据分析 ===")
        
        if self.data is None or self.data.empty:
            print("没有数据可供分析")
            return
        
        # 基本统计信息
        print(f"数据时间范围: {self.data.index[0]} 到 {self.data.index[-1]}")
        print(f"数据点数: {len(self.data)}")
        
        # 价格统计
        print(f"\n价格统计:")
        print(f"最高价: ${self.data['High'].max():.2f}")
        print(f"最低价: ${self.data['Low'].min():.2f}")
        print(f"平均价: ${self.data['Close'].mean():.2f}")
        print(f"价格波动率: {self.data['Close'].pct_change().std()*100:.2f}%")
        
        # 成交量统计
        print(f"\n成交量统计:")
        print(f"平均成交量: {self.data['Volume'].mean():.0f}")
        print(f"最大成交量: {self.data['Volume'].max():.0f}")
        print(f"成交量波动率: {self.data['Volume'].pct_change().std()*100:.2f}%")
        
        # 计算技术指标
        self.calculate_technical_indicators()
    
    def calculate_technical_indicators(self):
        """计算技术指标"""
        print("\n=== 技术指标 ===")
        
        # 移动平均线
        self.data['MA5'] = self.data['Close'].rolling(window=5).mean()
        self.data['MA20'] = self.data['Close'].rolling(window=20).mean()
        
        # RSI
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = self.data['Close'].ewm(span=12).mean()
        exp2 = self.data['Close'].ewm(span=26).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['MACD_signal'] = self.data['MACD'].ewm(span=9).mean()
        
        print(f"当前RSI: {self.data['RSI'].iloc[-1]:.2f}")
        print(f"当前MACD: {self.data['MACD'].iloc[-1]:.4f}")
    
    def predict_future(self, days=3):
        """预测未来价格"""
        print(f"\n=== 预测未来{days}天 ===")
        
        if self.data is None or self.data.empty:
            print("没有数据可供预测")
            return
        
        # 使用多种方法进行预测
        predictions = {}
        
        # 方法1: 简单移动平均趋势
        recent_trend = self.data['Close'].tail(24).pct_change().mean()  # 最近24小时平均变化率
        last_price = self.data['Close'].iloc[-1]
        
        # 方法2: 基于成交量的价格预测
        volume_trend = self.data['Volume'].tail(24).pct_change().mean()
        price_volume_correlation = self.data['Close'].pct_change().corr(self.data['Volume'].pct_change())
        
        # 方法3: 基于技术指标的预测
        rsi = self.data['RSI'].iloc[-1]
        macd = self.data['MACD'].iloc[-1]
        
        # 生成未来3天的预测
        future_dates = pd.date_range(start=self.data.index[-1] + timedelta(hours=1), 
                                   periods=days*24, freq='H')
        
        predicted_prices = []
        predicted_volumes = []
        current_price = last_price
        
        for i, future_date in enumerate(future_dates):
            # 综合多种因素调整价格
            trend_factor = 1 + recent_trend
            volume_factor = 1 + (volume_trend * price_volume_correlation * 0.1)
            
            # RSI调整
            if rsi > 70:  # 超买
                rsi_factor = 0.999
            elif rsi < 30:  # 超卖
                rsi_factor = 1.001
            else:
                rsi_factor = 1.0
            
            # MACD调整
            if macd > 0:
                macd_factor = 1.001
            else:
                macd_factor = 0.999
            
            # 随机波动
            random_factor = 1 + np.random.normal(0, 0.01)
            
            # 计算新价格
            new_price = current_price * trend_factor * volume_factor * rsi_factor * macd_factor * random_factor
            
            # 计算OHLC
            price_change = new_price - current_price
            high = max(current_price, new_price) * (1 + abs(np.random.normal(0, 0.005)))
            low = min(current_price, new_price) * (1 - abs(np.random.normal(0, 0.005)))
            
            # 预测成交量
            base_volume = self.data['Volume'].tail(24).mean()
            volume_factor = 1 + np.random.normal(0, 0.2)
            predicted_volume = base_volume * volume_factor
            
            predicted_prices.append({
                'datetime': future_date,
                'Open': current_price,
                'High': high,
                'Low': low,
                'Close': new_price,
                'Volume': predicted_volume
            })
            
            current_price = new_price
        
        self.predictions = pd.DataFrame(predicted_prices)
        self.predictions.set_index('datetime', inplace=True)
        
        print(f"预测完成，生成了 {len(self.predictions)} 条预测数据")
        print(f"预测价格范围: ${self.predictions['Low'].min():.2f} - ${self.predictions['High'].max():.2f}")
    
    def visualize_results(self):
        """可视化结果"""
        print("\n=== 生成可视化图表 ===")
        
        if self.data is None or self.predictions is None:
            print("没有数据可供可视化")
            return
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('ETH价格预测分析', fontsize=16, fontweight='bold')
        
        # 1. 价格走势图
        ax1 = axes[0, 0]
        ax1.plot(self.data.index, self.data['Close'], label='历史价格', color='blue', linewidth=2)
        ax1.plot(self.predictions.index, self.predictions['Close'], label='预测价格', color='red', linewidth=2, linestyle='--')
        ax1.set_title('价格走势预测')
        ax1.set_ylabel('价格 (USD)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 成交量对比
        ax2 = axes[0, 1]
        ax2.bar(self.data.index[-48:], self.data['Volume'].tail(48), alpha=0.7, label='历史成交量', color='blue')
        ax2.bar(self.predictions.index, self.predictions['Volume'], alpha=0.7, label='预测成交量', color='red')
        ax2.set_title('成交量对比')
        ax2.set_ylabel('成交量')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 技术指标
        ax3 = axes[1, 0]
        ax3.plot(self.data.index, self.data['RSI'], label='RSI', color='purple')
        ax3.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='超买线')
        ax3.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='超卖线')
        ax3.set_title('RSI指标')
        ax3.set_ylabel('RSI')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 预测置信区间
        ax4 = axes[1, 1]
        ax4.fill_between(self.predictions.index, 
                        self.predictions['Low'], 
                        self.predictions['High'], 
                        alpha=0.3, color='red', label='预测区间')
        ax4.plot(self.predictions.index, self.predictions['Close'], color='red', linewidth=2, label='预测价格')
        ax4.set_title('预测价格区间')
        ax4.set_ylabel('价格 (USD)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/workspace/eth_prediction.png', dpi=300, bbox_inches='tight')
        print("图表已保存为 eth_prediction.png")
        
        # 显示预测结果表格
        print("\n=== 预测结果详情 ===")
        print(self.predictions[['Open', 'High', 'Low', 'Close', 'Volume']].round(2))
    
    def run_analysis(self):
        """运行完整分析"""
        print("开始ETH价格预测分析...")
        
        # 获取数据
        self.fetch_data(days=7)
        
        # 分析数据
        self.analyze_data()
        
        # 预测未来
        self.predict_future(days=3)
        
        # 可视化结果
        self.visualize_results()
        
        print("\n分析完成！")

if __name__ == "__main__":
    predictor = ETHPredictor()
    predictor.run_analysis()