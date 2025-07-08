import requests
import pandas as pd
from time import sleep
import random

# 初始化数据存储列表
all_data = []

#毕业院校处理
def get_school(character):
    # 获取中文和英文院校信息
    cn_school = character.get('hs_Character_School_Cn', '')
    en_school = character.get('hs_Character_School_En', '')

    # 处理缺失值（NaN或None）
    cn_school = cn_school if cn_school and str(cn_school).lower() != 'nan' else ''
    en_school = en_school if en_school and str(en_school).lower() != 'nan' else ''

    # 比较长度并返回结果
    if not cn_school and not en_school:
        return '未知'
    elif len(str(cn_school)) >= len(str(en_school)):
        return cn_school
    else:
        return en_school

# 循环请求所有页面
for page in range(1, 7):
    # 随机等待防止反爬
    sleep_time = random.uniform(1.5, 3)
    print(f'等待 {sleep_time:.2f} 秒...')
    sleep(sleep_time)

    # 计算偏移量
    offset = (page - 1) * 200
    url = f'https://www.hurun.net/zh-CN/Rank/HsRankDetailsList?num=ODBYW2BI&search=&offset={offset}&limit=200'

    # 请求头设置
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/json, */*; q=0.01',
        'Referer': 'https://www.hurun.net/zh-CN/Rank/HsRankDetails?pagetype=rich',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        print(f'正在爬取第 {page} 页...')
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查HTTP错误

        json_data = response.json()

        # 遍历每条记录
        for item in json_data['rows']:
            # 提取人物信息
            character = item['hs_Character'][0] if item['hs_Character'] else {}

            # 准备毕业院校字典
            school_dict = {
                'hs_Character_School_Cn': character.get('hs_Character_School_Cn', ''),
                'hs_Character_School_En': character.get('hs_Character_School_En', '')
            }

            # 提取排名信息
            rank_info = {
                '胡润百富榜年份': item.get('hs_Rank_Rich_Year', ''),
                '排名': item.get('hs_Rank_Rich_Ranking', ''),
                '排名变化': item.get('hs_Rank_Rich_Ranking_Change', ''),
                '财富(人民币/亿)': item.get('hs_Rank_Rich_Wealth', ''),
                '财富(美元/百万)': item.get('hs_Rank_Rich_Wealth_USD', ''),
                '财富变化': item.get('hs_Rank_Rich_Wealth_Change', ''),
                '个人信息_人物关系': item.get('hs_Rank_Rich_Relations', '').replace('未知', '个人'),
                '个人信息_姓名_中文': character.get('hs_Character_Fullname_Cn', ''),
                '个人信息_姓名_英文': character.get('hs_Character_Fullname_En', ''),
                '个人信息_性别': character.get('hs_Character_Gender', '').replace('先生', '男').replace('女士', '女'),
                '个人信息_年龄': character.get('hs_Character_Age', ''),
                '个人信息_照片URL': character.get('hs_Character_Photo', ''),
                '个人信息_籍贯_中文': character.get('hs_Character_NativePlace_Cn', ''),
                '个人信息_籍贯_英文': character.get('hs_Character_NativePlace_En', ''),
                '个人信息_出生地_中文': character.get('hs_Character_BirthPlace_Cn', ''),
                '个人信息_出生地_英文': character.get('hs_Character_BirthPlace_En', ''),
                '个人信息_常住地_中文': character.get('hs_Character_Permanent_Cn', ''),
                '个人信息_常住地_英文': character.get('hs_Character_Permanent_En', ''),
                '个人信息_教育程度_中文': character.get('hs_Character_Education_Cn', ''),
                '个人信息_教育程度_英文': character.get('hs_Character_Education_En', ''),
                '个人信息_毕业院校': get_school(school_dict),
                '个人信息_专业_中文': character.get('hs_Character_Major_En', ''),
                '个人信息_专业_英文': character.get('hs_Character_Major_Cn', ''),
                '企业信息_公司名称_中文': item.get('hs_Rank_Rich_ComName_Cn', ''),
                '企业信息_公司名称_英文': item.get('hs_Rank_Rich_ComName_En', ''),
                '企业信息_公司总部_中文': item.get('hs_Rank_Rich_ComHeadquarters_Cn', ''),
                '企业信息_公司总部_英文': item.get('hs_Rank_Rich_ComHeadquarters_En', ''),
                '企业信息_行业_中文': item.get('hs_Rank_Rich_Industry_Cn', ''),
                '企业信息_行业_英文': item.get('hs_Rank_Rich_Industry_En', '')
            }

            all_data.append(rank_info)

        print(f'第 {page} 页完成，已获取 {len(all_data)} 条记录')

    except Exception as e:
        print(f'第 {page} 页爬取失败: {str(e)}')
        continue

# 创建DataFrame
df = pd.DataFrame(all_data)

# 保存结果
output_file = '2024胡润百富榜.csv'
df.to_csv(output_file, index=False, encoding='utf_8_sig')
print(f'数据爬取完成! 共获取 {len(df)} 条记录，已保存至 {output_file}')
