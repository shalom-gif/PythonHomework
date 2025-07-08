import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 数据
years = [2020, 2021, 2022, 2023, 2024]
conferences = {
    'aaai': [1864, 1961, 1624, 2021, 2866,],
    'cvpr': [1465, 1660, 2072, 2353, 2716],
    'icml': [1085, 1183, 1234, 1828, 2610],
    'ijcai': [778, 721, 863, 846, 1048],
    'nips': [1898, 2334, 2834, 3540, 4494]
}

# 绘制
plt.figure(figsize=(10, 5))

for conf, papers in conferences.items():
    plt.plot(years, papers, marker='o', label=conf)

plt.title('Paper Count by Conference Over Years')
plt.xlabel('Year')
plt.ylabel('Number of Papers')
plt.legend()
plt.grid(True)
plt.xticks(years)
plt.tight_layout()

# 保存
plt.savefig('paper_count_trend.png')