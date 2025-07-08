import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import seaborn as sns
import os
import matplotlib.patches as mpatches

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
sns.set(style="whitegrid", font='SimHei')

data = {
    '会议': ['aaai', 'cvpr', 'icml', 'ijcai', 'nips'],
    '2020': [1864, 1465, 1085, 778, 1898],
    '2021': [1961, 1660, 1183, 721, 2334],
    '2022': [1624, 2072, 1234, 863, 2834],
    '2023': [2021, 2353, 1828, 846, 3540],
    '2024': [2866, 2716, 2610, 1048, 4494]
}

df = pd.DataFrame(data).set_index('会议').T
df.index = df.index.astype(int)
predict_year = 2025

# 创建输出目录
output_dir = "Homework3.4"
os.makedirs(output_dir, exist_ok=True)

# 为每个会议创建单独的预测图表
for conference in data['会议']:
    plt.figure(figsize=(10, 6))
    # 提取该会议的数据
    conf_data = df[conference].values
    years = df.index.values
    # 线性回归预测
    X = years.reshape(-1, 1)
    y = conf_data
    model = LinearRegression()
    model.fit(X, y)
    lr_pred = model.predict(np.array([[predict_year]]))[0]
    # 绘制历史数据
    plt.plot(years, conf_data, 'o-', label='历史数据', linewidth=2, color='blue')
    # 绘制线性回归线
    regression_line = model.predict(X)
    plt.plot(years, regression_line, '--', color='orange', label='线性趋势')
    # 绘制预测点
    plt.plot(predict_year, lr_pred, '^', markersize=10, color='red', label='2025年预测')
    # 添加数据标签
    for year, value in zip(years, conf_data):
        plt.text(year, value, f'{value}', ha='center', va='bottom', fontsize=9)
    # 添加预测值标签
    plt.text(predict_year, lr_pred, f'{round(lr_pred)}', ha='center', va='bottom', fontsize=10, color='red')
    # 设置图表属性
    plt.title(f'{conference.upper()} 论文数量趋势与预测 (2020-2025)', fontsize=14)
    plt.xlabel('年份')
    plt.ylabel('论文数量')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    # 设置x轴范围
    plt.xlim(2020, 2026)
    # 保存单个会议图表
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{conference}_prediction.png', dpi=300)
    plt.close()

# 创建综合图表
plt.figure(figsize=(14, 10))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # 更鲜明的颜色
markers = ['o', 's', 'D', 'v', 'p']  # 不同形状的标记
line_styles = ['-', '--', '-.', ':', '-']  # 不同线型
predict_markers = ['^', '>', '<', 'd', '*']  # 不同形状的预测标记
# 为每个会议创建图例项
legend_handles = []
for i, conference in enumerate(data['会议']):
    conf_data = df[conference].values
    years = df.index.values
    # 线性回归预测
    X = years.reshape(-1, 1)
    y = conf_data
    model = LinearRegression()
    model.fit(X, y)
    lr_pred = model.predict(np.array([[predict_year]]))[0]
    # 绘制历史数据
    plt.plot(years, conf_data,
             marker=markers[i],
             linestyle=line_styles[i],
             color=colors[i],
             linewidth=2.5,
             markersize=8,
             label=f'{conference.upper()} 历史数据')
    # 绘制线性回归线
    regression_line = model.predict(X)
    plt.plot(years, regression_line,
             linestyle=line_styles[i],
             color=colors[i],
             alpha=0.7,
             linewidth=1.5)
    # 绘制预测点
    plt.plot(predict_year, lr_pred,
             marker=predict_markers[i],
             markersize=12,
             color=colors[i],
             label=f'{conference.upper()} 2025预测')
    # 为预测点添加会议标签
    plt.text(predict_year, lr_pred, f' {conference.upper()}',
             fontsize=10, ha='left', va='center', color=colors[i])
    # 创建图例项
    history_patch = mpatches.Patch(color=colors[i],
                                   label=f'{conference.upper()} 历史数据')
    predict_patch = mpatches.Patch(color=colors[i],
                                   label=f'{conference.upper()} 2025预测')
    legend_handles.extend([history_patch, predict_patch])
# 设置图表属性
plt.title('国际顶级会议论文数量趋势与2025年预测', fontsize=18, fontweight='bold')
plt.xlabel('年份', fontsize=12)
plt.ylabel('论文数量', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xlim(2020, 2026)
plt.ylim(0, 5500)  # 扩展y轴范围以容纳标签
# 添加数据点标签
for conference in data['会议']:
    conf_data = df[conference].values
    years = df.index.values
    for j, year in enumerate(years):
        plt.text(year, conf_data[j], f'{conf_data[j]}',
                 fontsize=8, ha='center', va='bottom',
                 color=colors[data['会议'].index(conference)])
# 添加图例
plt.legend(handles=legend_handles, loc='upper left', ncol=2, fontsize=10)
# 添加注释
plt.figtext(0.5, 0.01,
            "注：预测基于2020-2024年数据进行线性回归分析",
            ha="center", fontsize=10, bbox=dict(facecolor='lightyellow', alpha=0.5))
# 保存综合图表
plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.savefig(f'{output_dir}/all_conferences_prediction.png', dpi=300)
plt.close()

# 仅显示图表保存信息
print("=" * 80)
print(f"所有图表已保存至目录: {os.path.abspath(output_dir)}")
print("=" * 80)