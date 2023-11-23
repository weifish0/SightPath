import json
import os
from tags_description import *
from transformers import pipeline
import numpy as np
pipe = pipeline("zero-shot-classification", model="morit/chinese_xlm_xnli")
# morit/chinese_xlm_xnli
# yechen/bert-large-chinese
# fnlp/bart-large-chinese
# GanymedeNil/text2vec-large-chinese

# "繪畫比賽","平面設計比賽","產品設計比賽","綜合設計",
#         "攝影比賽","影片比賽",
#         "文學獎","創意寫作",
#         "企劃競賽","創業競賽","程式競賽",
#         "音樂大賽","歌唱比賽","詞曲創作",
#         "運動","選秀"


json_path = os.getcwd()+'/base/fixtures/ourtag_fixture.json'
output_tags_fixture = []

for i in range(len(tags)):
    output_tags_fixture.append({"model": "base.ourtag",
                                    "pk": i+1,
                                    "fields": {"tag_name": tags[i],
                                               "description": descriptions[i]}})

ourtag = tags
for i in range(len(descriptions)):
    result = pipe(descriptions[i][0:400], candidate_labels=ourtag)
    # ind = [ourtag.index(d) for d in result["labels"]]
    # vec = np.array(result["scores"])[ind]

    output_tags_fixture[i]["fields"]["emb"] = np.array(result["scores"]).tolist()


with open(json_path, "w", encoding="utf-8") as fp:
    json.dump(output_tags_fixture, fp, indent=2, ensure_ascii=False)
