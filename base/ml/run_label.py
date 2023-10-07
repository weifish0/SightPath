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
        emb1 = model.encode(converter.
                            convert(tag["fields"]["tag_name"]))
        tag_emb.append(emb1.reshape(1, -1))

    i=0
    for d in range(len(data)):
        score_v=[]
        i+=1
        print("rounds "+str(i))

        html = cleanhtml(data[d]["fields"]["guide_line_html"])
        emb2 = model.encode(converter.
                            convert(data[d]["fields"]["name"])).reshape(1, -1)
        # +' '+html
        data[d]["fields"]["tags"] = []

        for pk in range(len(tag_emb)):
            #if pk+1==11 and i==290:
            score = cosine_similarity(emb2, tag_emb[pk])[0][0]
            if score>0.4:
                data[d]["fields"]["tags"].append(pk+1)
            #score_v.append(score)

        """
        vec = sorted(score_v)
        data[d]["fields"]["tags"].append(score_v.index(vec[-1])+1)
        data[d]["fields"]["tags"].append(score_v.index(vec[-2])+1)
        data[d]["fields"]["tags"].append(score_v.index(vec[-3])+1)
        """


    with open(comp_path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)
