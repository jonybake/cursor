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
            this.renderDataTable();
            this.hideLoading();
        } catch (error) {
            console.error('初始化失败:', error);
            this.showError('数据加载失败，请刷新页面重试');
        }
    }

    async loadAllData() {
        const [exchangeData, kellyData, volumeStats, priceTrend] = await Promise.all([
            this.fetchData('/api/exchange-data'),
            this.fetchData('/api/kelly-index'),
            this.fetchData('/api/volume-stats'),
            this.fetchData('/api/price-trend')
        ]);

        this.data = {
            exchange: exchangeData.data,
            kelly: kellyData.data,
            volumeStats: volumeStats.data,
            priceTrend: priceTrend.data
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