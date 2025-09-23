#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用功能测试脚本
Web Application Function Test Script
"""

import requests
import json
import time

def test_web_app():
    """测试Web应用的各个API接口"""
    base_url = "http://localhost:5000"
    
    print("🧪 开始测试ETH分析Web应用...")
    print("=" * 50)
    
    # 测试API接口
    apis = [
        ("/api/exchange-data", "交易所数据"),
        ("/api/kelly-index", "凯利指数"),
        ("/api/volume-stats", "交易量统计"),
        ("/api/price-trend", "价格趋势")
    ]
    
    for api, name in apis:
        try:
            print(f"\n📊 测试 {name} API...")
            response = requests.get(f"{base_url}{api}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {name} API 测试成功")
                    
                    # 显示部分数据
                    if 'data' in data:
                        if isinstance(data['data'], list) and len(data['data']) > 0:
                            print(f"   数据条数: {len(data['data'])}")
                            if 'exchange' in data['data'][0]:
                                exchanges = list(set([item['exchange'] for item in data['data']]))
                                print(f"   交易所: {', '.join(exchanges)}")
                        elif isinstance(data['data'], dict):
                            print(f"   数据类型: 字典")
                            print(f"   键数量: {len(data['data'])}")
                else:
                    print(f"❌ {name} API 返回错误: {data.get('error', '未知错误')}")
            else:
                print(f"❌ {name} API 请求失败: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} API 连接失败: {e}")
        except Exception as e:
            print(f"❌ {name} API 测试异常: {e}")
    
    # 测试主页
    print(f"\n🌐 测试主页...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ 主页访问成功")
            if "ETH交易量和凯利指数分析平台" in response.text:
                print("✅ 页面内容正确")
            else:
                print("⚠️  页面内容可能有问题")
        else:
            print(f"❌ 主页访问失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 主页测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    print(f"📱 请在浏览器中访问: {base_url}")
    print("💡 建议使用Chrome或Firefox浏览器获得最佳体验")

if __name__ == "__main__":
    test_web_app()