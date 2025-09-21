#!/usr/bin/env python3
"""
ETH交易量分析与K线图推算工具 - 简化版
基于ETH一周交易量数据，推算最合理的K线图周期
"""

import json
from datetime import datetime, timedelta
import random

class ETHKlineAnalyzer:
    def __init__(self):
        self.eth_data = None
        self.volume_data = None
        
    def generate_realistic_eth_data(self):
        """
        基于实际ETH价格和交易量特征生成模拟数据
        价格范围: 3000-4500 USD
        交易量范围: 15-45亿美元/天
        """
        # 生成过去7天的数据
        dates = []
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            dates.append(date.strftime('%Y-%m-%d'))
        
        # 基础价格趋势（从3000上涨到4500）
        base_prices = [3000, 3200, 3400, 3600, 3800, 4000, 4200]
        
        data = []
        for i, (date, base_price) in enumerate(zip(dates, base_prices)):
            # 添加随机波动
            price_volatility = random.uniform(-50, 50)
            price = base_price + price_volatility
            
            # 日内波动范围
            daily_range = random.uniform(20, 100)
            
            # 开盘价
            open_price = price + random.uniform(-daily_range/2, daily_range/2)
            
            # 最高价和最低价
            high_price = open_price + random.uniform(0, daily_range)
            low_price = open_price - random.uniform(0, daily_range)
            
            # 收盘价（基于趋势）
            close_price = open_price + random.uniform(-daily_range/2, daily_range/2)
            
            # 交易量（与价格波动相关）
            volume_base = random.uniform(1.5, 4.5)  # 15-45亿美元
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
        
        return data
    
    def calculate_optimal_timeframe(self, data):
        """
        基于交易量分析计算最优K线图时间周期
        """
        # 计算价格波动率
        price_changes = []
        for i in range(1, len(data)):
            change = (data[i]['close'] - data[i-1]['close']) / data[i-1]['close']
            price_changes.append(change)
        
        # 计算交易量特征
        volumes = [d['volume'] for d in data]
        avg_volume = sum(volumes) / len(volumes)
        volume_variance = sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)
        volume_std = volume_variance ** 0.5
        volume_cv = volume_std / avg_volume  # 变异系数
        
        # 计算价格趋势强度
        price_trend = (data[-1]['close'] - data[0]['close']) / data[0]['close']
        
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
    
    def generate_analysis_report(self, data):
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

📋 详细数据:
"""
        
        for i, day in enumerate(data):
            report += f"第{i+1}天 ({day['date']}): 开盘{day['open']}, 最高{day['high']}, 最低{day['low']}, 收盘{day['close']}, 交易量{day['volume']}十亿\n"
        
        return report
    
    def generate_html_chart(self, data):
        """
        生成HTML格式的K线图
        """
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>ETH K线图分析</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .chart-container { width: 100%; height: 400px; margin: 20px 0; }
        .data-table { margin: 20px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>ETH K线图分析</h1>
    <div class="chart-container">
        <canvas id="priceChart"></canvas>
    </div>
    <div class="chart-container">
        <canvas id="volumeChart"></canvas>
    </div>
    <div class="data-table">
        <h3>详细数据</h3>
        <table>
            <tr>
                <th>日期</th>
                <th>开盘</th>
                <th>最高</th>
                <th>最低</th>
                <th>收盘</th>
                <th>交易量(十亿)</th>
            </tr>
"""
        
        for day in data:
            html += f"""
            <tr>
                <td>{day['date']}</td>
                <td>{day['open']}</td>
                <td>{day['high']}</td>
                <td>{day['low']}</td>
                <td>{day['close']}</td>
                <td>{day['volume']}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <script>
        // 价格图表
        const priceCtx = document.getElementById('priceChart').getContext('2d');
        const priceData = """ + json.dumps(data) + """;
        
        new Chart(priceCtx, {
            type: 'line',
            data: {
                labels: priceData.map(d => d.date),
                datasets: [{
                    label: '收盘价',
                    data: priceData.map(d => d.close),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
        
        // 交易量图表
        const volumeCtx = document.getElementById('volumeChart').getContext('2d');
        new Chart(volumeCtx, {
            type: 'bar',
            data: {
                labels: priceData.map(d => d.date),
                datasets: [{
                    label: '交易量(十亿)',
                    data: priceData.map(d => d.volume),
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
        return html
    
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
        
        # 生成HTML图表
        html_chart = self.generate_html_chart(self.eth_data)
        with open('/workspace/eth_kline_analysis.html', 'w', encoding='utf-8') as f:
            f.write(html_chart)
        print("✅ HTML图表已保存为 eth_kline_analysis.html")
        
        # 保存数据为JSON
        with open('/workspace/eth_data.json', 'w', encoding='utf-8') as f:
            json.dump({
                'data': self.eth_data,
                'analysis': analysis
            }, f, ensure_ascii=False, indent=2)
        print("✅ 数据已保存为 eth_data.json")
        
        return self.eth_data, analysis

if __name__ == "__main__":
    analyzer = ETHKlineAnalyzer()
    data, analysis = analyzer.run_analysis()