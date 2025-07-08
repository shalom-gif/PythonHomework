import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

#数据可视化

# 设置中文字体，这里使用的是Windows系统中常见的宋体
font = FontProperties(fname='C:/Windows/Fonts/simsun.ttc', size=14)

# 读取CSV文件
df = pd.read_csv('dalian_weather_2022_2024.csv')

# 将日期列转换为datetime类型，指定日期格式
df['日期'] = pd.to_datetime(df['日期'], format='%Y年%m月%d日', errors='coerce')

# 提取年份和月份
df['年'] = df['日期'].dt.year
df['月'] = df['日期'].dt.month

# 计算每个月的平均最高温度和平均最低温度
monthly_avg_temp = df.groupby(['年', '月']).agg({
    '最高气温(℃)': 'mean',
    '最低气温(℃)': 'mean'
}).reset_index()

# 绘制折线图
plt.figure(figsize=(10, 6))
plt.plot(monthly_avg_temp['月'], monthly_avg_temp['最高气温(℃)'], label='平均最高温度', marker='o')
plt.plot(monthly_avg_temp['月'], monthly_avg_temp['最低气温(℃)'], label='平均最低温度', marker='o')

# 添加标题和标签
plt.title('大连市近三年月平均气温变化图', fontproperties=font)
plt.xlabel('月份', fontproperties=font)
plt.ylabel('温度 (℃)', fontproperties=font)
plt.xticks(range(1, 13), [f'{month}月' for month in range(1, 13)], fontproperties=font)
plt.legend(prop=font)

# 显示网格
plt.grid(True)

# 保存图形
plt.savefig('dalian_avg_temp.png', bbox_inches='tight')

# 显示图形
plt.show()

# 提取风力等级
df['白天风力等级'] = df['白天风力风向'].str.extract(r'(\d+-\d+)')
df['夜间风力等级'] = df['夜间风力风向'].str.extract(r'(\d+-\d+)')

# 统计每个月不同风力等级出现的天数
monthly_wind_count = df.groupby(['年', '月', '白天风力等级']).size().reset_index(name='白天天数')
monthly_wind_count = monthly_wind_count.groupby(['年', '月', '白天风力等级']).sum().reset_index()

# 绘制柱状图
plt.figure(figsize=(12, 8))
for wind_level in monthly_wind_count['白天风力等级'].unique():
    subset = monthly_wind_count[monthly_wind_count['白天风力等级'] == wind_level]
    plt.bar(subset['月'] + (wind_level != subset['白天风力等级']) * 0.4, subset['白天天数'], width=0.4, label=f'{wind_level}级')

plt.title('大连市近三年每月不同风力等级天数分布图', fontproperties=font)
plt.xlabel('月份', fontproperties=font)
plt.ylabel('天数', fontproperties=font)
plt.xticks(range(1, 13), [f'{month}月' for month in range(1, 13)], fontproperties=font)
plt.legend(prop=font)

# 显示网格
plt.grid(True)

# 保存图形
plt.savefig('dalian_wind_level_distribution.png', bbox_inches='tight')

# 显示图形
plt.show()

# 提取天气状况
df['天气状况'] = df['白天天气'] + '/' + df['夜间天气']

# 统计每个月中不同天气状况出现的天数
monthly_weather_count = df.groupby(['年', '月', '天气状况']).size().reset_index(name='天数')

# 绘制柱状图
plt.figure(figsize=(12, 8))
for weather in monthly_weather_count['天气状况'].unique():
    subset = monthly_weather_count[monthly_weather_count['天气状况'] == weather]
    plt.bar(subset['月'] + (weather != subset['天气状况']) * 0.4, subset['天数'], width=0.4, label=weather)

plt.title('大连市近三年每月不同天气状况天数分布图', fontproperties=font)
plt.xlabel('月份', fontproperties=font)
plt.ylabel('天数', fontproperties=font)
plt.xticks(range(1, 13), [f'{month}月' for month in range(1, 13)], fontproperties=font)
plt.legend(prop=font)

# 显示网格
plt.grid(True)

# 保存图形
plt.savefig('dalian_weather_distribution.png', bbox_inches='tight')

# 显示图形
plt.show()