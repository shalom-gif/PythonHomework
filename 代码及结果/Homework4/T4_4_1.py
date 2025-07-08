import requests
import pandas as pd
import time
import random
from tqdm import tqdm


# 配置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Referer': 'https://www.cmzj.net/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
}


def fetch_expert_list(page):
    """获取单页专家列表数据"""
    url = f"https://i.cmzj.net/expert/rankingDetail?limit=10&page={page}&lottery=4&issueNum=7&target=esm&classPay=2"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['code'] == 0:
            return data['data']
        else:
            print(f"第 {page} 页数据获取失败: {data['msg']}")
            return []
    except Exception as e:
        print(f"获取第 {page} 页数据时出错: {str(e)}")
        return []


def fetch_expert_detail(expert_id):
    """获取专家详情数据"""
    url = f"https://i.cmzj.net/expert/queryExpertById?expertId={expert_id}"

    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        data = response.json()

        if data['code'] == 0 and 'data' in data:
            return data['data']
        else:
            print(f"专家 {expert_id} 详情获取失败: {data.get('msg', '未知错误')}")
            return {}
    except Exception as e:
        print(f"获取专家 {expert_id} 详情时出错: {str(e)}")
        return {}


def main():
    all_experts = []

    # 爬取所有100页的专家基本信息
    print("开始爬取专家排行榜数据...")
    for page in tqdm(range(1, 101)):
        experts = fetch_expert_list(page)
        if experts:
            all_experts.extend(experts)
        # 随机延时防止请求过快
        time.sleep(random.uniform(0.3, 0.8))

    print(f"共获取到 {len(all_experts)} 位专家的基本信息")

    # 爬取每个专家的详情信息
    print("\n开始爬取专家详情数据...")
    full_data = []

    # 进度条
    pbar = tqdm(total=len(all_experts))

    for expert in all_experts:
        # 基础信息
        expert_data = {
            # 排行榜信息
            '专家编号': expert['expertId'],
            '榜单排名': expert['rank'],
            '专家名': expert['name'],
            '成功率': expert['scoreRate'],
            '成绩': expert['score'],
            '最新文章': expert['title'],
            'bbxId': expert['bbxId'],
            'lift': expert['lift'],

            # 详情信息 (先初始化为空)
            'gradeName': '',
            'skills': '',
            'explains': '',
            'bestRecord': '',
            'fans': '',
            'age': '',
            'articles': '',
            'dltOne': '',
            'dltTwo': '',
            'dltThree': '',
            'dltScore': ''
        }

        # 获取详情信息
        detail = fetch_expert_detail(expert['expertId'])
        if detail:
            # 更新详情字段
            expert_data.update({
                'gradeName': detail.get('gradeName', ''),
                'skills': detail.get('skills', ''),
                'explains': detail.get('explains', ''),
                'bestRecord': detail.get('bestRecord', ''),
                'fans': detail.get('fans', ''),
                'age': detail.get('age', ''),
                'articles': detail.get('articles', ''),
                'dltOne': detail.get('dltOne', ''),
                'dltTwo': detail.get('dltTwo', ''),
                'dltThree': detail.get('dltThree', ''),
                'dltScore': detail.get('dltScore', '')
            })

        full_data.append(expert_data)
        pbar.update(1)

        # 随机延时
        time.sleep(random.uniform(0.2, 0.6))

    pbar.close()

    # 保存到CSV文件
    df = pd.DataFrame(full_data)

    # 优化列顺序
    columns_order = [
        'expertId', 'rank', 'name', 'gradeName', 'scoreRate', 'score',
        'bestRecord', 'dltOne', 'dltTwo', 'dltThree', 'dltScore',
        'fans', 'age', 'articles', 'skills', 'explains',
        'title', 'bbxId', 'lift'
    ]
    df = df.reindex(columns=columns_order)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f'大乐透收费专家20码排行榜各专家信息.csv'
    df.to_csv(filename, index=False, encoding='utf_8_sig')


    print(f"\n数据爬取完成! 共获取 {len(full_data)} 位专家数据")
    print(f"结果已保存到: {filename}")


if __name__ == "__main__":
    main()
