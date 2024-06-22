import matplotlib.pyplot as plt
import matplotlib
from numpy import random
import seaborn as sns
import os
import io
import matplotlib.font_manager as font_manager

# /home/ubuntu/SightPath/base/api/


def persona_chart(y):
    # print(os.path.dirname(os.path.abspath(__file__)))
    font_manager.fontManager.addfont(
        os.path.dirname(os.path.abspath(__file__)) + "/msjh.ttc"
    )
    # print([f.name for f in font_manager.fontManager.ttflist])

    # print([f.name for f in font_manager.fontManager.ttflist])
    figure = io.BytesIO()
    # x = [67.98, 54.23, 40.67]
    # y = [67.98, 54.23, 40.67, 29, 13, 14, 17,
    #      15, 29, 12, 21, 20, 18, 18, 13, 14, 9]
    # x.extend(random.randint(1, 30, 14))
    # print(x)

    data_categories = ["資訊", "工程", "數理化", "醫藥衛生", "生命科學", "生物資源",
                       "地球與環境", "建築與設計", "藝術", "社會與心理", "大眾傳播", "外語",
                       "文史哲", "教育", "法政", "管理", "財經", "遊憩與運動"]

    explode_data = []
    for i in range(len(data_categories)):
        explode_data.append(0.05)

    color = '447D7A'

    sns.set(font_scale=1.2)

    matplotlib.rc('font', family='Microsoft JhengHei')
    matplotlib.rcParams['text.color'] = 'white'
    plt.figure(figsize=(8, 8))

    plt.pie(y,
            textprops={'weight': 'bold', 'size': 14},  # 設定文字樣式
            pctdistance=0.8,
            labels=data_categories,
            autopct="%.1f%%",
            explode=explode_data,
            colors=sns.color_palette('Set2'),
            wedgeprops={"edgecolor": "white",
                        'linewidth': 0.3,
                        'antialiased': True})

    # plt.title(
    #     label="個人興趣傾向",
    #     fontdict={"fontsize": 16},
    #     pad=20
    # )

    # Add a hole in the pie
    # 正常版
    hole = plt.Circle((0, 0), 0.65, color="#447D7A")

    # 去背版
    # hole = plt.Circle((0, 0), 0.65, facecolor='none')

    plt.gcf().gca().add_artist(hole)

    script_path = os.path.dirname(os.path.abspath(__file__))
    final_script_path = os.path.join(script_path, 'test_persona.svg')

    # 存圖片
    plt.savefig(figure, format="png", transparent=True)
    return figure
    # plt.show()
