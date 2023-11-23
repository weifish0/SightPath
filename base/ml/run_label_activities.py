import os
import json
import re
import numpy as np
from tags_description import *
from transformers import pipeline
pipe = pipeline("zero-shot-classification", model="yechen/bert-large-chinese", device=0)

# converter = opencc.OpenCC('tw2sp.json')
CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
def cleanhtml(raw_html: str):
    cleantext = re.sub(CLEANR, '', raw_html.strip())
    return cleantext


comp_path = os.getcwd()+'/base/fixtures/activities_fixture.json'
ourtag = tags

comp = open(comp_path, "r", encoding="utf-8")
data = json.load(comp)
comp.close()

for d in range(len(data)):
    print("rounds "+str(d))

    html = cleanhtml(data[d]["fields"]["guide_line_html"])
    summary = data[d]["fields"]["summary"]
    content = data[d]["fields"]["name"]+' '+summary+' '+html

    data[d]["fields"]["our_tags"] = []
    vec = pipe(content[0:400], candidate_labels=ourtag)["scores"]
    for i in range(len(vec)):
        if vec[i] > 0.4:
            data[d]["fields"]["our_tags"].append(i+1)

    data[d]["fields"]["emb"] = np.array(vec).tolist()


with open(comp_path, "w", encoding="utf-8") as fp:
    json.dump(data, fp, indent=2, ensure_ascii=False)
