import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# 设置中文显示和图表样式
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# ====================== 行业映射部分 ======================
import pandas as pd
import re


class IndustryClassifier:
    def __init__(self):
        # 国民经济行业分类（GB/T 4754-2017）二十大核心门类映射
        self.industry_map = {
            # A-农、林、牧、渔业
            r'^农\w*|^林\w*|^牧\w*|^渔\w*|^畜牧\w*|^种业|^养殖|^农业$|^农产品|^农副|^林业|^森林|^渔业|^水产|^饲料|^兽药': 'A-农、林、牧、渔业',

            # B-采矿业
            r'^采矿|^矿业|^煤矿|^煤炭|^金矿|^铁矿|^锂矿|^钼矿|^钨矿|^矿产|^油田|^天然气|^原油|^石油|^矿山|^矿井|^勘查|^勘探': 'B-采矿业',

            # C-制造业 (细分重点行业)
            r'制造|^生产|^加工|^厂|^制品|^工业品|^化工|^医药制造|^生物制药|^医疗器械|^食品制造|'
            r'^饮料制造|^白酒|^电子制造|^半导体|^芯片|^集成电路|^光伏|^锂电池|^汽车制造|^零配件|'
            r'^机械制造|^设备制造|^家电|^服装|^鞋业|^家具|^建材|^玻璃|^包装|^钢铁|^有色金属|^化纤|'
            r'^轮胎|^水泥|^塑料|^橡胶|^纺织|^印染|^造纸|^印刷|^船舶|^航空器|^轨道交通装备|^武器弹药|'
            r'^乐器|^玩具|^体育用品|^工艺品|^文教用品|^办公用品|^照明器具|^钟表|^眼镜|^电池|^电线电缆|'
            r'^消防器材|^安全防范产品|^供应用仪器仪表|^环境监测专用仪器仪表': 'C-制造业',

            # D-电力、热力、燃气及水生产和供应业
            r'^电力|^热力|^燃气|^能源|^新能源|^太阳能|^风电|^发电|^供电|^输配电|^充电桩|^充电服务|^热电|'
            r'^水电|^火电|^核电|^风电|^光伏发电|^生物质能|^地热能|^智能电网|^水生产|^水供应|^自来水|'
            r'^污水处理及其再生利用|^海水淡化处理': 'D-电力、热力、燃气及水生产和供应业',

            # E-建筑业
            r'^建筑|^工程|^土木|^建设|^施工|^装修|^装饰|^安装|^路桥|^基建|^基础建设|^环保建筑|^房屋建筑|'
            r'^土木工程建筑|^建筑安装|^建筑装饰|^装修|^市政工程|^园林工程|^消防工程|^防水工程|^防腐保温工程|'
            r'^电子与智能化工程|^建筑幕墙工程|^古建筑工程|^钢结构工程|^模板脚手架工程|^起重设备安装工程': 'E-建筑业',

            # F-批发和零售业
            r'^批发|^零售|^贸易|^经销|^销售|^百货|^超市|^电商|^电子商务|^购物|^新零售|^连锁|^汽车销售|'
            r'^医药零售|^珠宝零售|^服装零售|^食品零售|^日用品零售|^五金交电|^建材销售|^机械设备销售|'
            r'^农产品销售|^畜牧产品销售|^渔业产品销售|^矿产品销售|^化工产品销售|^医疗器械销售': 'F-批发和零售业',

            # G-交通运输、仓储和邮政业
            r'^运输|^物流|^快递|^仓储|^航运|^航空|^海运|^船运|^货运|^配送|^邮政|^地铁|^铁路|^轨道交通|'
            r'^码头|^港口|^公路运输|^水上运输|^航空运输|^管道运输|^多式联运|^运输代理|^装卸搬运|'
            r'^快递服务|^邮政服务|^仓储服务|^配送服务|^包装服务': 'G-交通运输、仓储和邮政业',

            # H-住宿和餐饮业
            r'^住宿|^酒店|^餐饮|^饭店|^餐馆|^旅馆|^宾馆|^美食|^快餐|^餐饮连锁|^连锁酒店|^民宿|^客栈|'
            r'^度假村|^餐饮管理|^餐饮配送|^外卖服务': 'H-住宿和餐饮业',

            # I-信息传输、软件和信息技术服务业
            r'^信息|^软件|^IT|^互联网|^人工智能|^AI|^大数据|^云计算|^区块链|^网络|^通信|^电信|^5G|^物联网|'
            r'^游戏|^电竞|^网游|^手游|^平台|^SaaS|^算法|^云服务|^信息安全|^网络安全|^数据中心|^服务器|'
            r'^集成电路设计|^数字内容服务|^呼叫中心|^信息系统集成|^信息技术咨询|^数据处理和存储服务': 'I-信息传输、软件和信息技术服务业',

            # J-金融业
            r'^金融|^银行|^证券|^保险|^基金|^投资|^理财|^信贷|^融资|^担保|^风投|^PE|^VC|^交易所|^支付|'
            r'^金融科技|^FinTech|^期货|^信托|^融资租赁|^典当|^小额贷款|^金融信息服务|^外汇交易|'
            r'^黄金交易|^资产评估|^不动产评估|^价格鉴定': 'J-金融业',

            # K-房地产业
            r'^房地产|^地产|^物业|^置业|^楼盘|^不动产|^房产|^地产开发|^商业地产|^物流地产|^园区开发|'
            r'^物业管理|^房地产中介|^房地产咨询|^房地产评估|^住房租赁|^土地开发|^棚户区改造': 'K-房地产业',

            # L-租赁和商务服务业
            r'^租赁|^商务服务|^企业服务|^咨询|^会展|^广告|^中介|^外包|^代理|^拍卖|^供应链|^人力资源|'
            r'^会计|^审计|^法律|^管理咨询|^市场调查|^工程管理服务|^旅行社|^安全保护服务|^办公服务': 'L-租赁和商务服务业',

            # M-科学研究和技术服务业
            r'^科研|^研发|^设计|^技术服务|^工程|^实验室|^检测|^认证|^标准|^知识产权|^科技咨询|^技术转移|'
            r'^工程和技术研究|^医学研究|^农业科学研究|^环境与生态监测|^地质勘查|^测绘服务|^气象服务|'
            r'^海洋服务|^质检技术服务': 'M-科学研究和技术服务业',

            # N-水利、环境和公共设施管理业
            r'^水利|^环保|^环境|^生态|^绿化|^园林|^环卫|^污染|^治理|^节能|^减排|^污水处理|^公共设施|^市政|'
            r'^水务管理|^环境卫生管理|^城乡市容管理|^绿化管理|^公园管理|^游览景区管理|^自然保护区管理': 'N-水利、环境和公共设施管理业',

            # O-居民服务、修理和其他服务业
            r'^居民服务|^生活服务|^修理|^家政|^保洁|^美容|^美发|^洗浴|^摄影|^婚庆|^殡葬|^宠物|^社区服务|'
            r'^维修|^洗染服务|^洗浴服务|^保健服务|^婚姻服务|^殡仪服务|^宠物服务|^养老服务|^托育服务': 'O-居民服务、修理和其他服务业',

            # P-教育
            r'^教育|^培训|^学校|^学院|^大学|^幼儿园|^托育|^职业教育|^在线教育|^课程|^辅导|^留学|^考试|'
            r'^教材|^教具|^文具|^教育咨询|^教育评估|^职业技能培训|^语言培训|^艺术培训|^体育培训|'
            r'^科普服务': 'P-教育',

            # Q-卫生和社会工作
            r'^卫生|^医疗|^医院|^诊所|^健康|^养老|^护理|^康复|^体检|^疾控|^防疫|^社工|^福利|^救助|^慈善|'
            r'^心理咨询|^精神康复|^临终关怀|^残疾人养护服务|^孤残儿童收养和庇护服务|^母婴照护服务': 'Q-卫生和社会工作',

            # R-文化、体育和娱乐业
            r'^文化|^体育|^娱乐|^媒体|^影视|^音乐|^动漫|^出版|^艺术|^博物馆|^展览|^赛事|^健身|^旅游|^景区|'
            r'^主题公园|^演出经纪|^文艺创作与表演|^艺术表演场馆|^图书馆|^档案馆|^文物保护|^非物质文化遗产保护|'
            r'^体育场馆|^体育组织|^健身休闲活动|^高危险性体育项目服务|^彩票活动': 'R-文化、体育和娱乐业'
        }

        # 精确行业映射（优先级高于正则匹配）
        self.precise_map = {
            '房地产': 'K-房地产业',
            '医药': 'C-制造业',
            '投资': 'J-金融业',
            '半导体': 'C-制造业',
            '钢铁': 'C-制造业',
            '化工': 'C-制造业',
            '食品': 'C-制造业',
            '金融服务': 'J-金融业',
            '游戏': 'R-文化、体育和娱乐业',
            '餐饮': 'H-住宿和餐饮业',
            '电子元件': 'C-制造业',
            '化纤': 'C-制造业',
            '锂电池': 'C-制造业',
            '物流': 'G-交通运输、仓储和邮政业',
            '服装': 'C-制造业',
            '汽车零部件': 'C-制造业',
            '生物医药': 'C-制造业',
            '消费电子产品': 'C-制造业',
            '医疗器械': 'C-制造业',
            '调味品': 'C-制造业',
            '体育用品': 'C-制造业',
            '互联网服务': 'I-信息传输、软件和信息技术服务业',
            '化妆品': 'C-制造业',
            '软件与信息服务': 'I-信息传输、软件和信息技术服务业',
            '生活服务': 'O-居民服务、修理和其他服务业',
            '生物制药': 'C-制造业',
            '医疗服务': 'Q-卫生和社会工作',
            '饮料': 'C-制造业',
            '电子器件制造': 'C-制造业',
            '光伏设备': 'C-制造业',
            '快递': 'G-交通运输、仓储和邮政业',
            '重型机械': 'C-制造业',
            '博彩': 'R-文化、体育和娱乐业',
            '畜牧': 'A-农、林、牧、渔业',
            '机械制造': 'C-制造业',
            '教育': 'P-教育',
            '能源': 'D-电力、热力、燃气及水生产和供应业',
            '汽车销售': 'F-批发和零售业',
            '电子商务': 'F-批发和零售业',
            '新能源': 'D-电力、热力、燃气及水生产和供应业',
            '人工智能': 'I-信息传输、软件和信息技术服务业',
            '区块链': 'I-信息传输、软件和信息技术服务业',
            '智能制造': 'C-制造业',
            '数字经济': 'I-信息传输、软件和信息技术服务业',
            # 添加更多精确映射确保全面覆盖
            '种植业': 'A-农、林、牧、渔业',
            '煤炭开采': 'B-采矿业',
            '石油开采': 'B-采矿业',
            '汽车制造': 'C-制造业',
            '食品加工': 'C-制造业',
            '电力生产': 'D-电力、热力、燃气及水生产和供应业',
            '房屋建筑': 'E-建筑业',
            '商品销售': 'F-批发和零售业',
            '货物运输': 'G-交通运输、仓储和邮政业',
            '住宿服务': 'H-住宿和餐饮业',
            '软件开发': 'I-信息传输、软件和信息技术服务业',
            '证券交易': 'J-金融业',
            '物业管理': 'K-房地产业',
            '企业管理咨询': 'L-租赁和商务服务业',
            '环境监测': 'N-水利、环境和公共设施管理业',
            '家政服务': 'O-居民服务、修理和其他服务业',
            '学校教育': 'P-教育',
            '医院诊疗': 'Q-卫生和社会工作',
            '影视制作': 'R-文化、体育和娱乐业'
        }

    def classify(self, industry_str):
        """行业分类主函数"""
        if not industry_str or pd.isna(industry_str):
            # 对于空值，根据上下文选择最可能的分类，这里假设为金融业（可根据实际情况调整）
            return "J-金融业"

        # 转换为字符串并去除空格
        industry_str = str(industry_str).strip()

        # 1. 精确匹配优先
        if industry_str in self.precise_map:
            return self.precise_map[industry_str]

        # 2. 处理复合行业（如"房地产、投资"）
        if '、' in industry_str or ',' in industry_str or ' ' in industry_str:
            separators = r'[、,，\s]+'
            parts = re.split(separators, industry_str)
            categories = []
            for part in parts:
                part = part.strip()
                if part in self.precise_map:
                    categories.append(self.precise_map[part])
                else:
                    matched = False
                    for pattern, category in self.industry_map.items():
                        if re.search(pattern, part):
                            categories.append(category)
                            matched = True
                            break
                    # 如果没有匹配到任何模式，根据关键词进行最后判断
                    if not matched:
                        categories.append(self._keyword_fallback(part))

            # 统计各类别出现频率，返回最可能的分类
            category_count = defaultdict(int)
            for cat in categories:
                category_count[cat] += 1

            if category_count:
                # 返回出现次数最多的类别
                return max(category_count.items(), key=lambda x: x[1])[0]

        # 3. 正则表达式匹配
        for pattern, category in self.industry_map.items():
            if re.search(pattern, industry_str):
                return category

        # 4. 关键词兜底匹配
        return self._keyword_fallback(industry_str)

    def _keyword_fallback(self, industry_str):
        """关键词兜底匹配，确保所有输入都能被分类"""
        keywords = {
            '科技': 'I-信息传输、软件和信息技术服务业',
            '电子': 'C-制造业',
            '医疗': 'Q-卫生和社会工作',
            '教育': 'P-教育',
            '金融': 'J-金融业',
            '地产': 'K-房地产业',
            '制造': 'C-制造业',
            '能源': 'D-电力、热力、燃气及水生产和供应业',
            '消费': 'F-批发和零售业',
            '食品': 'C-制造业',
            '汽车': 'C-制造业',
            '互联网': 'I-信息传输、软件和信息技术服务业',
            '物流': 'G-交通运输、仓储和邮政业',
            '建筑': 'E-建筑业',
            '化工': 'C-制造业',
            '服务': 'L-租赁和商务服务业',
            '零售': 'F-批发和零售业',
            '投资': 'J-金融业',
            '农业': 'A-农、林、牧、渔业',
            '矿业': 'B-采矿业',
            '酒店': 'H-住宿和餐饮业',
            '娱乐': 'R-文化、体育和娱乐业',
            '环保': 'N-水利、环境和公共设施管理业',
            '咨询': 'L-租赁和商务服务业',
            '贸易': 'F-批发和零售业'
        }

        for keyword, category in keywords.items():
            if keyword in industry_str:
                return category

        # 如果以上都未匹配，根据行业字符串特征进行最后判断
        if '制造' in industry_str or '产品' in industry_str or '设备' in industry_str:
            return 'C-制造业'
        elif '服务' in industry_str:
            return 'L-租赁和商务服务业'
        elif '技术' in industry_str or '科技' in industry_str:
            return 'I-信息传输、软件和信息技术服务业'
        elif '开发' in industry_str:
            if '地产' in industry_str or '房产' in industry_str:
                return 'K-房地产业'
            else:
                return 'M-科学研究和技术服务业'
        else:
            # 默认返回金融业（因为金融行业通常涉及多种业务）
            return 'J-金融业'


class IndustryWealthAnalyzer:
    def __init__(self, file_path):
        self.df = self._load_and_preprocess_data(file_path)
        self.classifier = IndustryClassifier()  # 使用行业分类器
        self.classified_data = self._classify_industries()
        self.industry_stats = self._analyze_industry_wealth()

    def _load_and_preprocess_data(self, file_path):
        """加载并预处理数据"""
        df = pd.read_csv(file_path)
        # 重命名列以匹配分析需求
        df = df.rename(columns={
            '企业信息_行业_中文': '原始行业',
            '财富总值_亿': '财富总值',
            '个人信息_姓名_中文': '代表人物'  # 假设数据中有此列，实际需根据CSV调整
        })
        # 处理空值和异常值
        df['原始行业'] = df['原始行业'].fillna('未分类')
        df['财富总值'] = pd.to_numeric(df['财富总值'], errors='coerce').fillna(0)
        return df

    def _classify_industries(self):
        """使用IndustryClassifier进行行业分类处理"""
        classified = []
        for _, row in self.df.iterrows():
            original = str(row['原始行业'])
            wealth = row['财富总值']
            # 使用分类器获取行业类别
            category_str = self.classifier.classify(original)

            # 处理复合行业分类结果
            if ' / ' in category_str:
                categories = category_str.split(' / ')
                for cat in categories:
                    classified.append({
                        '原始行业': original,
                        '细分行业': original,
                        '行业大类': cat,
                        '财富值': wealth,
                        '代表人物': row['代表人物']  # 添加代表人物
                    })
            else:
                classified.append({
                    '原始行业': original,
                    '细分行业': original,
                    '行业大类': category_str,
                    '财富值': wealth,
                    '代表人物': row['代表人物']  # 添加代表人物
                })
        return pd.DataFrame(classified)

    def _analyze_industry_wealth(self):
        """行业财富统计分析"""
        # 按行业大类统计
        stats = self.classified_data.groupby('行业大类').agg(
            富豪数量=('原始行业', 'count'),
            财富总值=('财富值', 'sum'),
            细分行业数=('细分行业', 'nunique')
        ).reset_index()

        # 计算平均财富和占比
        total_wealth = stats['财富总值'].sum()
        stats['平均财富'] = stats['财富总值'] / stats['富豪数量']
        stats['财富占比'] = (stats['财富总值'] / total_wealth * 100).round(2)

        # 获取代表人物（取每个行业财富最高的）
        representatives = []
        for industry, group in self.classified_data.groupby('行业大类'):
            # 获取该行业财富最高的代表人物
            top_person = group.nlargest(1, '财富值')['代表人物'].values[0]
            representatives.append({
                '行业大类': industry,
                '代表人物': top_person
            })
        reps_df = pd.DataFrame(representatives)

        # 合并结果
        stats = pd.merge(stats, reps_df, on='行业大类')
        return stats.sort_values('财富总值', ascending=False)

    def visualize_analysis(self, top_n=10, output_file='行业财富分析可视化-大类行业.png'):
        """生成可视化图表"""
        plt.figure(figsize=(18, 12))

        # 1. 财富总值对比柱状图
        plt.subplot(2, 2, 1)
        top_industries = self.industry_stats.head(top_n)
        bars = plt.bar(top_industries['行业大类'], top_industries['财富总值'], color='skyblue')
        plt.title('各行业财富总值对比', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('财富总值（亿元）')
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:,.0f}',
                     ha='center', va='bottom')

        # 2. 财富占比条形图
        plt.subplot(2, 2, 2)
        top_industries = top_industries.sort_values('财富占比', ascending=True)
        bars = plt.barh(
            top_industries['行业大类'],
            top_industries['财富占比'],
            color=plt.cm.Paired(range(len(top_industries)))
        )

        plt.xlabel('财富占比 (%)')
        plt.title('行业财富占比分布', fontsize=14)
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # 添加数值标签
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                     f'{width:.1f}%',
                     va='center')

        # 3. 平均财富对比柱状图
        plt.subplot(2, 2, 3)
        avg_wealth = top_industries.sort_values('平均财富', ascending=False)
        bars = plt.bar(avg_wealth['行业大类'], avg_wealth['平均财富'], color='salmon')
        plt.title('行业平均财富对比', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('平均财富（亿元）')
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:,.2f}',
                     ha='center', va='bottom')

        # 4. 富豪数量对比柱状图
        plt.subplot(2, 2, 4)
        count_data = top_industries.sort_values('富豪数量', ascending=False)
        bars = plt.bar(count_data['行业大类'], count_data['富豪数量'], color='lightgreen')
        plt.title('各行业富豪数量对比', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('富豪数量（人）')
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{int(height)}',
                     ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"分析图表已保存至 {output_file}")


# 使用示例
if __name__ == "__main__":
    try:
        analyzer = IndustryWealthAnalyzer("行业财富分析结果-具体行业.csv")

        # 打印统计结果
        print("行业财富分布分析结果：")
        print(analyzer.industry_stats.to_string(index=False))

        # 生成可视化图表
        analyzer.visualize_analysis(top_n=10)

        # 保存分析结果到Excel
        analyzer.industry_stats.to_csv('行业财富分析结果-大类行业.csv', encoding='utf-8-sig')
        print("\n详细分析结果已保存至：行业财富分析结果-大类行业.csv")
    except Exception as e:
        print(f"分析过程中发生错误：{str(e)}")