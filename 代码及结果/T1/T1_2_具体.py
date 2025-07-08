import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 行业统计分析
def analyze_industries(df):
    """计算各行业富豪数量和财富总值"""
    # 行业分类统计
    industry_stats = df.groupby('企业信息_行业_中文').agg(
        富豪数量=('个人信息_姓名_中文', 'count'),
        财富总值_亿=('财富(人民币/亿)', 'sum'),
        平均财富_亿=('财富(人民币/亿)', 'mean'),
        代表人物=('个人信息_姓名_中文', lambda x: x.iloc[0] if not x.empty else '')
    ).sort_values('财富总值_亿', ascending=False)

    # 计算行业财富占比
    total_wealth = df['财富(人民币/亿)'].sum()
    industry_stats['财富占比'] = (industry_stats['财富总值_亿'] / total_wealth * 100).round(2)

    return industry_stats


# 可视化函数
def visualize_data(industry_stats):
    """生成行业分析可视化图表"""
    plt.figure(figsize=(18, 12))

    # 子图1：行业富豪数量TOP15
    plt.subplot(2, 2, 1)
    top15_count = industry_stats.head(15)
    sns.barplot(
        x='富豪数量',
        y=top15_count.index,
        data=top15_count,
        palette='viridis',
        legend=False
    )
    plt.title('各行业上榜富豪数量TOP15', fontsize=14)
    plt.xlabel('人数', fontsize=12)
    plt.ylabel('行业', fontsize=12)


    # 子图2：行业财富总值TOP15
    plt.subplot(2, 2, 2)
    top15_wealth = industry_stats.head(15)
    sns.barplot(
        x='财富总值_亿',
        y=top15_wealth.index,
        data=top15_wealth,
        palette = 'plasma',
        legend = False
    )
    plt.title('各行业财富总值TOP15', fontsize=14)
    plt.xlabel('财富总额（亿元）', fontsize=12)


    # 子图3：行业平均财富对比
    plt.subplot(2, 2, 3)
    avg_wealth = industry_stats[industry_stats['富豪数量'] > 3]  # 过滤小众行业
    avg_wealth = avg_wealth.sort_values('平均财富_亿', ascending=False).head(10)
    sns.barplot(
        x='平均财富_亿',
        y=avg_wealth.index,
        data=avg_wealth,
        palette='coolwarm',
        legend = False
    )
    plt.title('各行业富豪平均财富TOP10', fontsize=14)
    plt.xlabel('平均财富（亿元）', fontsize=12)


    # 子图4：行业财富占比饼图
    plt.subplot(2, 2, 4)
    wealth_share = industry_stats.head(10)  # 取前10大行业
    plt.pie(
        wealth_share['财富占比'],
        labels=wealth_share.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=sns.color_palette('pastel')
    )
    plt.title('行业财富分布占比', fontsize=14)


    plt.tight_layout()
    plt.savefig('行业财富分析可视化-具体行业.png', dpi=300, bbox_inches='tight')
    plt.show()


# 行业趋势分析
def trend_analysis(df):
    """分析行业发展趋势"""
    # 计算行业财富集中度（前5大行业占比）
    industry_stats = analyze_industries(df)
    top5_wealth = industry_stats.head(5)['财富总值_亿'].sum()
    print(f"\n行业集中度分析：前5大行业财富占比 {top5_wealth / industry_stats['财富总值_亿'].sum() * 100:.1f}%")

    # 找出高增长行业（财富增速>20%的行业）
    # 注意：原数据无历史对比，此处仅为示例逻辑
    # 实际应用中需要历年数据对比
    print("\n潜在高增长行业（需历史数据验证）：")
    print("1. 半导体：技术壁垒高，国产替代加速")
    print("2. 锂电池：新能源赛道持续火热")
    print("3. 生物医药：创新药研发投入加大")


# 主程序
if __name__ == "__main__":
    # 数据加载
    file_path = '2024胡润百富榜.csv'
    try:
        df = pd.read_csv(file_path)

        # 行业分析
        industry_stats = analyze_industries(df)
        print("=== 各行业财富分析 ===")
        print(industry_stats.head(15))

        # 可视化
        visualize_data(industry_stats)

        # 趋势分析
        trend_analysis(df)

        # 保存详细数据
        industry_stats.to_csv('行业财富分析结果-具体行业.csv', encoding='utf-8-sig')
        print("\n详细分析结果已保存至：行业财富分析结果-具体行业.csv")

    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到，请确认路径")
    except Exception as e:
        print(f"分析过程中发生错误：{str(e)}")