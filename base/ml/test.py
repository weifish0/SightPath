import os
import json
import tags
from text2vec import SentenceModel
import re
from sklearn.metrics.pairwise import cosine_similarity
import opencc

converter = opencc.OpenCC('tw2sp.json')

CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

def cleanhtml(raw_html: str):
    cleantext = re.sub(CLEANR, '', raw_html.strip())
    return cleantext

if __name__ == "__main__":
    # 支持多语言的句向量模型（CoSENT），多语言（包括中英文）语义匹配任务推荐，支持fine-tune继续训练
    model = SentenceModel("GanymedeNil/text2vec-base-chinese")
    #pool = model.start_multi_process_pool()

    emb2 = model.encode(converter.convert("程式競賽")).reshape(1, -1)
    emb1 = model.encode(converter.convert("2023 第二十五屆網際網路程式設計全國大賽")).reshape(1, -1)
    score = cosine_similarity(emb1, emb2)[0][0]
    print(score)


