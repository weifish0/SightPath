import requests
import json
import os
from datetime import datetime, timezone

def generate_fixture():
    
    web_url = "https://api.bhuntr.com/cms/bhuntr/contest?language=tw&target=competition&limit=1000&page=1&sort=mixed&keyword=&timeline=notEnded&identify=&prizeRange=none&location=taiwan&deadline=none&category=&canApplyCertificate=no"

    response = requests.get(web_url).text
    res_json = json.loads(response)
    
    # 獲取當前py檔案絕對路徑
    script_path = os.path.dirname(os.path.abspath(__file__))
    # 構建寫入的完整路徑
    tags_fixture_file_path = os.path.join(script_path, "tags_fixture.json")
    competitions_fixture_file_path = os.path.join(script_path, "competitions_fixture.json")
    
    competition_data_list = res_json["payload"]["list"] 
    
    created_tags = []
    output_tags_fixture = []
    
    created_competitions = []
    output_competitions_fixture = []
    
    # 建立比賽所有包含的tag物件
    for data in competition_data_list:
        limit_highschool = data['identifyLimit']['highSchool']
        limit_none = data['identifyLimit']['none']
        limit_other = data['identifyLimit']['other']
        
        # 確保是高中生能夠參加的比賽
        if limit_highschool or limit_none or limit_other:        
            tags = data["tags"]
            if tags != None:
                for tag in tags:
                    # 
                    if tag in created_tags:
                        continue
                    output_tags_fixture.append({"model": "base.competitiontag",
                                            "pk": len(created_tags)+1,
                                            "fields": {"tag_name": tag}})
                    created_tags.append(tag)
            
    # 建立competition物件
    for data in competition_data_list:
        limit_highschool = data['identifyLimit']['highSchool']
        limit_none = data['identifyLimit']['none']
        limit_other = data['identifyLimit']['other']
        
        # 確保是高中生能夠參加的比賽
        if limit_highschool or limit_none or limit_other:
            name = data["title"]        
            url = data["officialUrl"]
            cover_img_url = data["coverImage"]["url"]
            
            start_time_obj = datetime.fromtimestamp(data["startTime"])
            end_time_obj = datetime.fromtimestamp(data['endTime'])
            start_time_str = start_time_obj.strftime('%Y-%m-%d %H:%M:%S')
            end_time_str = end_time_obj.strftime('%Y-%m-%d %H:%M:%S')  
            
            guide_line = data["guideline"]
            organizer_title = data["organizerTitle"]
            page_views = data["analyticsFlag"]["pageViews"]
            contact_email = data["contactEmail"]
            contact_name = data["contactName"]
            contact_phone = data["contactPhone"]
            tags = data["tags"]
            
            # 將 tags藉由created_tags處理成適合manytomanyfield的格式，方便之後建立competition物件
            competition_related_tags = []
            if tags != None:
                for tag in tags:
                    tag_id_index = created_tags.index(tag)+1
                    
                    # 將tag id新增到competition_related_tags
                    competition_related_tags.append(tag_id_index)
            
                
            output_competitions_fixture.append({"model": "base.competition",
                        "pk": len(created_competitions)+1,
                        "fields": {"name": name,
                                   "url": url,
                                   "cover_img_url": cover_img_url,
                                   "start_time": start_time_str,
                                   "end_time": end_time_str,
                                   "guide_line_html": guide_line,
                                   "organizer_title": organizer_title,
                                   "page_views": page_views,
                                   "contact_email": contact_email,
                                   "contact_name": contact_name,
                                   "contact_phone": contact_phone,
                                   "tags": competition_related_tags,
                                   "limit_highschool": limit_highschool,
                                   "limit_none": limit_none,
                                   "limit_other": limit_other}})
            created_competitions.append(name)
                    
                    
                    
    print(f"共建立{len(created_tags)}個tag物件")
    print(f"共建立{len(created_competitions)}個competition物件")
    
    
    with open(tags_fixture_file_path, "w", encoding="utf-8") as fp:
        json.dump(output_tags_fixture, fp, indent=2, ensure_ascii=False)         
        # file.write(json.dumps(output_fixtures, indent=2, ensure_ascii=False))   
            
    with open(competitions_fixture_file_path, "w", encoding="utf-8") as fp:
        json.dump(output_competitions_fixture, fp, indent=2, ensure_ascii=False)         
        # file.write(json.dumps(output_fixtures, indent=2, ensure_ascii=False))       

if __name__ == "__main__":
    generate_fixture()
    