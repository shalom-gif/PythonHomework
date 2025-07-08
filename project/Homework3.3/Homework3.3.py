import os
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文

# 设置文件夹路径
base_path = r"D:\Homework3\project"
conference_path = os.path.join(base_path, "Homework3.1")  # 直接指向conference文件夹

high_freq_path = os.path.join(base_path, "Homework3.3")
os.makedirs(high_freq_path, exist_ok=True)

# 定义年份范围
years = range(2020, 2025)

# 停用词
english_stopwords = {
    "the", "and", "of", "in", "to", "a", "an", "for", "on", "with", "by", "at",
    "from", "is", "are", "as", "be", "this", "that", "it", "we", "our", "you",
    "your", "their", "its", "they", "or", "not", "but", "if", "then", "else",
    "when", "where", "how", "what", "which", "why", "who", "whom", "whose",
}


# 创建一个函数来提取关键词
def extract_keywords(text):
    # 转换为小写
    text = text.lower()

    # 使用正则表达式分词
    words = re.findall(r'\b\w+\b', text)

    # 过滤停用词、短词和纯数字
    keywords = [
        word for word in words
        if (word not in english_stopwords and
            len(word) > 2 and
            not word.isdigit())
    ]

    return keywords

# 存储每年的关键词数据
yearly_keywords = {}
yearly_frequencies = {}
all_titles_count = 0

# 确保输出目录存在
os.makedirs(base_path, exist_ok=True)

# 初始化每年标题列表
yearly_titles = {year: [] for year in years}

# 直接遍历conference文件夹中的CSV文件
print(f"扫描会议文件夹: {conference_path}")
for filename in os.listdir(conference_path):
    if filename.endswith(".csv"):
        # 从文件名中提取年份
        match = re.search(r'_(\d{4})_', filename)
        if match:
            year = int(match.group(1))
            if year in years:
                csv_file = os.path.join(conference_path, filename)
                try:
                    df = pd.read_csv(csv_file)
                    if 'title' in df.columns:
                        titles = df['title'].dropna().tolist()  # 去除NaN值
                        yearly_titles[year].extend(titles)
                        print(f"在 {filename} 中找到 {len(titles)} 个标题")
                    else:
                        print(f"CSV文件缺少'title'列: {filename}")
                except Exception as e:
                    print(f"读取文件错误 {filename}: {str(e)}")
        else:
            print(f"跳过文件(未找到年份): {filename}")

# 处理每年的标题
for year in years:
    all_titles = yearly_titles[year]
    all_titles_count += len(all_titles)

    # 提取关键词
    all_keywords = []
    for title in all_titles:
        if isinstance(title, str):
            keywords = extract_keywords(title)
            all_keywords.extend(keywords)

    print(f"\n年份 {year}: 总标题数: {len(all_titles)} | 总关键词数: {len(all_keywords)}")

    # 保存关键词和频率
    yearly_keywords[year] = all_keywords
    keyword_freq = Counter(all_keywords)
    yearly_frequencies[year] = keyword_freq

    # 生成词云
    if len(all_keywords) >= 10:
        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color="white",
            max_words=200,
            collocations=False,
            font_path='simhei.ttf'  # 支持中文的字体
        ).generate_from_frequencies(keyword_freq)

        # 保存词云到high_frequency文件夹
        output_path = os.path.join(high_freq_path, f"wordcloud_{year}.png")
        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"{year}年研究热点词云图", fontsize=20)
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        print(f"词云已保存: {output_path}")
    else:
        print(f"{year}年关键词不足，无法生成词云")


# 创建关键词趋势分析数据框架
# 获取所有年份的所有关键词
all_keywords_set = set()
for year in years:
    all_keywords_set.update(yearly_frequencies[year].keys())

# 创建数据框架
trend_df = pd.DataFrame(index=list(all_keywords_set), columns=years)

# 填充频率数据
for year in years:
    freq_dict = yearly_frequencies[year]
    for keyword in trend_df.index:
        trend_df.at[keyword, year] = freq_dict.get(keyword, 0)

# 计算总频率
trend_df['total'] = trend_df.sum(axis=1)

# 只保留总频率前100的关键词
if not trend_df.empty:
    top_keywords = trend_df.sort_values('total', ascending=False).head(100).index
    trend_df = trend_df.loc[top_keywords]

    # 删除总频率列
    trend_df = trend_df.drop(columns=['total'])

    # 1. 关键词趋势可视化
    # 更相关的研究主题关键词
    selected_keywords = [
        'transformer', 'attention', 'contrastive', 'generative',
        'diffusion', 'robust', 'efficient', 'federated',
        'graph', 'reinforcement', 'selfsupervised', 'vision',
        'language', 'detection', 'segmentation', 'classification',
        'optimization', 'privacy', 'security', 'adversarial'
    ]

    # 只选择在数据中存在的关键词
    selected_keywords = [word for word in selected_keywords if word in trend_df.index]

    if selected_keywords:
        plt.figure(figsize=(14, 8))

        # 创建颜色映射
        colors = plt.cm.tab20(np.linspace(0, 1, len(selected_keywords)))

        for i, keyword in enumerate(selected_keywords):
            plt.plot(years, trend_df.loc[keyword], 'o-',
                     label=keyword, linewidth=2.5, markersize=8,
                     color=colors[i])

        plt.title('人工智能研究热点趋势 (2020-2024)', fontsize=18)
        plt.xlabel('年份', fontsize=14)
        plt.ylabel('出现频率', fontsize=14)
        plt.legend(fontsize=10, ncol=2)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(years, fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()

        # 保存趋势图到high_frequency文件夹
        output_path = os.path.join(high_freq_path, 'research_trends.png')
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"研究趋势图保存至: {output_path}")
    else:
        print("没有找到选定的关键词数据。")
else:
    print("没有足够的数据进行趋势分析。")

print("\n分析完成! 所有文件已保存在 high_frequency 文件夹中。")