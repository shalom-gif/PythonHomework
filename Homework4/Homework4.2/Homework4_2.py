import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TkAgg')  # 或 'Qt5Agg'
import os
from collections import Counter
from datetime import datetime

# 设置支持中文的字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
mpl.rcParams['axes.unicode_minus'] = False

# 创建输出目录
os.makedirs('星期统计', exist_ok=True)

# 读取Excel文件
df = pd.read_excel('近100期大乐透开奖数据和中奖情况.xlsx')

# 数据预处理
df['前区号码'] = df['中奖号码_前区'].str.split().apply(lambda x: [int(n) for n in x])
df['后区号码'] = df['中奖号码_后区'].str.split().apply(lambda x: [int(n) for n in x])

# 按星期分组
grouped = df.groupby('星期')


# 整体频率统计（不区分星期）
def generate_full_stats():
    # 前区号码频率统计
    front_counts = pd.Series([num for sublist in df['前区号码'] for num in sublist]).value_counts().sort_index()
    front_counts_df = front_counts.reset_index()
    front_counts_df.columns = ['前区号码', '出现次数']
    front_counts_df.to_csv('整体前区频率统计.csv', index=False, encoding='utf_8_sig')

    # 后区号码频率统计
    back_counts = pd.Series([num for sublist in df['后区号码'] for num in sublist]).value_counts().sort_index()
    back_counts_df = back_counts.reset_index()
    back_counts_df.columns = ['后区号码', '出现次数']
    back_counts_df.to_csv('整体后区频率统计.csv', index=False, encoding='utf_8_sig')

    # 组合频率统计
    heatmap_data = pd.DataFrame(0, index=range(1, 36), columns=range(1, 13))
    for _, row in df.iterrows():
        for f in row['前区号码']:
            for b in row['后区号码']:
                heatmap_data.loc[f, b] += 1
    heatmap_data.to_csv('整体前后区组合频率统计.csv', index=True, index_label='前区号码\后区号码', encoding='utf_8_sig')

    # 可视化前区频率
    plt.figure(figsize=(15, 6))
    front_counts.plot(kind='bar', color='skyblue')
    plt.title('大乐透前区号码出现频率 (近100期)', fontsize=15)
    plt.xlabel('号码', fontsize=12)
    plt.ylabel('出现次数', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('整体前区号码频率分布图.png', dpi=300)
    plt.show()

    # 可视化后区频率
    plt.figure(figsize=(10, 6))
    back_counts.plot(kind='bar', color='lightgreen')
    plt.title('大乐透后区号码出现频率 (近100期)', fontsize=15)
    plt.xlabel('号码', fontsize=12)
    plt.ylabel('出现次数', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('整体后区号码频率分布图.png', dpi=300)
    plt.show()

    # 绘制热力图
    plt.figure(figsize=(12, 8))
    plt.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
    plt.colorbar(label='组合出现次数')
    plt.title('前区-后区号码组合热力图', fontsize=15)
    plt.xlabel('后区号码', fontsize=12)
    plt.ylabel('前区号码', fontsize=12)
    plt.xticks(range(12), range(1, 13))
    plt.yticks(range(35), range(1, 36))
    plt.tight_layout()
    plt.savefig('整体前后区组合热力图.png', dpi=300)
    plt.show()


# 按星期生成统计
wednesday_data = None
for day, group in grouped:
    # 保存星期三的数据用于预测
    if day == '星期三':
        wednesday_data = group.copy()

    # 前区号码频率统计
    front_counts = pd.Series([num for sublist in group['前区号码'] for num in sublist]).value_counts().sort_index()
    front_counts_df = front_counts.reset_index()
    front_counts_df.columns = ['前区号码', '出现次数']
    front_counts_df.to_csv(f'星期统计/{day}_前区频率统计.csv', index=False, encoding='utf_8_sig')

    # 后区号码频率统计
    back_counts = pd.Series([num for sublist in group['后区号码'] for num in sublist]).value_counts().sort_index()
    back_counts_df = back_counts.reset_index()
    back_counts_df.columns = ['后区号码', '出现次数']
    back_counts_df.to_csv(f'星期统计/{day}_后区频率统计.csv', index=False, encoding='utf_8_sig')

    # 组合频率统计
    heatmap_data = pd.DataFrame(0, index=range(1, 36), columns=range(1, 13))
    for _, row in group.iterrows():
        for f in row['前区号码']:
            for b in row['后区号码']:
                heatmap_data.loc[f, b] += 1
    heatmap_data.to_csv(f'星期统计/{day}_前后区组合频率统计.csv', index=True, index_label='前区号码\后区号码',
                        encoding='utf_8_sig')

    # 生成可视化图表
    plt.figure(figsize=(12, 6))
    front_counts.plot(kind='bar', color='skyblue')
    plt.title(f'大乐透前区号码出现频率 ({day})', fontsize=15)
    plt.xlabel('号码', fontsize=12)
    plt.ylabel('出现次数', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'星期统计/{day}_前区频率分布图.png', dpi=300)
    plt.show()

    plt.figure(figsize=(8, 6))
    back_counts.plot(kind='bar', color='lightgreen')
    plt.title(f'大乐透后区号码出现频率 ({day})', fontsize=15)
    plt.xlabel('号码', fontsize=12)
    plt.ylabel('出现次数', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'星期统计/{day}_后区频率分布图.png', dpi=300)
    plt.show()

    plt.figure(figsize=(12, 8))
    plt.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
    plt.colorbar(label='组合出现次数')
    plt.title(f'大乐透前区-后区号码组合热力图 ({day})', fontsize=15)
    plt.xlabel('后区号码', fontsize=12)
    plt.ylabel('前区号码', fontsize=12)
    plt.xticks(range(12), range(1, 13))
    plt.yticks(range(35), range(1, 36))
    plt.tight_layout()
    plt.savefig(f'星期统计/{day}_前后区组合热力图.png', dpi=300)
    plt.show()

# 生成整体统计
generate_full_stats()


# 预测函数 - 基于整体数据和星期三历史数据
def predict_numbers(wed_data, full_df):
    # 计算整体频率
    full_front_counts = Counter([num for sublist in full_df['前区号码'] for num in sublist])
    full_back_counts = Counter([num for sublist in full_df['后区号码'] for num in sublist])

    # 计算星期三频率
    wed_front_counts = Counter([num for sublist in wed_data['前区号码'] for num in sublist])
    wed_back_counts = Counter([num for sublist in wed_data['后区号码'] for num in sublist])

    # 组合频率统计（星期三）
    wed_combo_counts = {}
    for _, row in wed_data.iterrows():
        for f in row['前区号码']:
            for b in row['后区号码']:
                wed_combo_counts[(f, b)] = wed_combo_counts.get((f, b), 0) + 1

    # 1. 保守策略 - 加权热号组合
    # 创建加权频率（50%星期三频率 + 50%整体频率）
    weighted_front = {}
    for num in range(1, 36):
        wed_count = wed_front_counts.get(num, 0)
        full_count = full_front_counts.get(num, 0)
        weighted_front[num] = 0.5 * wed_count + 0.5 * full_count

    weighted_back = {}
    for num in range(1, 13):
        wed_count = wed_back_counts.get(num, 0)
        full_count = full_back_counts.get(num, 0)
        weighted_back[num] = 0.6 * wed_count + 0.4 * full_count

    # 选择加权频率最高的号码
    front_conservative = sorted(weighted_front, key=weighted_front.get, reverse=True)[:5]
    front_conservative.sort()

    back_conservative = sorted(weighted_back, key=weighted_back.get, reverse=True)[:2]
    back_conservative.sort()

    # 2. 平衡策略 - 热号+潜力号
    # 前区：3个高频号 + 2个中频号
    # 高频：加权值在前20%的号码
    front_values = list(weighted_front.values())
    high_threshold = np.percentile(front_values, 80)
    mid_threshold = np.percentile(front_values, 50)

    high_front = [num for num, val in weighted_front.items() if val >= high_threshold]
    mid_front = [num for num, val in weighted_front.items() if mid_threshold <= val < high_threshold]

    if len(high_front) < 3:
        # 如果高频号码不足，补充整体高频
        high_front = sorted(full_front_counts, key=full_front_counts.get, reverse=True)[:10]

    if len(mid_front) < 5:
        # 如果中频号码不足，补充整体中频
        mid_front = [num for num in range(1, 36) if 5 <= full_front_counts.get(num, 0) <= 7]

    # 随机选择
    front_balanced = list(np.random.choice(high_front, min(3, len(high_front)), replace=False))
    if len(mid_front) > 0:
        front_balanced += list(np.random.choice(mid_front, 5 - len(front_balanced), replace=False))
    else:
    # 如果没有中频，补充高频
        front_balanced += list(np.random.choice(high_front, 5 - len(front_balanced), replace=False))
    front_balanced.sort()

    # 后区：1个高频 + 1个中频
    back_values = list(weighted_back.values())
    high_threshold_b = np.percentile(back_values, 80)
    mid_threshold_b = np.percentile(back_values, 50)

    high_back = [num for num, val in weighted_back.items() if val >= high_threshold_b]
    mid_back = [num for num, val in weighted_back.items() if mid_threshold_b <= val < high_threshold_b]

    if len(high_back) < 1:
        high_back = sorted(full_back_counts, key=full_back_counts.get, reverse=True)[:3]

    if len(mid_back) < 1:
        mid_back = [num for num in range(1, 13) if 3 <= full_back_counts.get(num, 0) <= 4]

    back_balanced = list(np.random.choice(high_back, 1, replace=False))
    if len(mid_back) > 0:
        back_balanced += list(np.random.choice(mid_back, 1, replace=False))
    else:
        back_balanced += list(np.random.choice(high_back, 1, replace=False))
    back_balanced.sort()

    # 3. 激进策略 - 热冷结合
    # 前区：2个高频 + 1个中频 + 2个低频
    low_front = [num for num in range(1, 36) if weighted_front.get(num, 0) < np.percentile(front_values, 30)]
    if len(low_front) < 2:
        low_front = [num for num in range(1, 36) if full_front_counts.get(num, 0) < 4]

    front_aggressive = list(np.random.choice(high_front, 2, replace=False))
    if len(mid_front) > 0:
        front_aggressive += list(np.random.choice(mid_front, 1, replace=False))
    else:
        front_aggressive += list(np.random.choice(high_front, 1, replace=False))
    if len(low_front) > 0:
        front_aggressive += list(np.random.choice(low_front, 2, replace=False))
    else:
        front_aggressive += list(np.random.choice(mid_front, 2, replace=False))
    front_aggressive.sort()

    # 后区：1个高频 + 1个低频
    low_back = [num for num in range(1, 13) if weighted_back.get(num, 0) < np.percentile(back_values, 30)]
    if len(low_back) < 1:
        low_back = [num for num in range(1, 13) if full_back_counts.get(num, 0) < 3]

    back_aggressive = list(np.random.choice(high_back, 1, replace=False))
    if len(low_back) > 0:
        back_aggressive += list(np.random.choice(low_back, 1, replace=False))
    else:
        back_aggressive += list(np.random.choice(mid_back, 1, replace=False))
    back_aggressive.sort()

    # 4. 组合优化策略 - 基于最佳组合
    # 找出最高频的前区-后区组合（星期三）
    top_combos = sorted(wed_combo_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    # 创建组合权重（考虑整体频率）
    combo_weights = {}
    for (f, b), count in top_combos:
    # 组合权重 = 星期三组合频率 * 0.7 + (整体前区频率 + 整体后区频率) * 0.3
        combo_weights[(f, b)] = 0.7 * count + 0.3 * (full_front_counts[f] + full_back_counts[b])

    # 选择最高权重的组合
    top_combos_weighted = sorted(combo_weights.items(), key=lambda x: x[1], reverse=True)[:20]

    front_combo = []
    back_combo = []
    selected_front = set()
    selected_back = set()

    for (f, b), weight in top_combos_weighted:
        if len(front_combo) < 5 and f not in selected_front:
            front_combo.append(f)
            selected_front.add(f)
        if len(back_combo) < 2 and b not in selected_back:
            back_combo.append(b)
            selected_back.add(b)
        if len(front_combo) == 5 and len(back_combo) == 2:
            break

    # 如果不足5个前区号码，补充加权高频号码
    if len(front_combo) < 5:
        remaining = sorted(weighted_front, key=weighted_front.get, reverse=True)
        remaining = [num for num in remaining if num not in selected_front]
        front_combo.extend(remaining[:5 - len(front_combo)])

    # 如果不足2个后区号码，补充加权高频号码
    if len(back_combo) < 2:
        remaining = sorted(weighted_back, key=weighted_back.get, reverse=True)
        remaining = [num for num in remaining if num not in selected_back]
        back_combo.extend(remaining[:2 - len(back_combo)])

    front_combo.sort()
    back_combo.sort()

    # 5. 新增策略：星期三高频号码
    # 前区：选择星期三频率最高的5个号码
    wed_high_front = [num for num, count in wed_front_counts.most_common(5)]
    wed_high_front.sort()

    # 后区：选择星期三频率最高的2个号码
    wed_high_back = [num for num, count in wed_back_counts.most_common(2)]
    wed_high_back.sort()

    # 6. 新增策略：整体高频号码
    # 前区：选择整体频率最高的5个号码
    full_high_front = [num for num, count in full_front_counts.most_common(5)]
    full_high_front.sort()

    # 后区：选择整体频率最高的2个号码
    full_high_back = [num for num, count in full_back_counts.most_common(2)]
    full_high_back.sort()

    return {
        "保守策略(加权)": (front_conservative, back_conservative),
        "平衡策略": (front_balanced, back_balanced),
        "激进策略": (front_aggressive, back_aggressive),
        "组合优化": (front_combo, back_combo),
        "星期三高频": (wed_high_front, wed_high_back),
        "整体高频": (full_high_front, full_high_back)
    }


# 预测2025年7月2日（周三）的号码
if wednesday_data is not None:
    predictions = predict_numbers(wednesday_data, df)
    print("\n" + "=" * 50)
    print(f"基于整体和星期三数据的2025年7月2日（周三）大乐透预测")
    print("=" * 50)

    # 获取整体前区高频号码
    full_front_counts = Counter([num for sublist in df['前区号码'] for num in sublist])
    full_top_front = [num for num, count in full_front_counts.most_common(10)]

    # 获取整体后区高频号码
    full_back_counts = Counter([num for sublist in df['后区号码'] for num in sublist])
    full_top_back = [num for num, count in full_back_counts.most_common(5)]

    # 获取星期三的前区高频号码
    wed_front_counts = Counter([num for sublist in wednesday_data['前区号码'] for num in sublist])
    wed_top_front = [num for num, count in wed_front_counts.most_common(10)]

    # 获取星期三的后区高频号码
    wed_back_counts = Counter([num for sublist in wednesday_data['后区号码'] for num in sublist])
    wed_top_back = [num for num, count in wed_back_counts.most_common(5)]

    print("\n整体历史高频号码:")
    print(f"前区: {', '.join(map(str, full_top_front))}")
    print(f"后区: {', '.join(map(str, full_top_back))}")

    print("\n星期三历史高频号码:")
    print(f"前区: {', '.join(map(str, wed_top_front))}")
    print(f"后区: {', '.join(map(str, wed_top_back))}")

    print("\n预测号码组合:")
    for strategy, (front, back) in predictions.items():
        print(f"{strategy}:")
        print(f"  前区: {', '.join(map(str, front))}")
        print(f"  后区: {', '.join(map(str, back))}")

    # 保存预测结果
    prediction_date = "2025-07-02"
    with open(f'星期统计/预测_{prediction_date}.txt', 'w', encoding='utf-8') as f:
        f.write(f"大乐透预测结果 ({prediction_date} 星期三)\n")
        f.write("=" * 50 + "\n")

        f.write("整体历史高频号码:\n")
        f.write(f"前区: {', '.join(map(str, full_top_front))}\n")
        f.write(f"后区: {', '.join(map(str, full_top_back))}\n\n")

        f.write("星期三历史高频号码:\n")
        f.write(f"前区: {', '.join(map(str, wed_top_front))}\n")
        f.write(f"后区: {', '.join(map(str, wed_top_back))}\n\n")

        f.write("预测号码组合:\n")
        for strategy, (front, back) in predictions.items():
            f.write(f"{strategy}:\n")
            f.write(f"  前区: {', '.join(map(str, front))}\n")
            f.write(f"  后区: {', '.join(map(str, back))}\n\n")

    print("\n预测结果已保存到: 星期统计/预测_2025-07-02.txt")
else:
    print("警告: 没有找到星期三的历史数据，无法进行预测")

print("\n统计完成！所有星期分类数据已保存到'星期统计'目录中")
print("包含以下文件：")
print("1. 各星期前区频率统计.csv")
print("2. 各星期后区频率统计.csv")
print("3. 各星期前后区组合频率统计.csv")
print("4. 各星期频率分布图.png")
print("5. 整体统计文件（整体前区频率统计.csv等）")
print("6. 预测结果文件")