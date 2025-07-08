import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 1. 数据加载与预处理
print("正在加载数据...")
df = pd.read_csv('2024胡润百富榜.csv')

# 数据清洗
df['财富(人民币/亿)'] = pd.to_numeric(df['财富(人民币/亿)'], errors='coerce')
df['个人信息_年龄'] = pd.to_numeric(df['个人信息_年龄'], errors='coerce')
df['财富变化'] = df['财富变化'].str.replace('%', '').str.replace('—', '0').str.replace('新', '0')
df['财富变化'] = pd.to_numeric(df['财富变化'], errors='coerce') / 100

# 提取省份信息
def extract_province(location):
    if pd.isna(location):
        return '未知'
    if '中国' in location:
        parts = location.split('-')
        return parts[1] if len(parts) > 1 else location
    return location

df['出生省份'] = df['个人信息_出生地_中文'].apply(extract_province)
df['出生省份'] = df['出生省份'].str.replace('自治区', '').str.replace('省', '').str.replace('市', '')

df['常住省份'] = df['个人信息_常住地_中文'].apply(extract_province)
df['常住省份'] = df['常住省份'].str.replace('自治区', '').str.replace('省', '').str.replace('市', '')

# 教育程度分类
education_map = {
    '本科': '本科',
    '硕士': '硕士',
    '博士': '博士',
    '研究生': '硕士',
    'MBA': '硕士',
    'EMBA': '硕士',
    '博士后': '博士',
    '大学': '本科',
    '学士': '本科',
    '高中': '高中及以下',
    '初中': '高中及以下',
    '小学': '高中及以下',
    '中专': '高中及以下',
    '大专': '专科',
    '专科': '专科',
    '无': '未知',
    '': '未知'
}

df['教育程度'] = df['个人信息_教育程度_中文'].fillna('未知').map(education_map).fillna('未知')

# 年龄分段
bins = [20, 30, 40, 50, 60, 70, 80, 100]
labels = ['20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
df['年龄分段'] = pd.cut(df['个人信息_年龄'], bins=bins, labels=labels, right=False)

# 财富层级
bins = [0, 100, 500, 1000, 2000, 5000, 10000]
labels = ['<100亿', '100-500亿', '500-1000亿', '1000-2000亿', '2000-5000亿', '5000亿+']
df['财富层级'] = pd.cut(df['财富(人民币/亿)'], bins=bins, labels=labels, right=False)

print("数据预处理完成!")

# ========================== 1. 年龄分析 ==========================
print("年龄分析大类图!")
fig = plt.figure(figsize=(20, 12))
fig.suptitle('富豪年龄分析', fontsize=24, fontweight='bold')

# 1.1 年龄分布直方图
ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=1)
sns.histplot(df['个人信息_年龄'].dropna(), bins=30, kde=True, color='royalblue', alpha=0.7, ax=ax1)
ax1.set_title('富豪年龄分布', fontsize=16, fontweight='bold')
ax1.set_xlabel('年龄', fontsize=12)
ax1.set_ylabel('人数', fontsize=12)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 1.2 年龄分段分析
ax2 = plt.subplot2grid((2, 2), (0, 1), colspan=1)
age_group = df['年龄分段'].value_counts().sort_index()
age_group_wealth = df.groupby('年龄分段')['财富(人民币/亿)'].mean()

color = '#1f77b4'
ax2.set_xlabel('年龄分段', fontsize=12)
ax2.set_ylabel('人数', color=color, fontsize=12)
ax2.bar(age_group.index, age_group.values, color=color, alpha=0.7)
ax2.tick_params(axis='y', labelcolor=color)
ax2.grid(axis='y', linestyle='--', alpha=0.3)

ax3 = ax2.twinx()
color = '#d62728'
ax3.set_ylabel('平均财富 (亿人民币)', color=color, fontsize=12)
ax3.plot(age_group_wealth.index, age_group_wealth.values, color=color, marker='o',
         linewidth=3, markersize=8)
ax3.tick_params(axis='y', labelcolor=color)
ax2.set_title('不同年龄段富豪数量及平均财富', fontsize=16, fontweight='bold')

# 1.3 年龄与财富关系
ax4 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
sns.scatterplot(
    x='个人信息_年龄',
    y='财富(人民币/亿)',
    hue='个人信息_性别',
    size='财富(人民币/亿)',
    sizes=(20, 500),
    alpha=0.7,
    palette='Set1',
    data=df,
    ax=ax4
)
ax4.set_title('富豪年龄与财富关系', fontsize=16, fontweight='bold')
ax4.set_xlabel('年龄', fontsize=12)
ax4.set_ylabel('财富 (亿人民币)', fontsize=12)
ax4.set_yscale('log')
ax4.grid(True, linestyle='--', alpha=0.3)
ax4.legend(title='性别', loc='upper right')

plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为标题留出空间
plt.savefig('年龄分析大类图.png', dpi=300, bbox_inches='tight')
plt.show()

# ========================== 2. 性别分析 ==========================
print("性别分析大类图!")
fig = plt.figure(figsize=(18, 8))
fig.suptitle('富豪性别分析', fontsize=24, fontweight='bold')

# 2.1 性别分布饼图
ax1 = plt.subplot(1, 2, 1)
gender_counts = df['个人信息_性别'].value_counts()
gender_counts = gender_counts[gender_counts.index != '']  # 移除空值

ax1.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%',
        colors=['#66c2a5', '#fc8d62', '#8da0cb'], startangle=90,
        textprops={'fontsize': 12}, explode=(0.05, 0, 0))
ax1.set_title('性别分布', fontsize=16, fontweight='bold')

# 2.2 性别与财富关系
ax2 = plt.subplot(1, 2, 2)
gender_wealth = df.groupby('个人信息_性别')['财富(人民币/亿)'].mean().sort_values(ascending=False)
gender_wealth = gender_wealth[gender_wealth.index != '']  # 移除空值

sns.barplot(x=gender_wealth.index, y=gender_wealth.values, palette='pastel', ax=ax2)
ax2.set_title('不同性别平均财富', fontsize=16, fontweight='bold')
ax2.set_xlabel('性别', fontsize=12)
ax2.set_ylabel('平均财富 (亿人民币)', fontsize=12)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('性别分析大类图.png', dpi=300, bbox_inches='tight')
plt.show()

# ========================== 3. 出生地与常住地分析 ==========================
print("出生地与常住地分析大类图!")
fig = plt.figure(figsize=(20, 12))
fig.suptitle('富豪出生地与常住地分析', fontsize=24, fontweight='bold')

# 3.1 出生地分布TOP15
ax1 = plt.subplot(2, 2, 1)
birth_province_counts = df['出生省份'].value_counts().head(15)

sns.barplot(x=birth_province_counts.values, y=birth_province_counts.index, palette='viridis', ax=ax1)
ax1.set_title('出生地TOP15省份', fontsize=16, fontweight='bold')
ax1.set_xlabel('富豪数量', fontsize=12)
ax1.set_ylabel('省份', fontsize=12)
ax1.grid(axis='x', linestyle='--', alpha=0.7)

# 3.2 常住地分布TOP15
ax2 = plt.subplot(2, 2, 2)
residence_province_counts = df['常住省份'].value_counts().head(15)

sns.barplot(x=residence_province_counts.values, y=residence_province_counts.index, palette='magma', ax=ax2)
ax2.set_title('常住地TOP15省份', fontsize=16, fontweight='bold')
ax2.set_xlabel('富豪数量', fontsize=12)
ax2.set_ylabel('省份', fontsize=12)
ax2.grid(axis='x', linestyle='--', alpha=0.7)

# 3.3 省份比较柱状图
ax3 = plt.subplot(2, 1, 2)
province_birth_counts = df['出生省份'].value_counts().reset_index()
province_birth_counts.columns = ['省份', '富豪数量']
province_residence_counts = df['常住省份'].value_counts().reset_index()
province_residence_counts.columns = ['省份', '富豪数量']

# 合并出生地和常住地数据
birth_residence_compare = pd.DataFrame({
    '出生地': province_birth_counts.set_index('省份')['富豪数量'],
    '常住地': province_residence_counts.set_index('省份')['富豪数量']
}).fillna(0)

# 只取TOP15省份
top_provinces = birth_residence_compare.sum(axis=1).sort_values(ascending=False).head(15).index
birth_residence_compare = birth_residence_compare.loc[top_provinces]

# 绘制柱状图
birth_residence_compare.plot(kind='bar', figsize=(16, 8), color=['#FF8C00', '#1E90FF'], ax=ax3)
ax3.set_title('TOP15省份出生地与常住地富豪数量比较', fontsize=16, fontweight='bold')
ax3.set_xlabel('省份', fontsize=12)
ax3.set_ylabel('富豪数量', fontsize=12)
ax3.grid(axis='y', linestyle='--', alpha=0.7)
ax3.legend(title='分布类型')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('出生地与常住地分析大类图.png', dpi=300, bbox_inches='tight')
plt.show()

# ========================== 4. 教育程度分析 ==========================
print("教育程度分析大类图!")
fig = plt.figure(figsize=(18, 12))
fig.suptitle('富豪教育程度分析', fontsize=24, fontweight='bold')

# 4.1 教育程度分布
ax1 = plt.subplot(2, 2, 1)
education_counts = df['教育程度'].value_counts()

sns.barplot(x=education_counts.values, y=education_counts.index, palette='coolwarm', ax=ax1)
ax1.set_title('教育程度分布', fontsize=16, fontweight='bold')
ax1.set_xlabel('人数', fontsize=12)
ax1.set_ylabel('教育程度', fontsize=12)
ax1.grid(axis='x', linestyle='--', alpha=0.7)

# 4.2 教育程度与财富关系
ax2 = plt.subplot(2, 2, 2)
education_wealth = df.groupby('教育程度')['财富(人民币/亿)'].mean().sort_values(ascending=False)

sns.barplot(x=education_wealth.values, y=education_wealth.index, palette='plasma', ax=ax2)
ax2.set_title('不同教育程度平均财富', fontsize=16, fontweight='bold')
ax2.set_xlabel('平均财富 (亿人民币)', fontsize=12)
ax2.set_ylabel('教育程度', fontsize=12)
ax2.grid(axis='x', linestyle='--', alpha=0.7)

# 4.3 教育程度与年龄关系
ax3 = plt.subplot(2, 1, 2)
sns.boxplot(x='教育程度', y='个人信息_年龄', data=df, palette='Set2',
            order=['高中及以下', '专科', '本科', '硕士', '博士'], ax=ax3)
ax3.set_title('不同教育程度富豪年龄分布', fontsize=16, fontweight='bold')
ax3.set_xlabel('教育程度', fontsize=12)
ax3.set_ylabel('年龄', fontsize=12)
ax3.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('教育程度分析大类图.png', dpi=300, bbox_inches='tight')
plt.show()

# ========================== 5. 财富分析 ==========================
print("财富分析大类图!")
fig = plt.figure(figsize=(18, 12))
fig.suptitle('富豪财富分析', fontsize=24, fontweight='bold')

# 5.1 财富分布直方图
ax1 = plt.subplot(2, 2, 1)
sns.histplot(df['财富(人民币/亿)'], bins=50, kde=True, color='green', alpha=0.6, ax=ax1)
ax1.set_title('财富分布', fontsize=16, fontweight='bold')
ax1.set_xlabel('财富值 (亿人民币)', fontsize=12)
ax1.set_ylabel('人数', fontsize=12)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 5.2 财富层级分布
ax2 = plt.subplot(2, 2, 2)
wealth_level = df['财富层级'].value_counts().sort_index()

sns.barplot(x=wealth_level.index, y=wealth_level.values, palette='viridis', ax=ax2)
ax2.set_title('财富层级分布', fontsize=16, fontweight='bold')
ax2.set_xlabel('财富层级 (亿人民币)', fontsize=12)
ax2.set_ylabel('人数', fontsize=12)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# 5.3 财富变化分布
ax3 = plt.subplot(2, 1, 2)
sns.histplot(df['财富变化'].dropna(), bins=30, kde=True, color='purple', alpha=0.6, ax=ax3)
ax3.set_title('财富变化分布', fontsize=16, fontweight='bold')
ax3.set_xlabel('财富变化率', fontsize=12)
ax3.set_ylabel('人数', fontsize=12)
ax3.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('财富分析大类图.png', dpi=300, bbox_inches='tight')
plt.show()

# ========================== 6. 行业分析 ==========================
print("行业分析大类图!")
fig = plt.figure(figsize=(20, 12))
fig.suptitle('富豪行业分析', fontsize=24, fontweight='bold')

# 6.1 行业分布TOP15
ax1 = plt.subplot(2, 2, 1)
industry_counts = df['企业信息_行业_中文'].value_counts().head(15)

sns.barplot(x=industry_counts.values, y=industry_counts.index, palette='coolwarm', ax=ax1)
ax1.set_title('行业分布TOP15', fontsize=16, fontweight='bold')
ax1.set_xlabel('富豪数量', fontsize=12)
ax1.set_ylabel('行业', fontsize=12)
ax1.grid(axis='x', linestyle='--', alpha=0.7)

# 6.2 行业平均财富TOP15
ax2 = plt.subplot(2, 2, 2)
industry_wealth = df.groupby('企业信息_行业_中文')['财富(人民币/亿)'].mean().sort_values(ascending=False).head(15)

sns.barplot(x=industry_wealth.values, y=industry_wealth.index, palette='plasma', ax=ax2)
ax2.set_title('行业平均财富TOP15', fontsize=16, fontweight='bold')
ax2.set_xlabel('平均财富 (亿人民币)', fontsize=12)
ax2.set_ylabel('行业', fontsize=12)
ax2.grid(axis='x', linestyle='--', alpha=0.7)

# 6.3 行业、年龄与财富关系
ax3 = plt.subplot(2, 1, 2)
top_industries = df['企业信息_行业_中文'].value_counts().head(10).index
top_df = df[df['企业信息_行业_中文'].isin(top_industries)]

sns.scatterplot(
    x='个人信息_年龄',
    y='财富(人民币/亿)',
    hue='企业信息_行业_中文',
    size='财富(人民币/亿)',
    sizes=(20, 500),
    alpha=0.7,
    palette='tab10',
    data=top_df,
    ax=ax3
)
ax3.set_title('TOP10行业富豪年龄与财富关系', fontsize=16, fontweight='bold')
ax3.set_xlabel('年龄', fontsize=12)
ax3.set_ylabel('财富 (亿人民币)', fontsize=12)
ax3.set_yscale('log')
ax3.grid(True, linestyle='--', alpha=0.3)
ax3.legend(title='行业', loc='upper right')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('行业分析大类图.png', dpi=300, bbox_inches='tight')
plt.show()

# ========================== 7. 地理分布分析 ==========================
print("地理分布分析大类图!")
# 创建中国省份坐标映射
province_coords = {
    '北京': (116.4, 39.9), '天津': (117.2, 39.1), '河北': (114.5, 38.0),
    '山西': (112.5, 37.9), '内蒙古': (111.7, 40.8), '辽宁': (123.4, 41.8),
    '吉林': (125.3, 43.9), '黑龙江': (126.6, 45.8), '上海': (121.5, 31.2),
    '江苏': (118.8, 32.1), '浙江': (120.2, 30.3), '安徽': (117.3, 31.8),
    '福建': (119.3, 26.1), '江西': (115.9, 28.7), '山东': (117.0, 36.7),
    '河南': (113.7, 34.8), '湖北': (114.3, 30.6), '湖南': (113.0, 28.2),
    '广东': (113.3, 23.1), '广西': (108.3, 22.8), '海南': (110.3, 20.0),
    '重庆': (106.5, 29.5), '四川': (104.1, 30.7), '贵州': (106.7, 26.6),
    '云南': (102.7, 25.0), '西藏': (91.1, 29.6), '陕西': (108.9, 34.3),
    '甘肃': (103.8, 36.0), '青海': (101.8, 36.6), '宁夏': (106.3, 38.5),
    '新疆': (87.6, 43.8), '台湾': (121.5, 25.0), '香港': (114.2, 22.3),
    '澳门': (113.5, 22.2), '未知': (100.0, 20.0),'新加坡':(100.0,20.0)
}

# 准备数据
province_birth_counts = df['出生省份'].value_counts().reset_index()
province_birth_counts.columns = ['省份', '富豪数量']
province_birth_counts['经度'] = province_birth_counts['省份'].map(lambda x: province_coords.get(x, (0, 0))[0])
province_birth_counts['纬度'] = province_birth_counts['省份'].map(lambda x: province_coords.get(x, (0, 0))[1])
province_birth_counts = province_birth_counts[province_birth_counts['省份'] != '未知']

province_residence_counts = df['常住省份'].value_counts().reset_index()
province_residence_counts.columns = ['省份', '富豪数量']
province_residence_counts['经度'] = province_residence_counts['省份'].map(lambda x: province_coords.get(x, (0, 0))[0])
province_residence_counts['纬度'] = province_residence_counts['省份'].map(lambda x: province_coords.get(x, (0, 0))[1])
province_residence_counts = province_residence_counts[province_residence_counts['省份'] != '未知']

# 创建图表
fig = plt.figure(figsize=(20, 20))
fig.suptitle('富豪地理分布分析', fontsize=24, fontweight='bold')
plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.15, wspace=0.3, hspace=0.4)
# 7.1 出生地地理分布热力图
ax1 = plt.subplot(2, 2, 1)
ax1.scatter(
    province_birth_counts['经度'],
    province_birth_counts['纬度'],
    s=province_birth_counts['富豪数量']*5,
    c=province_birth_counts['富豪数量'],
    cmap='YlOrRd',
    alpha=0.7
)

for i, row in province_birth_counts.iterrows():
    if row['富豪数量'] > 5:
        ax1.text(
            row['经度'] + 0.5,
            row['纬度'] + 0.5,
            f"{row['省份']}({row['富豪数量']})",
            fontsize=10,
            ha='center'
        )

ax1.set_title('出生地分布', fontsize=16, fontweight='bold')
ax1.set_xlabel('经度', fontsize=12)
ax1.set_ylabel('纬度', fontsize=12)
ax1.set_xlim(100, 130)
ax1.set_ylim(20, 45)
ax1.grid(True, linestyle='--', alpha=0.5)

# 7.2 常住地地理分布热力图
ax2 = plt.subplot(2, 2, 2)
ax2.scatter(
    province_residence_counts['经度'],
    province_residence_counts['纬度'],
    s=province_residence_counts['富豪数量']*5,
    c=province_residence_counts['富豪数量'],
    cmap='Blues',
    alpha=0.7
)

for i, row in province_residence_counts.iterrows():
    if row['富豪数量'] > 5:
        ax2.text(
            row['经度'] + 0.5,
            row['纬度'] + 0.5,
            f"{row['省份']}({row['富豪数量']})",
            fontsize=10,
            ha='center'
        )

ax2.set_title('常住地分布', fontsize=16, fontweight='bold')
ax2.set_xlabel('经度', fontsize=12)
ax2.set_ylabel('纬度', fontsize=12)
ax2.set_xlim(100, 130)
ax2.set_ylim(20, 45)
ax2.grid(True, linestyle='--', alpha=0.5)

# 7.3 省份比较柱状图
ax3 = plt.subplot(2, 1, 2)
birth_residence_compare = pd.DataFrame({
    '出生地': province_birth_counts.set_index('省份')['富豪数量'],
    '常住地': province_residence_counts.set_index('省份')['富豪数量']
}).fillna(0)
top_provinces = birth_residence_compare.sum(axis=1).sort_values(ascending=False).head(15).index
birth_residence_compare = birth_residence_compare.loc[top_provinces]
birth_residence_compare.plot(kind='bar', color=['#FF8C00', '#1E90FF'], ax=ax3)
ax3.set_title('TOP15省份出生地与常住地富豪数量比较', fontsize=16, fontweight='bold')
ax3.set_xlabel('省份', fontsize=12)
ax3.set_ylabel('富豪数量', fontsize=12)
ax3.grid(axis='y', linestyle='--', alpha=0.7)
ax3.legend(title='分布类型')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('地理分布分析大类图.png', dpi=300, bbox_inches='tight')
plt.show()

# ========================== 8. 毕业院校分析 ==========================
print("毕业院校分析大类图!")
fig = plt.figure(figsize=(20, 12))
fig.suptitle('富豪毕业院校分析', fontsize=24, fontweight='bold')
plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.15, wspace=0.5)
# 8.1 毕业院校词云
ax1 = plt.subplot(1, 2, 1)
school_text = ' '.join(df['个人信息_毕业院校'].dropna().astype(str))
stopwords = set(['大学', '学院', '学校', '中国', '北京', '上海', '浙江', '江苏', '广东'])

wordcloud = WordCloud(
    font_path='C:/Windows/Fonts/simhei.ttf',
    background_color='white',
    width=1200,
    height=800,
    max_words=150,
    stopwords=stopwords,
    colormap='viridis'
).generate(school_text)

ax1.imshow(wordcloud, interpolation='bilinear')
ax1.axis('off')
ax1.set_title('毕业院校词云', fontsize=20, fontweight='bold')

# 8.2 TOP20毕业院校
ax2 = plt.subplot(1, 2, 2)
school_counts = df['个人信息_毕业院校'].value_counts().head(20)

sns.barplot(x=school_counts.values, y=school_counts.index, palette='magma', ax=ax2)
ax2.set_title('TOP20富豪毕业院校', fontsize=18, fontweight='bold')
ax2.set_xlabel('富豪数量', fontsize=14)
ax2.set_ylabel('院校', fontsize=14)
ax2.grid(axis='x', linestyle='--', alpha=0.7)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('毕业院校分析大类图.png', dpi=300, bbox_inches='tight')
plt.show()

print("所有大类分析图表已生成并保存!")