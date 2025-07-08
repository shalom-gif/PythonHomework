import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

def fetch_weather_data(year, month):
    url = f"https://www.tianqihoubao.com/lishi/dalian/month/{year}{month:02d}.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到天气数据表格
    table = soup.find('table', class_='weather-table')
    rows = table.find_all('tr')[1:]  # 跳过表头

    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 4:  # 确保有足够的列
            date = cols[0].text.strip()
            weather = cols[1].text.strip().split('/') if '/' in cols[1].text.strip() else [cols[1].text.strip()]
            temp = cols[2].text.strip().split('/') if '/' in cols[2].text.strip() else [cols[2].text.strip()]
            wind = cols[3].text.strip().split('/') if '/' in cols[3].text.strip() else [cols[3].text.strip()]

            data.append({
                '日期': date,
                '白天天气': weather[0] if len(weather) > 0 else '',
                '夜间天气': weather[1] if len(weather) > 1 else '',
                '最高气温(℃)': temp[0].strip('℃ ') if len(temp) > 0 else '',
                '最低气温(℃)': temp[1].strip('℃ ') if len(temp) > 1 else '',
                '白天风力风向': wind[0].strip() if len(wind) > 0 else '',
                '夜间风力风向': wind[1].strip() if len(wind) > 1 else ''
            })
    return data


# 爬取2025年1-6月的数据
weather_data_2025 = {}
for month in range(1, 7):
    weather_data_2025[month] = fetch_weather_data(2025, month)
    weather_data_2025[month] = pd.DataFrame(weather_data_2025[month])

# 保存数据到CSV文件
weather_data_2025 = pd.concat(weather_data_2025.values(), ignore_index=True)
weather_data_2025.to_csv('dalian_weather_2025.csv', index=False)

# 设置中文字体，这里使用的是Windows系统中常见的宋体
font = FontProperties(fname='C:/Windows/Fonts/simsun.ttc', size=14)

# 读取CSV文件
data_2022_2024 = pd.read_csv('dalian_weather_2022_2024.csv')
data_2025 = pd.read_csv('dalian_weather_2025.csv')

# 合并数据
data = pd.concat([data_2022_2024, data_2025], ignore_index=True)

# 将日期列转换为datetime类型，指定日期格式
data['日期'] = pd.to_datetime(data['日期'], format='%Y年%m月%d日', errors='coerce')

# 提取年份和月份
data['年'] = data['日期'].dt.year
data['月'] = data['日期'].dt.month

# 计算每个月的平均最高温度
monthly_avg_temp = data.groupby(['年', '月'])['最高气温(℃)'].mean().reset_index()

# 准备特征和标签
X = monthly_avg_temp[['年', '月']]
y = monthly_avg_temp['最高气温(℃)']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建线性回归模型
model = LinearRegression()

# 训练模型
model.fit(X_train, y_train)

# 预测2025年1-6月的温度
future_months = pd.DataFrame({
    '年': [2025]*6,
    '月': list(range(1, 7))
})

predicted_temps = model.predict(future_months)

# 绘制真实结果和预测结果的对比图
plt.figure(figsize=(10, 6))
plt.plot(monthly_avg_temp['月'], monthly_avg_temp['最高气温(℃)'], label='真实温度', marker='o')
plt.plot(future_months['月'], predicted_temps, label='预测温度', linestyle='--', marker='x', color='red')
plt.xlabel('月份', fontproperties=font)
plt.ylabel('平均最高温度 (℃)', fontproperties=font)
plt.title('大连市温度预测', fontproperties=font)
plt.legend(prop=font)
plt.grid(True)

# 保存图形
plt.savefig('temperature_prediction.png', bbox_inches='tight')

# 显示图形
plt.show()
