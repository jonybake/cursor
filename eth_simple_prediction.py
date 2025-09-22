#!/usr/bin/env python3
"""
ETH价格预测脚本 - 简化版
使用基础Python库进行ETH价格预测
"""

import math
import random
from datetime import datetime, timedelta
import json

class ETHPredictor:
    def __init__(self):
        self.data = []
        self.predictions = []
        
    def generate_mock_data(self, days=7):
        """生成模拟的ETH数据"""
        print("生成模拟ETH数据...")
        
        # 设置随机种子确保结果可重现
        random.seed(42)
        
        # 基础价格和参数
        base_price = 3000.0
        volatility = 0.02  # 2%的波动率
        base_volume = 1000000  # 基础成交量
        
        # 生成一周的小时数据
        hours = days * 24
        current_time = datetime.now() - timedelta(days=days)
        
        for i in range(hours):
            # 价格变化基于随机游走
            price_change = random.gauss(0, volatility)
            base_price *= (1 + price_change)
            
            # 生成OHLC数据
            open_price = base_price
            high_price = open_price * (1 + abs(random.gauss(0, 0.01)))
            low_price = open_price * (1 - abs(random.gauss(0, 0.01)))
            close_price = open_price * (1 + random.gauss(0, 0.005))
            
            # 生成成交量
            volume = int(base_volume * (1 + random.gauss(0, 0.3)))
            
            self.data.append({
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
            
            current_time += timedelta(hours=1)
            base_price = close_price
        
        print(f"生成了 {len(self.data)} 条数据")
    
    def calculate_technical_indicators(self):
        """计算技术指标"""
        if len(self.data) < 20:
            return
        
        # 计算移动平均线
        for i in range(19, len(self.data)):
            # 5期移动平均
            ma5_sum = sum(self.data[j]['close'] for j in range(i-4, i+1))
            self.data[i]['ma5'] = round(ma5_sum / 5, 2)
            
            # 20期移动平均
            ma20_sum = sum(self.data[j]['close'] for j in range(i-19, i+1))
            self.data[i]['ma20'] = round(ma20_sum / 20, 2)
        
        # 计算RSI
        for i in range(14, len(self.data)):
            gains = []
            losses = []
            
            for j in range(i-13, i+1):
                if j > 0:
                    change = self.data[j]['close'] - self.data[j-1]['close']
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(-change)
            
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            self.data[i]['rsi'] = round(rsi, 2)
    
    def analyze_trends(self):
        """分析趋势"""
        if len(self.data) < 24:
            return {}
        
        # 分析最近24小时的趋势
        recent_data = self.data[-24:]
        
        # 价格趋势
        price_changes = []
        for i in range(1, len(recent_data)):
            change = (recent_data[i]['close'] - recent_data[i-1]['close']) / recent_data[i-1]['close']
            price_changes.append(change)
        
        avg_price_change = sum(price_changes) / len(price_changes)
        
        # 成交量趋势
        volumes = [d['volume'] for d in recent_data]
        avg_volume = sum(volumes) / len(volumes)
        volume_volatility = math.sqrt(sum((v - avg_volume) ** 2 for v in volumes) / len(volumes))
        
        # 技术指标
        last_rsi = self.data[-1].get('rsi', 50)
        last_ma5 = self.data[-1].get('ma5', self.data[-1]['close'])
        last_ma20 = self.data[-1].get('ma20', self.data[-1]['close'])
        
        return {
            'price_trend': avg_price_change,
            'volume_avg': avg_volume,
            'volume_volatility': volume_volatility,
            'rsi': last_rsi,
            'ma5': last_ma5,
            'ma20': last_ma20,
            'ma_trend': (last_ma5 - last_ma20) / last_ma20
        }
    
    def predict_future(self, days=3):
        """预测未来价格"""
        print(f"\n开始预测未来{days}天...")
        
        if not self.data:
            print("没有历史数据")
            return
        
        # 分析当前趋势
        trends = self.analyze_trends()
        
        # 获取最后的价格和成交量
        last_price = self.data[-1]['close']
        last_volume = self.data[-1]['volume']
        
        # 预测参数
        hours_to_predict = days * 24
        current_time = datetime.now()
        
        for i in range(hours_to_predict):
            # 基础价格变化
            base_change = trends['price_trend']
            
            # RSI调整
            rsi = trends['rsi']
            if rsi > 70:  # 超买
                rsi_factor = -0.001
            elif rsi < 30:  # 超卖
                rsi_factor = 0.001
            else:
                rsi_factor = 0
            
            # 移动平均趋势
            ma_trend = trends['ma_trend']
            
            # 随机波动
            random_factor = random.gauss(0, 0.01)
            
            # 计算价格变化
            total_change = base_change + rsi_factor + ma_trend * 0.1 + random_factor
            new_price = last_price * (1 + total_change)
            
            # 生成OHLC
            open_price = last_price
            high_price = max(open_price, new_price) * (1 + abs(random.gauss(0, 0.005)))
            low_price = min(open_price, new_price) * (1 - abs(random.gauss(0, 0.005)))
            close_price = new_price
            
            # 预测成交量
            volume_factor = 1 + random.gauss(0, 0.2)
            predicted_volume = int(last_volume * volume_factor)
            
            self.predictions.append({
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': predicted_volume
            })
            
            current_time += timedelta(hours=1)
            last_price = close_price
            last_volume = predicted_volume
        
        print(f"预测完成，生成了 {len(self.predictions)} 条预测数据")
    
    def print_analysis(self):
        """打印分析结果"""
        print("\n" + "="*50)
        print("ETH价格预测分析报告")
        print("="*50)
        
        if not self.data:
            print("没有历史数据")
            return
        
        # 历史数据统计
        prices = [d['close'] for d in self.data]
        volumes = [d['volume'] for d in self.data]
        
        print(f"\n历史数据统计 (最近{len(self.data)}小时):")
        print(f"最高价: ${max(prices):.2f}")
        print(f"最低价: ${min(prices):.2f}")
        print(f"平均价: ${sum(prices)/len(prices):.2f}")
        print(f"价格波动率: {math.sqrt(sum((p - sum(prices)/len(prices))**2 for p in prices) / len(prices)):.2f}")
        print(f"平均成交量: {sum(volumes)/len(volumes):,.0f}")
        
        # 技术指标
        if len(self.data) >= 20:
            last_data = self.data[-1]
            print(f"\n当前技术指标:")
            print(f"RSI: {last_data.get('rsi', 'N/A')}")
            print(f"MA5: ${last_data.get('ma5', 'N/A')}")
            print(f"MA20: ${last_data.get('ma20', 'N/A')}")
        
        # 预测结果
        if self.predictions:
            pred_prices = [p['close'] for p in self.predictions]
            pred_volumes = [p['volume'] for p in self.predictions]
            
            print(f"\n未来3天预测:")
            print(f"预测价格范围: ${min(pred_prices):.2f} - ${max(pred_prices):.2f}")
            print(f"预测平均价: ${sum(pred_prices)/len(pred_prices):.2f}")
            print(f"预测平均成交量: {sum(pred_volumes)/len(pred_volumes):,.0f}")
            
            print(f"\n详细预测数据:")
            print("时间\t\t\t开盘\t最高\t最低\t收盘\t成交量")
            print("-" * 70)
            for pred in self.predictions[:12]:  # 显示前12小时
                print(f"{pred['timestamp']}\t{pred['open']}\t{pred['high']}\t{pred['low']}\t{pred['close']}\t{pred['volume']:,}")
            
            if len(self.predictions) > 12:
                print(f"... (还有 {len(self.predictions) - 12} 条数据)")
    
    def save_results(self):
        """保存结果到JSON文件"""
        results = {
            'historical_data': self.data,
            'predictions': self.predictions,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        with open('/workspace/eth_prediction_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到 eth_prediction_results.json")
    
    def run_analysis(self):
        """运行完整分析"""
        print("开始ETH价格预测分析...")
        
        # 生成历史数据
        self.generate_mock_data(days=7)
        
        # 计算技术指标
        self.calculate_technical_indicators()
        
        # 预测未来
        self.predict_future(days=3)
        
        # 打印结果
        self.print_analysis()
        
        # 保存结果
        self.save_results()
        
        print("\n分析完成！")

if __name__ == "__main__":
    predictor = ETHPredictor()
    predictor.run_analysis()