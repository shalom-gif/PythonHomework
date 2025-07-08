import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


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

    # 计算行业富豪占比
    total_people = len(df)
    industry_stats['富豪占比'] = (industry_stats['富豪数量'] / total_people * 100).round(2)

    # 计算行业财富集中度（财富总值/富豪数量）
    industry_stats['财富集中度'] = (industry_stats['财富总值_亿'] / industry_stats['富豪数量']).round(2)

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
        palette='plasma',
        legend=False
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
        legend=False
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
    analysis_result = []

    # 1. 行业集中度分析
    top5_wealth = industry_stats.head(5)['财富总值_亿'].sum()
    top5_percentage = top5_wealth / industry_stats['财富总值_亿'].sum() * 100
    analysis_result.append(f"行业集中度分析：前5大行业财富占比 {top5_percentage:.1f}%")

    # 2. 识别高潜力行业
    # 定义潜力行业标准：富豪数量增长快 OR 平均财富高 OR 财富集中度高
    industry_stats['潜力得分'] = (
            0.4 * industry_stats['富豪数量'].rank(pct=True) +
            0.3 * industry_stats['平均财富_亿'].rank(pct=True) +
            0.3 * industry_stats['财富集中度'].rank(pct=True)
    )

    high_potential = industry_stats.nlargest(5, '潜力得分')
    analysis_result.append("\n高潜力行业分析（基于富豪数量、平均财富和财富集中度）：")
    for idx, (industry, row) in enumerate(high_potential.iterrows(), 1):
        analysis_result.append(f"{idx}. {industry}: "
                               f"富豪数量={row['富豪数量']}人, "
                               f"平均财富={row['平均财富_亿']:.1f}亿, "
                               f"财富集中度={row['财富集中度']:.1f}")

    # 3. 识别成熟行业
    mature_industries = industry_stats[
        (industry_stats['富豪数量'] > industry_stats['富豪数量'].median()) &
        (industry_stats['平均财富_亿'] > industry_stats['平均财富_亿'].median())
        ].sort_values('财富总值_亿', ascending=False).head(5)

    analysis_result.append("\n成熟稳定行业（富豪数量多且平均财富高）：")
    for idx, (industry, row) in enumerate(mature_industries.iterrows(), 1):
        analysis_result.append(f"{idx}. {industry}: "
                               f"富豪数量={row['富豪数量']}人, "
                               f"财富总值={row['财富总值_亿']:.0f}亿")

    # 4. 识别新兴行业
    emerging_industries = industry_stats[
        (industry_stats['富豪数量'] < industry_stats['富豪数量'].quantile(0.3)) &
        (industry_stats['平均财富_亿'] > industry_stats['平均财富_亿'].median())
        ].sort_values('平均财富_亿', ascending=False)

    if not emerging_industries.empty:
        analysis_result.append("\n新兴高价值行业（富豪数量少但平均财富高）：")
        for idx, (industry, row) in enumerate(emerging_industries.head(3).iterrows(), 1):
            analysis_result.append(f"{idx}. {industry}: "
                                   f"富豪数量={row['富豪数量']}人, "
                                   f"平均财富={row['平均财富_亿']:.1f}亿")
    else:
        analysis_result.append("\n未识别到明显的新兴高价值行业")

    # 5. 行业发展趋势预测
    analysis_result.append("\n行业发展趋势预测：")
    analysis_result.append("- 科技行业（如半导体、人工智能）将继续保持高增长，受益于国家政策支持和市场需求")
    analysis_result.append("- 新能源行业（如锂电池、光伏）将面临行业整合，头部企业优势更加明显")
    analysis_result.append("- 传统行业（如房地产、建材）将进入深度调整期，财富集中度可能进一步提高")
    analysis_result.append("- 大健康产业（如生物医药、医疗器械）将迎来发展机遇，平均财富可能提升")

    return "\n".join(analysis_result)


# 主程序
if __name__ == "__main__":
    # 数据加载
    file_path = '2024胡润百富榜.csv'
    try:
        df = pd.read_csv(file_path)

        # 行业分析
        industry_stats = analyze_industries(df)
        industry_stats.to_csv('行业财富分析结果-具体行业.csv', encoding='utf-8-sig')
        print("\n行业统计分析结果已保存至：行业财富分析结果-具体行业.csv")

        # 趋势分析
        trend_report = trend_analysis(industry_stats)
        with open('行业发展趋势分析报告-具体行业.txt', 'w', encoding='utf-8') as f:
            f.write(trend_report)
        print("\n行业发展趋势分析报告已保存至：行业发展趋势分析报告.txt")

        # 可视化
        visualize_data(industry_stats)

    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到，请确认路径")
    except Exception as e:
        print(f"分析过程中发生错误：{str(e)}")