
import json
import os
# from datetime import datetime, timezone

from tags_description import *
import numpy as np
from FlagEmbedding import BGEM3FlagModel

# 繁to簡
import opencc


def generate_tags():
    converter = opencc.OpenCC('tw2sp.json')
    descriptions_sp = [converter.convert(it) for it in descriptions]

    model = BGEM3FlagModel(
        'BAAI/bge-m3', use_fp16=True)
    # Setting use_fp16 to True speeds up computation with a slight performance degradation

    base_path = os.path.abspath(
        os.path.dirname(
            os.path.dirname(__file__)
        ))
    json_path = os.path.join(base_path,
                             'fixtures', 'ourtag_fixture.json')

    tag_emb = model.encode(
        descriptions_sp,
        batch_size=10,
        max_length=8192,
        # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
    )['dense_vecs']

    output_tags_fixture = []
    for i in range(len(tags)):
        output_tags_fixture.append(
            {
                "model": "base.ourtag",
                "pk": i+1,
                "fields": {
                    "tag_name": tags[i],
                    "description": descriptions[i],
                    "emb_org": np.array(tag_emb[i]).tolist(),
                }
            }
        )

    # np.array([]).tolist()
    for i in range(len(output_tags_fixture)):
        vec = [tag_emb[i] @ it.T for it in tag_emb]
        output_tags_fixture[i]["fields"]["emb"] = np.array(vec).tolist()

    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(output_tags_fixture, fp, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_tags()
