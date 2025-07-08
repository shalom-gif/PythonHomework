import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


# 定义爬取单个月份天气数据的函数
def crawl_weather_data(year, month):
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
        if len(cols) == 4:
            date = cols[0].text.strip()
            weather = cols[1].text.strip().split('/')
            temp = cols[2].text.strip().split('/')
            wind = cols[3].text.strip().split('/')

            # 检查分割后的列表长度
            day_weather = weather[0].strip() if len(weather) > 0 else ''
            night_weather = weather[1].strip() if len(weather) > 1 else ''
            max_temp = temp[0].strip('℃ ') if len(temp) > 0 else ''
            min_temp = temp[1].strip('℃ ') if len(temp) > 1 else ''
            day_wind = wind[0].strip() if len(wind) > 0 else ''
            night_wind = wind[1].strip() if len(wind) > 1 else ''

            data.append({
                '日期': date,
                '白天天气': day_weather,
                '夜间天气': night_weather,
                '最高气温(℃)': max_temp,
                '最低气温(℃)': min_temp,
                '白天风力风向': day_wind,
                '夜间风力风向': night_wind
            })

    return data


# 爬取2022年到2024年的天气数据
all_data = []
for year in range(2022, 2025):
    for month in range(1, 13):
        print(f"爬取{year}年{month}月的数据...")
        month_data = crawl_weather_data(year, month)
        all_data.extend(month_data)

# 将数据转换为DataFrame
df = pd.DataFrame(all_data)

# 保存数据到CSV文件
df.to_csv('dalian_weather_2022_2024.csv', index=False, encoding='utf-8')

print("数据爬取完成并保存到CSV文件中。")


