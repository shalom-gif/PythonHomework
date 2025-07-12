import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')  # 或 'Qt5Agg'
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import linregress
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib as mpl


# 设置支持中文的字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
mpl.rcParams['axes.unicode_minus'] = False

# 读取数据并处理
df = pd.read_csv('近100期大乐透开奖数据和中奖情况.csv', usecols=[2, 8])  # 第三列索引2，第九列索引8
df.columns = ['开奖日期', '总销售额']  # 重命名列

# 转换日期格式并排序
df['开奖日期'] = pd.to_datetime(df['开奖日期'])
df.sort_values('开奖日期', inplace=True)  # 按日期升序排列
# 添加星期几信息（0=周一，1=周三，2=周六）
df['星期'] = df['开奖日期'].dt.weekday.map({0: '周一', 2: '周三', 5: '周六'})

# 计算移动平均线
df['3期移动平均'] = df['总销售额'].rolling(window=3).mean()
df['7期移动平均'] = df['总销售额'].rolling(window=7).mean()
df['30期移动平均'] = df['总销售额'].rolling(window=30).mean()

# 创建画布
plt.figure(figsize=(14, 8), facecolor='#f8f9fa')
ax = plt.gca()
ax.set_facecolor('#f8f9fa')

# 绘制销售额趋势
plt.plot(df['开奖日期'], df['总销售额'], label='每日销售额', color='#1f77b4',
         alpha=0.7, marker='o', markersize=4, linewidth=1.5)

# 绘制移动平均线
plt.plot(df['开奖日期'], df['3期移动平均'], label='3期移动平均', color='#9467bd', linewidth=2.5, linestyle='-.')
plt.plot(df['开奖日期'], df['7期移动平均'], label='7期移动平均', color='#ff7f0e', linewidth=2.5, linestyle='--')
plt.plot(df['开奖日期'], df['30期移动平均'], label='30期移动平均', color='#2ca02c', linewidth=2.5)

# 添加趋势线（线性回归）
x_num = mdates.date2num(df['开奖日期'])
slope, intercept, r_value, p_value, std_err = linregress(x_num, df['总销售额'])
trendline = slope * x_num + intercept
plt.plot(df['开奖日期'], trendline, color='#d62728', linewidth=2.5, linestyle='-.',
         label=f'趋势线 (R²={r_value**2: .3f})'.replace('²', '^2'))

# 标记极值点
max_idx = df['总销售额'].idxmax()
min_idx = df['总销售额'].idxmin()
plt.scatter(df.loc[max_idx, '开奖日期'], df.loc[max_idx, '总销售额'], color='#d62728', s=100, zorder=5)
plt.scatter(df.loc[min_idx, '开奖日期'], df.loc[min_idx, '总销售额'], color='#2ca02c', s=100, zorder=5)

# 添加文本标注
plt.annotate(f'最高: {df.loc[max_idx, "总销售额"]/1e6: .2f}百万', xy=(df.loc[max_idx, '开奖日期'], df.loc[max_idx, '总销售额']),
             xytext=(10, 20), textcoords='offset points', arrowprops=dict(arrowstyle='->', color='#d62728'))
plt.annotate(f'最低: {df.loc[min_idx, "总销售额"]/1e6: .2f}百万', xy=(df.loc[min_idx, '开奖日期'], df.loc[min_idx, '总销售额']),
             xytext=(10, -30), textcoords='offset points', arrowprops=dict(arrowstyle='->', color='#2ca02c'))

# 设置标题和标签
plt.title('大乐透总销售额趋势分析 (近100期)', fontsize=16, pad=20)
plt.xlabel('开奖日期', fontsize=12)
plt.ylabel('总销售额 (元)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

# 格式化坐标轴
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.xticks(rotation=45)
plt.gcf().autofmt_xdate()

# 添加统计信息框
stats_text = f"""数据统计:
最高销售额: {df['总销售额'].max()/1e6: .2f} 百万
最低销售额: {df['总销售额'].min()/1e6: .2f} 百万
平均销售额: {df['总销售额'].mean()/1e6: .2f} 百万
标准差: {df['总销售额'].std()/1e6: .2f} 百万
销售额变化率: {(df['总销售额'].iloc[-1]/df['总销售额'].iloc[0]-1)*100: .1f}%"""
plt.text(0.02, 0.98, stats_text, transform=ax.transAxes, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# 添加图例
plt.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.subplots_adjust(bottom=0.15)
plt.savefig('大乐透总销售额随开奖日期的变化趋势.png', dpi=300)
plt.show()

# 计算并打印关键统计指标
mean_sales = df['总销售额'].mean()
median_sales = df['总销售额'].median()
sales_growth = (df['总销售额'].iloc[-1] - df['总销售额'].iloc[0]) / df['总销售额'].iloc[0] * 100

print(f"\n关键趋势分析:")
print(f"1. 销售额整体变化率: {sales_growth: .1f}%")
print(f"2. 平均每期销售额: {mean_sales/1e6: .2f} 百万元")
print(f"3. 销售额中位数: {median_sales/1e6: .2f} 百万元")
print(f"4. 趋势线拟合优度 (R²): {r_value**2: .4f}".replace('²', '^2'))
print(f"5. 最高销售额出现在: {df.loc[max_idx, '开奖日期'].strftime('%Y-%m-%d')}")
print(f"6. 最低销售额出现在: {df.loc[min_idx, '开奖日期'].strftime('%Y-%m-%d')}")

# 方法1：按星期几分组预测
def method_weekday_avg(df):
    # 计算各星期平均销售额
    weekday_avg = df.groupby('星期')['总销售额'].mean()

    # 计算最近3期周三销售额的加权平均（最近一期权重最高）
    wed_data = df[df['星期'] == '周三'].tail(3)['总销售额']
    weights = np.array([0.2, 0.3, 0.5])  # 权重分配（由远到近）
    weighted_avg = np.sum(wed_data.values * weights)

    # 综合预测值（基础平均值占40%，近期趋势占60%）
    wed_pred = 0.4 * weekday_avg['周三'] + 0.6 * weighted_avg

    return wed_pred, weekday_avg


# 方法2：SARIMA时间序列预测（修复索引问题）
def method_sarima(df):
    # 创建整数索引的时间序列
    ts = df['总销售额'].reset_index(drop=True)

    # SARIMA参数设置 (p,d,q)(P,D,Q,s)
    # 基于数据特点：小数据量+明显周周期(s=3)
    order = (1, 0, 1)  # 非季节性部分
    seasonal_order = (1, 0, 1, 3)  # 季节性部分（周期为3）

    # 训练SARIMA模型
    model = SARIMAX(ts, order=order, seasonal_order=seasonal_order,
                    enforce_stationarity=False, enforce_invertibility=False)
    results = model.fit(disp=False, maxiter=100)

    # 预测下一期
    forecast = results.get_forecast(steps=1)
    pred_value = forecast.predicted_mean.iloc[0]
    conf_int = forecast.conf_int().iloc[0].tolist()

    # 获取拟合值（处理可能的缺失值）
    fitted_values = results.fittedvalues
    if len(fitted_values) < len(ts):
        # 补齐缺失的拟合值
        n_missing = len(ts) - len(fitted_values)
        fitted_values = pd.concat([pd.Series([np.nan] * n_missing), fitted_values])

    return pred_value, conf_int, fitted_values


# 方法3：移动平均预测（优化）
def method_moving_average(df):
    # 计算3期移动平均
    df['3期移动平均'] = df['总销售额'].rolling(window=3, min_periods=1).mean()

    # 计算周三的移动平均
    wed_mask = df['星期'] == '周三'
    wed_ma = df.loc[wed_mask, '总销售额'].rolling(window=3, min_periods=1).mean()

    # 获取最近值
    last_three = df['总销售额'].tail(3).values
    last_wed_ma = wed_ma.iloc[-1] if not wed_ma.empty else np.mean(last_three)

    # 综合预测值（整体移动平均占50%，周三移动平均占50%）
    final_pred = 0.5 * np.mean(last_three) + 0.5 * last_wed_ma

    return final_pred, df


# 执行三种预测方法
pred_weekday, weekday_avg = method_weekday_avg(df)
pred_sarima, conf_int, fitted_values = method_sarima(df)
pred_ma, df = method_moving_average(df)

# 打印预测结果
print(f"【按星期预测结果】2025-07-02(周三)预测销售额: {pred_weekday: .2f}元")
print(
    f"【SARIMA预测结果】2025-07-02(周三)预测销售额: {pred_sarima: .2f}元 (95%置信区间: {conf_int[0]: .2f}~{conf_int[1]: .2f})")
print(f"【移动平均预测结果】2025-07-02(周三)预测销售额: {pred_ma: .2f}元")

# ==================== 结果可视化 ====================
plt.figure(figsize=(14, 10))

# 1. 原始数据和星期分布
plt.subplot(3, 1, 1)
colors = {'周一': 'blue', '周三': 'green', '周六': 'red'}
for weekday, group in df.groupby('星期'):
    plt.scatter(group['开奖日期'], group['总销售额'],
                color=colors[weekday], label=weekday, alpha=0.7)
plt.title('大乐透销售额趋势 (按星期分组)')
plt.ylabel('销售额 (元)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

# 2. 移动平均趋势
plt.subplot(3, 1, 2)
plt.plot(df['开奖日期'], df['总销售额'], 'b-', label='实际销售额', alpha=0.5)
plt.plot(df['开奖日期'], df['3期移动平均'], 'r-', linewidth=2, label='3期移动平均')
plt.title('销售额趋势与移动平均线')
plt.ylabel('销售额 (元)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# 3. SARIMA拟合效果
plt.subplot(3, 1, 3)
plt.plot(df['开奖日期'], df['总销售额'], 'b-', label='实际销售额')
plt.plot(df['开奖日期'], fitted_values, 'r--', label='SARIMA拟合值')
plt.title('SARIMA模型拟合效果')
plt.ylabel('销售额 (元)')
plt.xlabel('日期')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

plt.tight_layout()

# 添加预测点标记和图例
pred_date = pd.to_datetime('2025-07-02')
predictions = {
    '按星期分组预测': pred_weekday,
    '移动平均预测': pred_ma,
    'SARIMA时间序列': pred_sarima
}

for i, (method, pred) in enumerate(predictions.items(), 1):
    plt.subplot(3, 1, i)

    # 绘制预测点标记
    plt.scatter([pred_date], [pred], s=100, c='purple', marker='*',
                edgecolors='gold', linewidths=1.5, zorder=10,
                label=f'{method}: {pred:,.2f}元')

    # 添加图例
    plt.legend()

plt.savefig('大乐透最近一期总销售额预测分析（2025年7月3日-周三）.png', dpi=300)
plt.show()

# 添加数据描述性统计
print("\n数据统计摘要:")
print(df.groupby('星期')['总销售额'].describe())

# 输出各方法预测值表格
results = pd.DataFrame({
    '预测方法': ['按星期分组预测', 'SARIMA时间序列', '移动平均'],
    '预测销售额': [round(pred_weekday, 2), round(pred_sarima, 2), round(pred_ma, 2)],
    '说明': [
        f'周三基础平均:{weekday_avg["周三"]:.2f} + 近期趋势调整',
        f'SARIMA(1,0,1)(1,0,1,3)模型',
        '整体3期MA + 周三3期MA组合'
    ]
})
print("\n预测结果汇总:")
print(results.to_string(index=False))

# 最新一期实际数据
print("\n大乐透最近一期实际总销售额（2025年7月3日-周三）为304472528	")
