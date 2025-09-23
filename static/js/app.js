// ETH交易量和凯利指数分析平台 - 前端JavaScript
class ETHAnalysisApp {
    constructor() {
        this.charts = {};
        this.data = {};
        this.init();
    }

    async init() {
        try {
            await this.loadAllData();
            this.renderOverviewStats();
            this.renderPriceChart();
            this.renderVolumeChart();
            this.renderKellyChart();
            this.renderKellyTable();
            this.renderPredictionOverview();
            this.renderPredictionChart();
            this.renderPredictionTable();
            this.renderInvestmentAdvice();
            this.renderDataTable();
            this.hideLoading();
        } catch (error) {
            console.error('初始化失败:', error);
            this.showError('数据加载失败，请刷新页面重试');
        }
    }

    async loadAllData() {
        const [exchangeData, kellyData, volumeStats, priceTrend, predictionData, predictionAnalysis] = await Promise.all([
            this.fetchData('/api/exchange-data'),
            this.fetchData('/api/kelly-index'),
            this.fetchData('/api/volume-stats'),
            this.fetchData('/api/price-trend'),
            this.fetchData('/api/kline-predictions'),
            this.fetchData('/api/prediction-analysis')
        ]);

        this.data = {
            exchange: exchangeData.data,
            kelly: kellyData.data,
            volumeStats: volumeStats.data,
            priceTrend: priceTrend.data,
            predictions: predictionData.data,
            predictionAnalysis: predictionAnalysis
        };
    }

    async fetchData(url) {
        const response = await fetch(url);
        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error);
        }
        return result;
    }

    renderOverviewStats() {
        const statsContainer = document.getElementById('overview-stats');
        const kellyData = this.data.kelly;
        const volumeStats = this.data.volumeStats;

        // 计算总体统计
        const totalVolume = volumeStats.reduce((sum, stat) => sum + stat.total_volume, 0);
        const avgKelly = kellyData.reduce((sum, item) => sum + item.kelly_index, 0) / kellyData.length;
        const bestExchange = kellyData[0]; // 已按凯利指数排序
        const totalExchanges = kellyData.length;

        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${this.formatNumber(totalVolume)}</div>
                <div class="stat-label">总交易量 (ETH)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${avgKelly.toFixed(3)}</div>
                <div class="stat-label">平均凯利指数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${bestExchange.exchange}</div>
                <div class="stat-label">最佳投资选择</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${totalExchanges}</div>
                <div class="stat-label">监控交易所数量</div>
            </div>
        `;
    }

    renderPriceChart() {
        const ctx = document.getElementById('priceChart').getContext('2d');
        const priceTrend = this.data.priceTrend;

        const datasets = Object.keys(priceTrend).map(exchange => ({
            label: exchange,
            data: priceTrend[exchange].prices,
            borderColor: priceTrend[exchange].color,
            backgroundColor: priceTrend[exchange].color + '20',
            borderWidth: 3,
            fill: false,
            tension: 0.4
        }));

        this.charts.price = new Chart(ctx, {
            type: 'line',
            data: {
                labels: priceTrend[Object.keys(priceTrend)[0]].timestamps,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'ETH价格趋势对比 (过去15天)',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '价格 (USD)'
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '日期'
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    renderVolumeChart() {
        const ctx = document.getElementById('volumeChart').getContext('2d');
        const volumeStats = this.data.volumeStats;

        this.charts.volume = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: volumeStats.map(stat => stat.exchange),
                datasets: [{
                    label: '平均日交易量 (ETH)',
                    data: volumeStats.map(stat => stat.avg_volume),
                    backgroundColor: volumeStats.map(stat => stat.color + '80'),
                    borderColor: volumeStats.map(stat => stat.color),
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '各交易所平均日交易量对比',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '交易量 (ETH)'
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '交易所'
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                }
            }
        });
    }

    renderKellyChart() {
        const ctx = document.getElementById('kellyChart').getContext('2d');
        const kellyData = this.data.kelly;

        this.charts.kelly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: kellyData.map(item => item.exchange),
                datasets: [{
                    label: '凯利指数',
                    data: kellyData.map(item => item.kelly_index),
                    backgroundColor: kellyData.map(item => item.color + '80'),
                    borderColor: kellyData.map(item => item.color),
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '各交易所凯利指数对比',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 0.25,
                        title: {
                            display: true,
                            text: '凯利指数'
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '交易所'
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                }
            }
        });
    }

    renderKellyTable() {
        const tbody = document.getElementById('kelly-table-body');
        const kellyData = this.data.kelly;

        tbody.innerHTML = kellyData.map(item => `
            <tr>
                <td>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background-color: ${item.color}; border-radius: 50%; margin-right: 8px;"></div>
                        ${item.exchange}
                    </div>
                </td>
                <td>
                    <strong>${item.kelly_index.toFixed(3)}</strong>
                </td>
                <td>
                    <span class="recommendation ${this.getRecommendationClass(item.kelly_index)}">
                        ${item.recommendation}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    renderDataTable() {
        const tbody = document.querySelector('#data-table tbody');
        const exchangeData = this.data.exchange;

        // 按日期和交易所排序
        const sortedData = exchangeData.sort((a, b) => {
            if (a.timestamp === b.timestamp) {
                return a.exchange.localeCompare(b.exchange);
            }
            return new Date(b.timestamp) - new Date(a.timestamp);
        });

        tbody.innerHTML = sortedData.map(item => {
            const priceChange = this.calculatePriceChange(item, exchangeData);
            return `
                <tr>
                    <td>${item.timestamp}</td>
                    <td>
                        <div style="display: flex; align-items: center;">
                            <div style="width: 12px; height: 12px; background-color: ${this.getExchangeColor(item.exchange)}; border-radius: 50%; margin-right: 8px;"></div>
                            ${item.exchange}
                        </div>
                    </td>
                    <td><strong>$${item.close.toLocaleString()}</strong></td>
                    <td>${this.formatNumber(item.volume)}</td>
                    <td>
                        <span class="${priceChange >= 0 ? 'text-success' : 'text-danger'}">
                            ${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)}%
                        </span>
                    </td>
                </tr>
            `;
        }).join('');
    }

    calculatePriceChange(item, allData) {
        const exchangeData = allData.filter(d => d.exchange === item.exchange);
        const currentIndex = exchangeData.findIndex(d => d.timestamp === item.timestamp);
        
        if (currentIndex > 0) {
            const prevPrice = exchangeData[currentIndex - 1].close;
            return ((item.close - prevPrice) / prevPrice) * 100;
        }
        return 0;
    }

    getExchangeColor(exchange) {
        const colors = {
            'Binance': '#F0B90B',
            'Coinbase': '#0052FF',
            'Kraken': '#4C4C4C',
            'OKX': '#000000'
        };
        return colors[exchange] || '#666';
    }

    getRecommendationClass(kellyIndex) {
        if (kellyIndex > 0.15) return 'strong-buy';
        if (kellyIndex > 0.10) return 'buy';
        if (kellyIndex > 0.05) return 'hold';
        return 'sell';
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('main-content').style.display = 'block';
    }

    showError(message) {
        const loading = document.getElementById('loading');
        loading.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }

    async refreshData() {
        const refreshBtn = document.querySelector('.refresh-btn');
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        try {
            await this.loadAllData();
            this.renderOverviewStats();
            this.renderPriceChart();
            this.renderVolumeChart();
            this.renderKellyChart();
            this.renderKellyTable();
            this.renderDataTable();
            
            // 显示成功提示
            this.showNotification('数据已更新', 'success');
        } catch (error) {
            console.error('刷新失败:', error);
            this.showNotification('数据刷新失败', 'error');
        } finally {
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }
    }

    // 预测功能渲染方法
    renderPredictionOverview() {
        const container = document.getElementById('prediction-overview');
        if (!container || !this.data.predictionAnalysis || !this.data.predictionAnalysis.success) {
            return;
        }

        const analysis = this.data.predictionAnalysis.analysis;
        
        container.innerHTML = `
            <div class="col-md-3">
                <div class="prediction-card">
                    <h5><i class="fas fa-dollar-sign"></i> 当前价格</h5>
                    <div class="value">$${analysis.current_price.toFixed(2)}</div>
                    <div class="label">ETH/USD</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="prediction-card">
                    <h5><i class="fas fa-target"></i> 目标价格</h5>
                    <div class="value">$${analysis.target_price.toFixed(2)}</div>
                    <div class="label">5天后预测</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="prediction-card">
                    <h5><i class="fas fa-chart-line"></i> 预期涨跌</h5>
                    <div class="value ${analysis.total_change_percent >= 0 ? 'text-success' : 'text-danger'}">
                        ${analysis.total_change_percent >= 0 ? '+' : ''}${analysis.total_change_percent.toFixed(2)}%
                    </div>
                    <div class="label">5天总变化</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="prediction-card">
                    <h5><i class="fas fa-shield-alt"></i> 置信度</h5>
                    <div class="value">${(analysis.confidence_score * 100).toFixed(1)}%</div>
                    <div class="label">预测可靠性</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${analysis.confidence_score * 100}%"></div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPredictionChart() {
        const ctx = document.getElementById('predictionChart');
        if (!ctx || !this.data.predictionAnalysis || !this.data.predictionAnalysis.success) {
            return;
        }

        const analysis = this.data.predictionAnalysis;
        const predictions = analysis.daily_predictions;
        
        // 准备图表数据
        const labels = predictions.map(p => p.date);
        const prices = predictions.map(p => p.close);
        const volumes = predictions.map(p => p.volume);
        
        // 创建双轴图表
        this.charts.prediction = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '预测价格 (USD)',
                    data: prices,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y'
                }, {
                    label: '预测交易量 (十亿)',
                    data: volumes,
                    borderColor: '#764ba2',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: '日期'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: '价格 (USD)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: '交易量 (十亿)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'ETH价格和交易量预测'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            afterLabel: function(context) {
                                const index = context.dataIndex;
                                const pred = predictions[index];
                                return [
                                    `开盘: $${pred.open.toFixed(2)}`,
                                    `最高: $${pred.high.toFixed(2)}`,
                                    `最低: $${pred.low.toFixed(2)}`,
                                    `置信度: ${(pred.confidence * 100).toFixed(1)}%`
                                ];
                            }
                        }
                    }
                }
            }
        });
    }

    renderPredictionTable() {
        const tbody = document.getElementById('prediction-table');
        if (!tbody || !this.data.predictionAnalysis || !this.data.predictionAnalysis.success) {
            return;
        }

        const predictions = this.data.predictionAnalysis.daily_predictions;
        
        tbody.innerHTML = predictions.map(pred => `
            <tr>
                <td>${pred.date}</td>
                <td>$${pred.close.toFixed(2)}</td>
                <td class="${pred.change_percent >= 0 ? 'text-success' : 'text-danger'}">
                    ${pred.change_percent >= 0 ? '+' : ''}${pred.change_percent.toFixed(2)}%
                </td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" style="width: ${pred.confidence * 100}%">
                            ${(pred.confidence * 100).toFixed(1)}%
                        </div>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    renderInvestmentAdvice() {
        const container = document.getElementById('investment-advice');
        if (!container || !this.data.predictionAnalysis || !this.data.predictionAnalysis.success) {
            return;
        }

        const advice = this.data.predictionAnalysis.analysis.investment_advice;
        const risk = this.data.predictionAnalysis.analysis.risk_assessment;
        const targets = this.data.predictionAnalysis.analysis.price_targets;
        
        container.innerHTML = `
            <div class="investment-advice-card">
                <h6><i class="fas fa-lightbulb"></i> 投资建议</h6>
                <div class="advice-action ${advice.action.toLowerCase()}">
                    ${advice.action} - ${advice.confidence}
                </div>
                <p class="mb-2">${advice.message}</p>
                <small class="text-muted">建议仓位: ${advice.position_size}</small>
                
                <hr>
                
                <h6><i class="fas fa-exclamation-triangle"></i> 风险评估</h6>
                <div class="risk-indicator ${risk.level.toLowerCase()}">
                    ${risk.level} 风险
                </div>
                <p class="mb-2">${risk.description}</p>
                <small class="text-muted">${risk.recommendation}</small>
                
                <hr>
                
                <h6><i class="fas fa-bullseye"></i> 价格目标</h6>
                <div class="row">
                    <div class="col-4 text-center">
                        <small class="text-muted">保守</small><br>
                        <strong>$${targets.conservative.toFixed(2)}</strong>
                    </div>
                    <div class="col-4 text-center">
                        <small class="text-muted">适中</small><br>
                        <strong>$${targets.moderate.toFixed(2)}</strong>
                    </div>
                    <div class="col-4 text-center">
                        <small class="text-muted">乐观</small><br>
                        <strong>$${targets.optimistic.toFixed(2)}</strong>
                    </div>
                </div>
            </div>
        `;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// 全局函数
function refreshData() {
    if (window.app) {
        window.app.refreshData();
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ETHAnalysisApp();
});

// 定期自动刷新数据 (每5分钟)
setInterval(() => {
    if (window.app) {
        window.app.refreshData();
    }
}, 300000);