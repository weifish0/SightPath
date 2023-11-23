import os
import json
from text2vec import SentenceModel
# from transformers import BertTokenizer, BertModel
import re
from sklearn.metrics.pairwise import cosine_similarity
# import opencc
import numpy as np

# converter = opencc.OpenCC('tw2sp.json')
CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def cleanhtml(raw_html: str):
    cleantext = re.sub(CLEANR, '', raw_html.strip())
    return cleantext


if __name__ == "__main__":
    # 支持多语言的句向量模型（CoSENT），多语言（包括中英文）语义匹配任务推荐，支持fine-tune继续训练
    model = SentenceModel("GanymedeNil/text2vec-large-chinese")
    # tokenizer = BertTokenizer.from_pretrained(
    #     # 可选，huggingface 中的预训练模型名称或路径，默认为 bert-base-chinese
    #     pretrained_model_name_or_path='bert-base-chinese',
    #     cache_dir=None,  # 将数据保存到的本地位置，使用cache_dir 可以指定文件下载位置
    #     force_download=False,
    # )
    # model = BertModel.from_pretrained('bert-base-chinese')

    # pool = model.start_multi_process_pool()
    comp_path = os.getcwd()+'/base/fixtures/activities_fixture.json'
    tag_emb = []

    comp = open(comp_path, "r", encoding="utf-8")
    ourtag_path = os.getcwd()+'/base/fixtures/ourtag_fixture.json'
    f = open(ourtag_path, "r", encoding="utf-8")

    data = json.load(comp)
    df = json.load(f)
    # Closing file
    comp.close()
    f.close()

    for tag in df:
        emb1 = np.array(tag["fields"]["emb_org"])
        tag_emb.append(emb1.reshape(1, -1))

    i = 0
    for d in range(len(data)):
        score_v = []
        i += 1
        print("rounds "+str(i))

        # html = ""
        html = cleanhtml(data[d]["fields"]["guide_line_html"])
        summary = data[d]["fields"]["summary"]

        ######
        content = data[d]["fields"]["name"]+' '+summary+' '+html

        emb2 = model.encode(content[0:400]).reshape(1, -1)

        # inputs = tokenizer(content[0:400], return_tensors="pt")
        # emb2_unshape = model(**inputs).pooler_output.detach().numpy()
        ######
        # +' '+html
        data[d]["fields"]["our_tags"] = []
        vec = []

        # np.array(emb2_unshape).tolist()

        for pk in range(len(tag_emb)):
            # if pk+1==11 and i==290:
            score = cosine_similarity(
                emb2, tag_emb[pk])[0][0]
            vec.append(score)

            if score > 0.4:
                data[d]["fields"]["our_tags"].append(pk+1)
            # score_v.append(score)

        data[d]["fields"]["emb"] = np.array(vec).tolist()

    with open(comp_path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)

        """
        vec = sorted(score_v)
        data[d]["fields"]["tags"].append(score_v.index(vec[-1])+1)
        data[d]["fields"]["tags"].append(score_v.index(vec[-2])+1)
        data[d]["fields"]["tags"].append(score_v.index(vec[-3])+1)
        """
