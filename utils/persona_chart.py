import matplotlib.pyplot as plt
import matplotlib
from numpy import random
import seaborn as sns


x = [67.98, 54.23, 40.67]
x.extend(random.randint(1, 30, 14))
print(x)

data_categories = ["資訊工程",
                   "數理化學",
                   "醫藥衛生",
                   "生命科學",
                   "生物資源",
                   "地球與環境",
                   "建築與設計",
                   "藝術",
                   "社會與心理",
                   "大眾傳播",
                   "外語",
                   "文史哲",
                   "教育",
                   "法政",
                   "管理",
                   "財經",
                   "遊憩與運動"]


explode_data = []
for i in range(len(data_categories)):
    explode_data.append(0.05)

sns.set(font_scale = 1.2)
matplotlib.rc('font', family='Microsoft JhengHei')
plt.figure(figsize=(8,8))

plt.pie(x,
        textprops={'weight': 'bold', 'size': 14},  # 設定文字樣式
        pctdistance=0.8,
        labels=data_categories,
        autopct="%.1f%%",
        explode=explode_data,
        colors=sns.color_palette('Set2'))


plt.title(
    label="個人興趣傾向",
    fontdict={"fontsize": 16},
    pad=20
)

# Add a hole in the pie
hole = plt.Circle((0, 0), 0.65, facecolor='white')
plt.gcf().gca().add_artist(hole)

plt.show()
