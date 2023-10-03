import requests
import json
import os
from datetime import datetime, timezone


def generate_fixture(url, last_index):
    web_url = url
    response = requests.get(web_url).text
    res_json = json.loads(response)
    
    activities_data_list = res_json["channel"]["tagEvents"]
    
    output_activities_fixture = []
    
    for data_index ,data in enumerate(activities_data_list):
        eventIdNumber = data["eventIdNumber"]
        photoUrl = data["photoUrl"]
        name = data["name"]
        startDateTime = data["startDateTime"]
        endDateTime = data["endDateTime"]
        eventPlaceType = data["eventPlaceType"]
        location = data["location"]
        tags = ""
        for tag in data["tags"]:
            tags = tags+(tag["name"])
        isAD = data["isAD"]
        output_activities_fixture.append({"model": "base.activities",
                        "pk": data_index+1+last_index,
                        "fields": {"name": name,
                                   "eventIdNumber": eventIdNumber,
                                   "start_time": startDateTime,
                                   "end_time": endDateTime,
                                   "eventPlaceType": eventPlaceType,
                                   "location": location,
                                   "isAD": isAD,
                                   "photoUrl": photoUrl,
                                   "strtags": tags}})
    created_data_num = len(output_activities_fixture)
        
    return output_activities_fixture, created_data_num            
                    
    
        

        
def webcrawler_url_list(tags_list):
    basic_url = "https://api.accupass.com/v3/home/north/channel"
    
    url_list = []
    for tag in tags_list:
        url_list.append(f"{basic_url}/{tag}")   
    return url_list

if __name__ == "__main__":
    test_url = "https://api.accupass.com/v3/home/north/channel/learning"
    
    tags_list = ['travel', 'fashion', 'blockchain', 'investment', 'startup', 
                'entertainment', 'design', 'pet', 'sports', 'business', 'learning', 
                'family', 'food', 'film', 'health', 'charitable', 'music', 'technology', 
                'handmade', 'arts', 'photography']
    
    output_activities_fixture = []
    activities_count = 0
    for url in webcrawler_url_list(tags_list):
        data, data_num = generate_fixture(test_url, activities_count)
        output_activities_fixture.extend(data)
        activities_count += data_num
        print(f"已建立{activities_count}個activity物件")
    
    # 獲取當前py檔案絕對路徑
    script_path = os.path.dirname(os.path.abspath(__file__))
    # 構建寫入的完整路徑
    activities_fixture_file_path = os.path.join(script_path, "activities_fixture.json")
    
    with open(activities_fixture_file_path, "w+", encoding="utf-8") as fp:
        json.dump(output_activities_fixture, fp, indent=2, ensure_ascii=False)
          
    
