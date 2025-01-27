# 组合交易策略

组合交易策略通过构建包含多种资产的投资组合，分散风险并优化收益。本文探讨组合交易的基本知识，基于马科维茨投资组合理论（Modern Portfolio Theory, MPT），并提供相应的量化实现代码。

## 一、组合交易原理

组合交易基于马科维茨投资组合理论，核心思想是通过分散投资来优化风险与收益的关系。

### 1. 马科维茨投资组合理论的基本原理

- **风险与收益的关系**
  - **收益**：用预期收益率（Expected Return）衡量，是投资者对未来投资回报的期望值。
  - **风险**：通过投资收益的波动性（标准差）衡量。波动性越大，风险越高。

- **分散化与相关性**
  - **分散化**：通过投资多个资产，降低整体投资组合的波动性。
  - **相关性**：
    - **正相关**：资产价格同步上涨或下跌，不能有效分散风险。
    - **负相关**：一种资产价格上涨，另一种下跌，能有效分散风险。
    - **不相关**：资产价格变动无明显关系。

- **有效前沿（Efficient Frontier）**
  - 表示在不同风险水平下可以获得的最高预期收益或在特定收益水平下的最低风险。
  - **全球最小方差组合（Global Minimum Variance Portfolio）**：在有效前沿上实现最低风险的组合。

- **投资者的风险偏好**
  - **保守型**：选择低风险、低收益的组合，位于有效前沿的左侧。
  - **激进型**：承担更高风险以追求更高收益，位于有效前沿的右侧。

- **市场组合与资本市场线（Capital Market Line, CML）**
  - 引入无风险资产后，通过无风险资产和市场组合之间的资金分配，找到投资者偏好的风险水平。

### 2. 马科维茨投资组合理论的数学模型

- **投资组合的预期收益**
  \[
  E(R_p) = \sum_{i=1}^{n} w_i E(R_i)
  \]
  
- **投资组合的风险（方差）**
  \[
  \sigma_p^2 = \sum_{i=1}^{n} \sum_{j=1}^{n} w_i w_j \sigma_i \sigma_j \rho_{i,j}
  \]

## 二、马科维茨理论的现实应用

### 1. 数据准确性
依赖历史数据来估计资产的预期收益、风险和相关性，但历史数据不总能准确预测未来。

### 2. 动态市场
金融市场动态变化，需定期调整投资组合以应对市场变化。

### 3. 行为偏差
投资者行为受到情绪和心理因素影响，可能导致不理性决策。

### 4. 交易成本
实际交易中存在佣金和税费，频繁调整投资组合可能增加成本。

## 三、组合交易的实现步骤

1. **获取资产的历史数据**：计算资产的预期收益和协方差矩阵。
2. **构建目标函数**：根据均值-方差优化模型，目标是最小化组合的方差或最大化夏普比率。
3. **求解优化问题**：通过约束条件（例如投资比例和总权重为1）进行优化，找到最优的投资组合。

## 四、代码实现

### 1. 基于Python的马科维茨投资组合优化

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as sco
import yfinance as yf

# 下载资产历史数据
assets = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # 资产代码
data = yf.download(assets, start="2020-01-01", end="2023-01-01")['Adj Close']

# 计算每日收益率
returns = data.pct_change().dropna()

# 计算年化预期收益和协方差矩阵
annual_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252

# 定义组合的预期收益和风险（方差）
def portfolio_performance(weights, mean_returns, cov_matrix):
    returns = np.sum(weights * mean_returns)
    volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return returns, volatility

# 定义目标函数：最小化风险（方差）
def minimize_volatility(weights, mean_returns, cov_matrix):
    return portfolio_performance(weights, mean_returns, cov_matrix)[1]

# 定义约束条件
def constraint_sum(weights):
    return np.sum(weights) - 1

# 初始化权重和边界（每个产的权重在0-1之间）
num_assets = len(assets)
bounds = tuple((0, 1) for asset in range(num_assets))
initial_weights = num_assets * [1. / num_assets]  # 初始等权重

# 定义约束条件：总权重为1
constraints = ({'type': 'eq', 'fun': constraint_sum})

# 优化组合，使得组合的方差最小
opt_result = sco.minimize(minimize_volatility, initial_weights, args=(annual_returns, cov_matrix),
                          method='SLSQP', bounds=bounds, constraints=constraints)

# 提取最优权重
optimal_weights = opt_result.x

# 计算最优组合的收益和风险
optimal_return, optimal_volatility = portfolio_performance(optimal_weights, annual_returns, cov_matrix)

# 输出最优组合结果
print("最优资产组合权重:")
for i, asset in enumerate(assets):
    print(f"{asset}: {optimal_weights[i]:.2%}")
    
print(f"\n最优组合的年化预期收益: {optimal_return:.2%}")
print(f"最优组合的年化风险（标准差）: {optimal_volatility:.2%}")

# 可视化有效前沿
def plot_efficient_frontier(mean_returns, cov_matrix, num_portfolios=10000):
    results = np.zeros((3, num_portfolios))
    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        portfolio_return, portfolio_volatility = portfolio_performance(weights, mean_returns, cov_matrix)
        results[0, i] = portfolio_return
        results[1, i] = portfolio_volatility
        results[2, i] = results[0, i] / results[1, i]  # 计算夏普比率

    plt.figure(figsize=(10, 6))
    plt.scatter(results[1, :], results[0, :], c=results[2, :], cmap='viridis')
    plt.colorbar(label='Sharpe Ratio')
    plt.scatter(optimal_volatility, optimal_return, c='red', marker='*', s=200)  # 最优组合
    plt.title('Efficient Frontier')
    plt.xlabel('Volatility (Risk)')
    plt.ylabel('Return')
    plt.show()

# 绘制有效前沿
plot_efficient_frontier(annual_returns, cov_matrix)
```

### 2. 基于国信证券iQuant平台的马科维茨投资组合策略

```python
import pandas as pd
import numpy as np
import statsmodels.api as sm
import scipy.stats as scs
import scipy.optimize as sco
import matplotlib.pyplot as plt

def init(ContextInfo):
    # hs300成分股中sh和sz市场各自流通市值最大的前3只股票
    ContextInfo.trade_code_list = ['601398.SH', '601857.SH', '601288.SH', '000333.SZ', '002415.SZ', '000002.SZ']
    ContextInfo.set_universe(ContextInfo.trade_code_list)
    ContextInfo.accID = 'test'

def handlebar(ContextInfo):
    df = ContextInfo.get_market_data(['close'], stock_code=ContextInfo.trade_code_list, start_time='20150101', end_time='20160101', period='1d')
    data = pd.DataFrame(columns=ContextInfo.trade_code_list)

    for stk in df.items:
        data[stk] = df[stk]['close']
    
    returns = np.log(data / data.shift(1))
    noa = len(ContextInfo.trade_code_list)
    weights = np.random.random(noa)
    weights /= np.sum(weights)

    # 组合年化收益
    print(np.sum(returns.mean() * weights) * 252)
    
    # 组合方差
    print(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    
    # 组合标准差
    print(np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights))))

    port_returns = []
    port_variance = []

    for p in range(4000):
        weights = np.random.random(noa)
        weights /= np.sum(weights)
        port_returns.append(np.sum(returns.mean() * 252 * weights))
        port_variance.append(np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights))))

    port_returns = np.array(port_returns)
    port_variance = np.array(port_variance)
    
    # 无风险利率设定为4%
    risk_free = 0.04

    # ================== 投资组合优化 1 — Sharpe 最大 ==================
    def statistics(weights):
        weights = np.array(weights)
        port_returns = np.sum(returns.mean() * weights) * 252
        port_variance = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        return np.array([port_returns, port_variance, port_returns / port_variance])

    # 最小化 Sharpe 指数的负值
    def min_sharpe(weights):
        return -statistics(weights)[2]

    # 约束是所有参数(权重)的总和为 1
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # 参数值(权重)限制在 0 和 1 之间
    bnds = tuple((0, 1) for x in range(noa))
    
    # 优化函数调用
    opts = sco.minimize(min_sharpe, noa * [1. / noa,], method='SLSQP', bounds=bnds, constraints=cons)
    
    # ================== 投资组合优化 2 — 方差最小 ==================
    def min_variance(weights):
        return statistics(weights)[1]

    optv = sco.minimize(min_variance, noa * [1. / noa,], method='SLSQP', bounds=bnds, constraints=cons)
    
    # ================== 组合的有效前沿 ==================
    target_returns = np.linspace(0.0, 0.5, 50)
    target_variance = []

    for tar in target_returns:
        cons = ({'type': 'eq', 'fun': lambda x: statistics(x)[0] - tar}, {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        res = sco.minimize(min_variance, noa * [1. / noa,], method='SLSQP', bounds=bnds, constraints=cons)
        target_variance.append(res['fun'])

    target_variance = np.array(target_variance)

    # ================== 最优结果展示 ==================
    plt.figure(figsize=(8, 4))
    
    # 圆圈：蒙特卡洛随机产生的组合分布
    plt.scatter(port_variance, port_returns, c=(port_returns - risk_free) / port_variance, marker='o')
    
    # 叉号：有效前沿
    plt.scatter(target_variance, target_returns, c=target_returns / target_variance, marker='x')
    
    # 红星：标记最高 Sharpe 组合
    plt.plot(statistics(opts['x'])[1], statistics(opts['x'])[0], 'r*', markersize=15.0)
    
    # 黄星：标记最小方差组合
    plt.plot(statistics(optv['x'])[1], statistics(optv['x'])[0], 'y*', markersize=15.0)
    
    plt.grid(True)
    plt.xlabel('Expected Volatility')
    plt.ylabel('Expected Return')
    plt.colorbar(label='Sharpe Ratio')
    plt.show()
```

## 四、结论

有效的组合交易策略是量化交易成功的基础。通过科学合理地构建多样化的投资组合，结合马科维茨投资组合理论，投资者可以在控制风险的同时，优化收益。利用量化手段进行投资组合优化，可以克服人性的不足，提升交易纪律性和稳定性。

