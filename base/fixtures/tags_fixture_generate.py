import requests
import json
import os


def generate_fixture():
    
    url = "https://api.bhuntr.com/cms/bhuntr/contest?language=tw&target=competition&limit=1000&page=1&sort=mixed&keyword=&timeline=notEnded&identify=&prizeRange=none&location=taiwan&deadline=none&category=&canApplyCertificate=no"

    response = requests.get(url).text
    res_json = json.loads(response)
    
    # 獲取當前py檔案絕對路徑
    script_path = os.path.dirname(os.path.abspath(__file__))
    # 構建寫入的完整路徑
    file_path = os.path.join(script_path, "tags_fixture.json")
    
    competition_data_list = res_json["payload"]["list"] 
    
    # char_pairs = list(product(map(chr, range(97, 123)), repeat=2))
    created_tags = []
    output_fixtures = []
    
    for data in competition_data_list:
        limit_highschool = data['identifyLimit']['highSchool']
        limit_none = data['identifyLimit']['none']
        limit_other = data['identifyLimit']['other']
        if limit_highschool or limit_none or limit_other:
            tags = data["tags"]
            if tags != None:
                for tag in tags:
                    if tag in created_tags:
                        continue
                    output_fixtures.append({"model": "base.competitiontag",
                                 "pk": len(created_tags)+1,
                                 "fields": {"tag_name": tag}})
                    created_tags.append(tag)
                    # print(f"第len(created_tags)個物件   建立成功")
    print(f"共建立{len(created_tags)}個物件")
    

    
    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(output_fixtures, fp, indent=2, ensure_ascii=False)         
        # file.write(json.dumps(output_fixtures, indent=2, ensure_ascii=False))       

if __name__ == "__main__":
    generate_fixture()
    