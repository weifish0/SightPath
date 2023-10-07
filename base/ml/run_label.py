import os
import json
import tags
from text2vec import SentenceModel
import re
from sklearn.metrics.pairwise import cosine_similarity

CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

def cleanhtml(raw_html: str):
    cleantext = re.sub(CLEANR, '', raw_html.strip())
    return cleantext

if __name__ == "__main__":
    # 支持多语言的句向量模型（CoSENT），多语言（包括中英文）语义匹配任务推荐，支持fine-tune继续训练
    model = SentenceModel("shibing624/text2vec-base-multilingual")
    #pool = model.start_multi_process_pool()
    comp_path = os.getcwd()+'\\base\\fixtures\\competitions_fixture.json'
    tag_emb = []
    tags.generate_tags()

    comp = open(comp_path,"r",encoding="utf-8")
    f = open(os.getcwd()+'\\base\\fixtures\\tags_fixture.json',"r",encoding="utf-8")
    data = json.load(comp)
    df = json.load(f)
    # Closing file
    comp.close()
    f.close()    

    for tag in df:
        emb1 = model.encode(tag["fields"]["tag_name"])
        tag_emb.append(emb1.reshape(1, -1))

    i=0
    for d in data:
        i+=1
        print("rounds "+str(i)+'\n')

        html = cleanhtml(d["fields"]["guide_line_html"])
        emb2 = model.encode(d["fields"]["name"]+' '+html).reshape(1, -1)
        d["fields"]["tags"] = []

        for pk in range(len(tag_emb)):
            score = cosine_similarity(tag_emb[pk], emb2)[0][0]
            #print(score)

            if score>0.8:
                d["fields"]["tags"].append(pk+1)
                with open(comp_path, "w", encoding="utf-8") as fp:
                    json.dump(data, fp, indent=2, ensure_ascii=False)


