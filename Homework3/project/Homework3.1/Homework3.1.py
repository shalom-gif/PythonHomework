import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

# 定义所有会议及其URL
conferences = {
    "ijcai": {
        2020: "https://dblp.org/db/conf/ijcai/ijcai2020.html",
        2021: "https://dblp.org/db/conf/ijcai/ijcai2021.html",
        2022: "https://dblp.org/db/conf/ijcai/ijcai2022.html",
        2023: "https://dblp.org/db/conf/ijcai/ijcai2023.html",
        2024: "https://dblp.org/db/conf/ijcai/ijcai2024.html"
    },
    "nips": {
        2020: "https://dblp.org/db/conf/nips/neurips2020.html",
        2021: "https://dblp.org/db/conf/nips/neurips2021.html",
        2022: "https://dblp.org/db/conf/nips/neurips2022.html",
        2023: "https://dblp.org/db/conf/nips/neurips2023.html",
        2024: "https://dblp.org/db/conf/nips/neurips2024.html"
    },
    "aaai": {
        2020: "https://dblp.org/db/conf/aaai/aaai2020.html",
        2021: "https://dblp.org/db/conf/aaai/aaai2021.html",
        2022: "https://dblp.org/db/conf/aaai/aaai2022.html",
        2023: "https://dblp.org/db/conf/aaai/aaai2023.html",
        2024: "https://dblp.org/db/conf/aaai/aaai2024.html",
    },
    "cvpr": {
        2020: "https://dblp.org/db/conf/cvpr/cvpr2020.html",
        2021: "https://dblp.org/db/conf/cvpr/cvpr2021.html",
        2022: "https://dblp.org/db/conf/cvpr/cvpr2022.html",
        2023: "https://dblp.org/db/conf/cvpr/cvpr2023.html",
        2024: "https://dblp.org/db/conf/cvpr/cvpr2024.html"
    },
    "icml": {
        2020: "https://dblp.org/db/conf/icml/icml2020.html",
        2021: "https://dblp.org/db/conf/icml/icml2021.html",
        2022: "https://dblp.org/db/conf/icml/icml2022.html",
        2023: "https://dblp.org/db/conf/icml/icml2023.html",
        2024: "https://dblp.org/db/conf/icml/icml2024.html"
    }
}


def fetch_conference_papers(conference, year):
    """获取指定会议和年份的论文"""
    if conference not in conferences or year not in conferences[conference]:
        print(f"Conference {conference} or year {year} not supported.")
        return []

    url = conferences[conference][year]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        # 发送HTTP请求
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 解析HTML内容
        soup = BeautifulSoup(response.content, 'html.parser')

        # 查找会议名称
        header_tag = soup.find('header', id='headline')
        conference_title = header_tag.find('h1').get_text(strip=True) if header_tag else conference.upper()

        # 查找所有论文部分
        paper_entries = soup.find_all('li', class_='entry inproceedings')

        papers = []

        # 遍历每个论文条目
        for entry in paper_entries:
            # 提取标题
            title_tag = entry.find('span', class_='title')
            if not title_tag:
                continue
            title = title_tag.get_text().strip()

            # 提取作者
            authors = []
            for author_tag in entry.find_all('span', itemprop='author'):
                for name_tag in author_tag.find_all('span', itemprop='name'):
                    authors.append(name_tag.get_text().strip())

            # 提取链接
            links = entry.find_all('a', href=True)
            link = None
            for a_tag in links:
                if a_tag.get('href'):
                    link = urljoin(url, a_tag['href'])  # 转换为完整URL
                    break  # 只取第一个链接

            # 创建论文字典
            paper = {
                'title': title,
                'authors': ', '.join(authors),
                'conference_name': conference_title,
                'conference_year': str(year),
                'link': link
            }

            papers.append(paper)

        return papers
    except requests.exceptions.RequestException as e:
        print(f"Error fetching papers for {conference} {year}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def save_papers_to_csv(papers, filename):
    """保存论文列表到CSV文件"""
    if not papers:
        return

    # 定义CSV文件头
    headers = ['title', 'authors', 'conference_name', 'conference_year', 'link']

    # 写入CSV文件
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper)


if __name__ == "__main__":
    # 爬取所有会议所有年份的论文
    for conference in conferences:
        for year in conferences[conference]:
            papers = fetch_conference_papers(conference, year)
            if papers:
                # 为该会议年份生成CSV文件
                filename = f'{conference}_{year}_papers.csv'
                save_papers_to_csv(papers, filename)
                print(f"已保存 {conference.upper()} {year} 年论文到 {filename}，共 {len(papers)} 篇")
            else:
                print(f"{conference.upper()} {year} 年未获取到论文数据")