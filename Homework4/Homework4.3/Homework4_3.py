import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TkAgg')  # 或 'Qt5Agg'、'Agg'
import seaborn as sns
from scipy import stats

# 设置支持中文的字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
mpl.rcParams['axes.unicode_minus'] = False


def load_and_preprocess(file_path):
    """加载并预处理数据"""
    df = pd.read_csv(file_path)

    # 日期转换
    df['开奖日期'] = pd.to_datetime(df['开奖日期'])

    # 销售额转换（去除逗号）
    df['总销售额(元)'] = df['总销售额(元)'].astype(str).str.replace(',', '').astype(float)

    # 拆分前区号码 (使用str.split()方法)
    df['前区号码'] = df['中奖号码_前区'].str.split().apply(lambda x: [int(n) for n in x])

    # 拆开后区号码 (使用str.split()方法)
    df['后区号码'] = df['中奖号码_后区'].str.split().apply(lambda x: [int(n) for n in x])

    # 验证星期列
    valid_days = ['星期一', '星期三', '星期六']
    if not set(df['星期'].unique()).issubset(set(valid_days)):
        invalid_days = set(df['星期'].unique()) - set(valid_days)
        print(f"警告: 数据中包含非目标开奖日: {invalid_days}")

    return df


def analyze_sales(df):
    """分析销售额特征"""
    # 按星期分组统计
    grouped = df.groupby('星期')
    sales_stats = grouped['总销售额(元)'].agg(['mean', 'median', 'std', 'count'])

    # 销售额可视化
    plt.figure(figsize=(14, 10))

    # 箱线图
    plt.subplot(2, 2, 1)
    sns.boxplot(x='星期', y='总销售额(元)', data=df, order=['星期一', '星期三', '星期六'])
    plt.title('不同开奖日销售额分布')
    plt.ylabel('销售额(百万元)')

    # 条形图
    plt.subplot(2, 2, 2)
    sales_mean = grouped['总销售额(元)'].mean().div(1000000)
    sales_mean = sales_mean.reindex(['星期一', '星期三', '星期六'])
    sales_mean.plot(kind='bar', color=['skyblue', 'lightgreen', 'salmon'])
    plt.title('平均销售额对比')
    plt.ylabel('平均销售额(百万元)')
    plt.xticks(rotation=0)

    # 时间序列图
    plt.subplot(2, 2, 3)
    for day in ['星期一', '星期三', '星期六']:
        subset = df[df['星期'] == day]
        plt.plot(subset['开奖日期'], subset['总销售额(元)'] / 1000000, 'o-', label=day, alpha=0.7)
    plt.title('销售额随时间变化趋势')
    plt.ylabel('销售额(百万元)')
    plt.legend()

    # 密度图
    plt.subplot(2, 2, 4)
    sns.kdeplot(data=df, x='总销售额(元)', hue='星期', hue_order=['星期一', '星期三', '星期六'],
                fill=True, common_norm=False, alpha=0.3, palette='viridis')
    plt.title('销售额密度分布')
    plt.xlabel('销售额(元)')

    plt.tight_layout()
    plt.savefig('销售额特征.png', dpi=300)
    plt.show()

    return sales_stats


def analyze_numbers(df):
    """分析号码分布特征"""
    # 按星期分组
    grouped = df.groupby('星期')

    # 分别创建前区和后区的数据列表
    front_data = {'号码': [], '区域': [], '星期': []}
    back_data = {'号码': [], '区域': [], '星期': []}

    for day in ['星期一', '星期三', '星期六']:
        # 获取该星期的数据
        day_data = grouped.get_group(day) if day in grouped.groups else pd.DataFrame()

        if not day_data.empty:
            # 处理前区号码
            for nums in day_data['前区号码']:
                for num in nums:
                    front_data['号码'].append(num)
                    front_data['区域'].append('前区')
                    front_data['星期'].append(day)

            # 处理后区号码
            for nums in day_data['后区号码']:
                for num in nums:
                    back_data['号码'].append(num)
                    back_data['区域'].append('后区')
                    back_data['星期'].append(day)

    # 创建数据框
    front_df = pd.DataFrame(front_data)
    back_df = pd.DataFrame(back_data)

    numbers_df = pd.concat([front_df, back_df])

    # 号码频率可视化
    plt.figure(figsize=(16, 12))

    # 前区号码分布
    plt.subplot(2, 2, 1)
    if not front_df.empty:
        sns.histplot(data=front_df, x='号码', hue='星期', multiple='dodge',
                     binwidth=1, kde=False, discrete=True,
                     hue_order=['星期一', '星期三', '星期六'],
                     palette='Set2')
        plt.title('前区号码分布对比')
        plt.xticks(range(1, 36))
        plt.xlim(0.5, 35.5)

    # 后区号码分布
    plt.subplot(2, 2, 2)
    if not back_df.empty:
        sns.histplot(data=back_df, x='号码', hue='星期', multiple='dodge',
                     binwidth=1, kde=False, discrete=True,
                     hue_order=['星期一', '星期三', '星期六'],
                     palette='Set2')
        plt.title('后区号码分布对比')
        plt.xticks(range(1, 13))
        plt.xlim(0.5, 12.5)

    # 热力图 - 前区
    plt.subplot(2, 2, 3)
    if not front_df.empty:
        front_pivot = front_df.groupby(['号码', '星期']).size().unstack().fillna(0)
        sns.heatmap(front_pivot.T, annot=True, fmt='g', cmap='YlGnBu')
        plt.title('前区号码出现频率热力图')
        plt.ylabel('开奖日')

    # 热力图 - 后区
    plt.subplot(2, 2, 4)
    if not back_df.empty:
        back_pivot = back_df.groupby(['号码', '星期']).size().unstack().fillna(0)
        sns.heatmap(back_pivot.T, annot=True, fmt='g', cmap='YlGnBu')
        plt.title('后区号码出现频率热力图')
        plt.ylabel('开奖日')

    plt.tight_layout()
    plt.savefig('号码分布.png', dpi=300)
    plt.show()

    return numbers_df


def statistical_analysis(df):
    """执行统计检验"""
    # 按星期分组
    grouped = df.groupby('星期')

    # 准备销售额数据
    mon = grouped.get_group('星期一')['总销售额(元)'] if '星期一' in grouped.groups else pd.Series(dtype=float)
    wed = grouped.get_group('星期三')['总销售额(元)'] if '星期三' in grouped.groups else pd.Series(dtype=float)
    sat = grouped.get_group('星期六')['总销售额(元)'] if '星期六' in grouped.groups else pd.Series(dtype=float)

    # 方差分析 (检验销售额差异)
    if not mon.empty and not wed.empty and not sat.empty:
        _, p_sales = stats.f_oneway(mon, wed, sat)
    else:
        p_sales = 1.0  # 如果缺少数据，设为不显著

    # 号码分布检验
    results = {}
    for num_type in ['前区', '后区']:
        # 创建号码列表
        all_numbers = []
        all_days = []

        for day in ['星期一', '星期三', '星期六']:
            if day in grouped.groups:
                day_data = grouped.get_group(day)
                for nums in day_data[f'{num_type}号码']:
                    all_numbers.extend(nums)
                    all_days.extend([day] * len(nums))

        # 创建列联表
        if all_numbers:
            crosstab = pd.crosstab(
                index=pd.Series(all_numbers, name='号码'),
                columns=pd.Series(all_days, name='星期')
            )

            # 确保有足够的数据进行卡方检验
            if crosstab.size > 0 and crosstab.sum().sum() > 0:
                # 卡方检验
                _, p_num, _, _ = stats.chi2_contingency(crosstab)
                results[f'{num_type}号码分布'] = p_num
            else:
                results[f'{num_type}号码分布'] = 1.0  # 如果缺少数据，设为不显著
        else:
            results[f'{num_type}号码分布'] = 1.0

    return p_sales, results


def main(file_path):
    """主分析流程"""
    # 1. 加载和预处理数据
    df = load_and_preprocess(file_path)

    print(f"数据集大小: {df.shape}")
    print("开奖日分布:")
    day_counts = df['星期'].value_counts().reindex(['星期一', '星期三', '星期六'], fill_value=0)
    print(day_counts)

    # 2. 销售额分析
    sales_stats = analyze_sales(df)
    print("\n销售额统计:")
    # 确保按顺序输出
    sales_stats = sales_stats.reindex(['星期一', '星期三', '星期六'])
    print(sales_stats)

    # 3. 号码分布分析
    numbers_df = analyze_numbers(df)

    # 4. 统计检验
    p_sales, p_numbers = statistical_analysis(df)

    print("\n统计检验结果:")
    print(f"销售额差异的ANOVA p值: {p_sales: .6f}")
    for k, v in p_numbers.items():
        print(f"{k}卡方检验p值: {v: .6f}")

    # 解释结果
    print("\n分析结论:")
    if p_sales < 0.05:
        print("- 不同开奖日的销售额存在显著差异")
    else:
        print("- 不同开奖日的销售额没有显著差异")

    for k, v in p_numbers.items():
        if v < 0.05:
            print(f"- {k}在不同开奖日之间存在显著差异")
        else:
            print(f"- {k}在不同开奖日之间没有显著差异")


if __name__ == "__main__":
    df = "近100期大乐透开奖数据和中奖情况.csv"
    main(df)
    