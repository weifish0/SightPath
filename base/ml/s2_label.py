
import os
import json
import re

import opencc
import numpy as np
from FlagEmbedding import BGEM3FlagModel

# 'activities_fixture.json'
# 'competitions_fixture.json'
FIXTURE = 'competitions_fixture.json'

MIN_TAG_SCORE = 0.5
MIN_TAG_NUM = 2
converter = opencc.OpenCC('tw2sp.json')
CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def cleanhtml(raw_html: str):
    cleantext = re.sub(CLEANR, '', raw_html.strip())
    return cleantext


model = BGEM3FlagModel(
    'BAAI/bge-m3', use_fp16=True)

base_path = os.path.abspath(
    os.path.dirname(
        os.path.dirname(__file__)
    ))
comp_path = os.path.join(base_path,
                         'fixtures', FIXTURE)

comp = open(comp_path, "r", encoding="utf-8")
ourtag_path = os.path.join(base_path,
                           'fixtures', 'ourtag_fixture.json')
f = open(ourtag_path, "r", encoding="utf-8")

data = json.load(comp)
df = json.load(f)

# Closing file
comp.close()
f.close()

tag_emb = [np.array(tag["fields"]["emb_org"]) for tag in df]

text_to_emb = []
for it in data:
    html = cleanhtml(
        it["fields"].get("description", it["fields"]["guide_line_html"]))
    summary = it["fields"].get("summary", "")
    if summary != "":
        summary += '\n'
    content = it["fields"]["name"]+'\n'+summary+html

    content = converter.convert(content)
    text_to_emb.append(content)

emb = model.encode(
    text_to_emb,
    batch_size=2,
    max_length=8192,
    # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
)['dense_vecs']


for i in range(len(data)):
    vec = [emb[i] @ it.T for it in tag_emb]
    data[i]["fields"]["emb_org"] = np.array(emb[i]).tolist()
    data[i]["fields"]["emb"] = np.array(vec).tolist()

    art = (-np.array(vec)).argsort()
    data[i]["fields"]["our_tags"] = art[:MIN_TAG_NUM]+1

    for ind in art[MIN_TAG_NUM:]:
        if vec[ind] >= MIN_TAG_SCORE:
            pk = ind+1
            data[i]["fields"]["our_tags"] = np.append(
                data[i]["fields"]["our_tags"], pk)
        else:
            data[i]["fields"]["our_tags"] = data[i]["fields"]["our_tags"].tolist()
            break


with open(comp_path, "w", encoding="utf-8") as fp:
    json.dump(data, fp, indent=2, ensure_ascii=False)
