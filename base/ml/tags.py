import requests
import json
import os
from datetime import datetime, timezone

tags = ["繪畫比賽","平面設計比賽","產品設計比賽","綜合設計",
        "攝影比賽","影片比賽",
        "文學獎","創意寫作",
        "企劃競賽","創業競賽","程式競賽",
        "音樂大賽","歌唱比賽","詞曲創作",
        "運動","選秀"]

def generate_tags():
    json_path = os.getcwd()+'\\base\\fixtures\\tags_fixture.json'
    output_tags_fixture = []

    for i in range(len(tags)):
        output_tags_fixture.append({"model": "base.competitiontag",
                                    "pk": i+1,
                                    "fields": {"tag_name": tags[i]}})
                    
    
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(output_tags_fixture, fp, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    generate_tags()
    