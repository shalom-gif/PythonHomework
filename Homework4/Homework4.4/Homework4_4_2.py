import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TkAgg')  # 或 'Qt5Agg'
import seaborn as sns
import numpy as np
from scipy.stats import pearsonr

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def load_data():
    """加载专家数据"""
    try:
        df = pd.read_csv('大乐透收费专家20码排行榜各专家信息.csv', encoding='utf_8_sig')
        print("数据加载成功，共{}条记录".format(len(df)))
        return df
    except Exception as e:
        print("数据加载失败:", e)
        return None


def analyze_data(df):
    """执行数据分析"""
    analysis_results = {}

    # 数据预处理 - 确保'成功率'是字符串类型后再处理
    if '成功率' in df.columns:
        # 先转换为字符串，再处理百分比
        df['成功率'] = df['成功率'].astype(str).str.rstrip('%').astype('float') / 100
        df['中奖率'] = df['成功率']  # 直接使用已转换的成功率

    # 处理"大乐透一等奖"等列中的"7中6"格式
    for col in ['大乐透一等奖', '大乐透二等奖', '大乐透三等奖']:
        if col in df.columns:
            # 先转换为字符串，再提取数字
            df[col] = df[col].astype(str).str.extract(r'(\d+)').astype('float')

    # 基本统计量
    analysis_results['basic_stats'] = df.describe(include='all').round(2)

    # 相关性分析 - 只选择数值列
    numeric_cols = ['成功率', '粉丝数', '彩龄', '文章数量',  # 删除了'成绩'
                    '大乐透一等奖', '大乐透二等奖', '大乐透三等奖']
    numeric_cols = [col for col in numeric_cols if col in df.columns]

    # 确保所有选择的列都是数值类型
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            # 先转换为字符串，再转换为数值
            df[col] = pd.to_numeric(df[col].astype(str), errors='coerce')

    corr_matrix = df[numeric_cols].corr().round(2)
    analysis_results['correlation'] = corr_matrix

    # 等级分布
    if '等级' in df.columns:
        grade_dist = df['等级'].value_counts(normalize=True).round(3)
        analysis_results['grade_dist'] = grade_dist

    # 中奖率分析
    if '中奖率' in df.columns:
        analysis_results['award_rate_stats'] = df['中奖率'].describe().round(3)

    return df, analysis_results


def create_visualizations(df, analysis_results):
    """创建可视化图表并保存"""
    corr_matrix = analysis_results['correlation']

    # 1. 相关性热力图
    plt.figure(figsize=(12, 8))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='YlOrRd',
                center=0, vmin=-1, vmax=1, linewidths=0.5)
    plt.title('专家特征相关性热力图', fontsize=15)
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig('专家特征相关性热力图.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 2. 中奖率分布图
    if '中奖率' in df.columns:
        plt.figure(figsize=(10, 6))
        plt.hist(df['中奖率'].dropna(), bins=20, color='skyblue', edgecolor='black')
        plt.title('专家中奖率分布', fontsize=15)
        plt.xlabel('中奖率', fontsize=12)
        plt.ylabel('专家数量', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('专家中奖率分布.png', dpi=300)
        plt.show()

    # 3. 彩龄与中奖率关系图
    if '彩龄' in df.columns and '中奖率' in df.columns:
        plt.figure(figsize=(10, 6))
        plt.scatter(df['彩龄'], df['中奖率'], alpha=0.6, color='green')
        plt.title('彩龄与中奖率关系', fontsize=15)
        plt.xlabel('彩龄(年)', fontsize=12)
        plt.ylabel('中奖率', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)

        # 添加趋势线
        valid_data = df[['彩龄', '中奖率']].dropna()
        if len(valid_data) > 1:
            z = np.polyfit(valid_data['彩龄'], valid_data['中奖率'], 1)
            p = np.poly1d(z)
            plt.plot(valid_data['彩龄'], p(valid_data['彩龄']), "r--")

            # 添加相关系数标注
            r = np.corrcoef(valid_data['彩龄'], valid_data['中奖率'])[0, 1]
            plt.text(0.05, 0.95, f'相关系数 r = {r:.2f}',
                     transform=plt.gca().transAxes,
                     fontsize=12, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig('彩龄与中奖率关系.png', dpi=300)
        plt.show()

    # 4. 文章数量与中奖率关系图
    if '文章数量' in df.columns and '中奖率' in df.columns:
        plt.figure(figsize=(10, 6))
        plt.scatter(df['文章数量'], df['中奖率'], alpha=0.6, color='blue')  # 使用蓝色表示文章相关

        # 添加标题和标签
        plt.title('文章数量与中奖率关系', fontsize=15)
        plt.xlabel('文章数量(篇)', fontsize=12)
        plt.ylabel('中奖率', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)

        # 添加趋势线
        valid_data = df[['文章数量', '中奖率']].dropna()
        if len(valid_data) > 1:
            z = np.polyfit(valid_data['文章数量'], valid_data['中奖率'], 1)  # 线性拟合
            p = np.poly1d(z)
            plt.plot(valid_data['文章数量'], p(valid_data['文章数量']), "m--")  # 使用品红色虚线

            # 添加相关系数标注
            r = np.corrcoef(valid_data['文章数量'], valid_data['中奖率'])[0, 1]
            plt.text(0.05, 0.95, f'相关系数 r = {r:.2f}',
                     transform=plt.gca().transAxes,
                     fontsize=12, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig('文章数量与中奖率关系.png', dpi=300)
        plt.show()


def main():
    print("开始分析大乐透专家数据...")

    df = load_data()
    if df is None:
        return

    df, analysis_results = analyze_data(df)
    create_visualizations(df, analysis_results)

    print("分析完成! 已保存可视化图表")


if __name__ == "__main__":
    main()