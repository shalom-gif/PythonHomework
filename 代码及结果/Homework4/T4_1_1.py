import requests
import json
import pandas as pd
from datetime import datetime
import time
import random


def fetch_dlt_data():
    base_url = "https://jc.zhcw.com/port/client_json.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.zhcw.com/kjxx/dlt/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
    }

    all_data = []
    total_pages = 4

    # 分页获取数据
    for page in range(1, total_pages + 1):
        # 生成时间戳参数
        timestamp = int(time.time() * 1000)
        params = {
            'transactionType': '10001001',
            'lotteryId': '281',
            'issueCount': '100',
            'pageNum': str(page),
            'pageSize': '30',
            'type': '0',
            'tt': f'0.{timestamp}',
            '_': str(timestamp)
        }

        try:
            print(f"正在获取第 {page}/{total_pages} 页数据...")
            response = requests.get(
                url=base_url,
                params=params,
                headers=headers,
                timeout=20
            )

            if response.status_code == 200:
                # 处理JSONP响应
                json_str = response.text
                if json_str.startswith('jQuery') and '(' in json_str:
                    json_str = json_str.split('(', 1)[1].rsplit(')', 1)[0]

                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    print("  响应不是有效JSON，尝试直接解析...")
                    json_str = response.text.strip().strip(';').strip()
                    if json_str.startswith('jQuery') and '(' in json_str:
                        json_str = json_str.split('(', 1)[1].rsplit(')', 1)[0]
                    data = json.loads(json_str)

                # 确保data字段存在
                if 'data' in data and isinstance(data['data'], list):
                    page_data_count = 0
                    for item in data['data']:
                        # 解析中奖详情
                        prize_details = parse_winner_details(item.get('winnerDetails', []))

                        # 创建详情页URL
                        issue_number = item.get('issue', '')
                        detail_url = f"https://www.zhcw.com/kjxx/dlt/kjxq/?kjData={issue_number}" if issue_number else ""

                        # 创建数据记录
                        record = {
                            '期号': issue_number,
                            '详情页链接': detail_url,
                            '开奖日期': item.get('openTime'),
                            '星期': item.get('week'),
                            '中奖号码_前区': item.get('frontWinningNum', ''),
                            '中奖号码_后区': item.get('backWinningNum', ''),
                            '出球顺序_前区': item.get('seqFrontWinningNum', ''),
                            '出球顺序_后区': item.get('seqBackWinningNum', ''),
                            '总销售额(元)': format_amount(item.get('saleMoney', '0')),
                            '奖池奖金(元)': format_amount(item.get('prizePoolMoney', '0')),
                        }

                        # 添加中奖详情
                        record.update(prize_details)
                        all_data.append(record)
                        page_data_count += 1

                    print(f"  成功解析 {page_data_count} 期数据")
                else:
                    print(f"  第{page}页返回数据格式异常")
                    print(f"  响应内容: {response.text[:500]}")
            else:
                print(f"  请求失败，状态码：{response.status_code}")
                print(f"  响应内容: {response.text[:200]}")

        except Exception as e:
            print(f"  请求异常：{str(e)}")

        # 添加随机请求间隔，避免被封IP
        time.sleep(random.uniform(1.0, 2.5))

    return all_data


def parse_winner_details(winner_details):
    """解析中奖详情数据结构，只为1-2等奖添加派奖和追加派奖字段"""
    prize_data = {}

    # 初始化所有奖项的基本和追加投注字段
    for level in range(1, 10):
        # 基本投注
        prize_data[f'{level}等奖_基本注数'] = 0
        prize_data[f'{level}等奖_基本单注奖金(元)'] = 0
        prize_data[f'{level}等奖_基本总奖金(元)'] = 0

        # 追加投注
        prize_data[f'{level}等奖_追加注数'] = 0
        prize_data[f'{level}等奖_追加单注奖金(元)'] = 0
        prize_data[f'{level}等奖_追加总奖金(元)'] = 0

    # 只为1-2等奖添加派奖和追加派奖字段
    for level in range(1, 3):
        prize_data[f'{level}等奖_派奖注数'] = 0
        prize_data[f'{level}等奖_派奖单注金额(元)'] = 0
        prize_data[f'{level}等奖_派奖总金额(元)'] = 0

        prize_data[f'{level}等奖_追加派奖注数'] = 0
        prize_data[f'{level}等奖_追加派奖单注金额(元)'] = 0
        prize_data[f'{level}等奖_追加派奖总金额(元)'] = 0

    # 解析每个奖项
    for detail in winner_details:
        try:
            level = int(detail.get('awardEtc', 0))
            if not (1 <= level <= 9):
                continue

            # 处理基本投注
            base = detail.get('baseBetWinner', {})
            if base and isinstance(base, dict):
                prize_data[f'{level}等奖_基本注数'] = base.get('awardNum', 0)
                prize_data[f'{level}等奖_基本单注奖金(元)'] = format_amount(base.get('awardMoney', 0))
                prize_data[f'{level}等奖_基本总奖金(元)'] = format_amount(base.get('totalMoney', 0))

            # 处理追加投注
            add = detail.get('addToBetWinner', {})
            if add and isinstance(add, dict):
                prize_data[f'{level}等奖_追加注数'] = add.get('awardNum', 0)
                prize_data[f'{level}等奖_追加单注奖金(元)'] = format_amount(add.get('awardMoney', 0))
                prize_data[f'{level}等奖_追加总奖金(元)'] = format_amount(add.get('totalMoney', 0))

            # 只处理1-2等奖的派奖信息
            if level in (1, 2):
                # 处理派奖
                add2 = detail.get('addToBetWinner2', {})
                if add2 and isinstance(add2, dict):
                    prize_data[f'{level}等奖_派奖注数'] = add2.get('awardNum', 0)
                    prize_data[f'{level}等奖_派奖单注金额(元)'] = format_amount(add2.get('awardMoney', 0))
                    prize_data[f'{level}等奖_派奖总金额(元)'] = format_amount(add2.get('totalMoney', 0))

                # 处理追加派奖
                add3 = detail.get('addToBetWinner3', {})
                if add3 and isinstance(add3, dict):
                    prize_data[f'{level}等奖_追加派奖注数'] = add3.get('awardNum', 0)
                    prize_data[f'{level}等奖_追加派奖单注金额(元)'] = format_amount(add3.get('awardMoney', 0))
                    prize_data[f'{level}等奖_追加派奖总金额(元)'] = format_amount(add3.get('totalMoney', 0))

        except Exception as e:
            print(f"解析中奖详情出错：{str(e)}")
            print(f"问题数据: {detail}")

    return prize_data

def format_amount(value):
    """格式化金额数字，移除逗号并转换为整数"""
    if isinstance(value, str):
        # 移除逗号和可能的货币符号
        value = value.replace(',', '').replace('￥', '').replace('元', '')
        # 处理小数情况
        if '.' in value:
            try:
                return int(float(value))
            except:
                return 0
        try:
            return int(value) if value else 0
        except:
            return 0
    elif isinstance(value, (int, float)):
        return int(value)
    return 0


# 主程序
if __name__ == "__main__":
    print("=" * 60)
    print("大乐透开奖数据分析工具")
    print("开始处理数据...")
    print("=" * 60)

    start_time = time.time()
    data = fetch_dlt_data()

    if data:
        df = pd.DataFrame(data)
        # 定义新的字段顺序
        new_columns = [
            '期号', '详情页链接', '开奖日期', '星期', '中奖号码_前区', '中奖号码_后区',
            '出球顺序_前区', '出球顺序_后区', '总销售额(元)', '奖池奖金(元)'
        ]

        # 为每个奖项定义字段顺序
        for level in range(1, 10):
            # 基本投注字段
            new_columns.extend([
                f'{level}等奖_基本注数',
                f'{level}等奖_基本单注奖金(元)',
                f'{level}等奖_基本总奖金(元)',
            ])

            # 追加投注字段
            new_columns.extend([
                f'{level}等奖_追加注数',
                f'{level}等奖_追加单注奖金(元)',
                f'{level}等奖_追加总奖金(元)',
            ])

            # 对于1-2等奖，添加派奖字段
            if level in (1, 2):
                new_columns.extend([
                    f'{level}等奖_派奖注数',
                    f'{level}等奖_派奖单注金额(元)',
                    f'{level}等奖_派奖总金额(元)',

                    f'{level}等奖_追加派奖注数',
                    f'{level}等奖_追加派奖单注金额(元)',
                    f'{level}等奖_追加派奖总金额(元)',
                ])

        # 确保所有列都存在（可能有些列在数据中不存在）
        existing_columns = [col for col in new_columns if col in df.columns]

        #添加可能遗漏的列
        for col in df.columns:
            if col not in existing_columns:
                existing_columns.append(col)

        # 重新排序数据框
        df = df[existing_columns]

        # 按开奖日期排序
        df['开奖日期'] = pd.to_datetime(df['开奖日期'])
        df = df.sort_values('开奖日期', ascending=False).reset_index(drop=True)

        # 保存文件
        current_date = datetime.now().strftime("%Y%m%d")
        csv_filename = "近100期大乐透开奖数据和中奖情况.csv"
        df.to_csv(csv_filename, index=False, encoding='utf_8_sig')
        print("\n" + "=" * 60)
        print(f"数据处理完成！耗时: {time.time() - start_time:.2f}秒")
        print(f"共处理 {len(df)} 期开奖数据")
        print(f"CSV文件已保存: {csv_filename}")
        print("=" * 60)