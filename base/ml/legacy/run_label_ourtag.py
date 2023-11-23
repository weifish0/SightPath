import requests
import json
import os
# from datetime import datetime, timezone
from tags_description import *

from text2vec import SentenceModel
from sklearn.metrics.pairwise import cosine_similarity
# import opencc
import numpy as np

# "繪畫比賽","平面設計比賽","產品設計比賽","綜合設計",
#         "攝影比賽","影片比賽",
#         "文學獎","創意寫作",
#         "企劃競賽","創業競賽","程式競賽",
#         "音樂大賽","歌唱比賽","詞曲創作",
#         "運動","選秀"

        

def generate_tags():
    model = SentenceModel("GanymedeNil/text2vec-large-chinese")

    json_path = os.getcwd()+'/base/fixtures/ourtag_fixture.json'
    output_tags_fixture = []

    for i in range(len(tags)):
        output_tags_fixture.append({"model": "base.ourtag",
                                    "pk": i+1,
                                    "fields": {"tag_name": tags[i],
                                               "description": descriptions[i]}})
    
    tag_emb = []
    for tag in output_tags_fixture:
        ######
        emb1 = model.encode(tag["fields"]["description"][0:400])
        # inputs = tokenizer(tag["fields"]["description"][0:400], return_tensors="pt")
        # emb1 = model(**inputs).pooler_output.detach().numpy()
        # print(emb1)
        ######
        tag_emb.append(emb1.reshape(1, -1))
        tag["fields"]["emb_org"] = np.array(emb1).tolist()


    for i in range(len(output_tags_fixture)):
        vec = []

        for pk in range(len(tag_emb)):
            # if pk+1==11 and i==290:
            score = cosine_similarity(
                tag_emb[i], tag_emb[pk])[0][0]
            vec.append(score)

        output_tags_fixture[i]["fields"]["emb"] = np.array(vec).tolist()
    
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(output_tags_fixture, fp, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_tags()