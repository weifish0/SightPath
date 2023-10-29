import requests
import json
import os
from datetime import datetime, timezone

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}

def generate_activity_fixture(url, last_index, tag_index):
    response = requests.get(url)
    res_json = response.json()
    
    activities_data_list = res_json["channel"]["tagEvents"]
    
    output_activities_fixture = []
    
    for data_index, data in enumerate(activities_data_list):
        name = data["name"]
        eventIdNumber = data["eventIdNumber"]
        startDateTime = data["startDateTime"]
        endDateTime = data["endDateTime"]
        eventPlaceType = data["eventPlaceType"]
        location = data["location"]
        likeCount = data["likeCount"]
        pageView = data["pageView"]
        isAD = data["isAD"]
        photoUrl = data["photoUrl"]
        
        # enumerate產出的第一個index是0，所以要加一
        data_index += 1
        
        output_activities_fixture.append({"model": "base.activity",
                        "pk": data_index+last_index,
                        "fields": {"name": name,
                                   "eventIdNumber": eventIdNumber,
                                   "start_time": startDateTime,
                                   "end_time": endDateTime,
                                   "eventPlaceType": eventPlaceType,
                                   "location": location,
                                   "likeCount": likeCount,
                                   "pageView": pageView,
                                   "isAD": isAD,
                                   "photoUrl": photoUrl,
                                   "mainTag": tag_index}})
    created_data_num = len(output_activities_fixture)
        
    return output_activities_fixture, created_data_num            
                    

def generate_multiple_activity_fixture(tags_list):
    output_activities_fixture = []
    activities_count = 0
    for tag_index, url in enumerate(webcrawler_url_list(tags_list)):
        # enumerate產出的第一個index是0，所以要加一
        tag_index += 1
        data, data_num = generate_activity_fixture(url, activities_count, tag_index)
        output_activities_fixture.extend(data)
        activities_count += data_num
        print(f"已建立{activities_count}個activity物件")
    return output_activities_fixture
    

def generate_tags_fixture(tags_list):
    output_activity_tags_fixture = []
    for tag_index, tag_name in enumerate(tags_list):
        # enumerate產出的第一個index是0，所以要加一
        tag_index += 1
        output_activity_tags_fixture.append({"model": "base.activityTag",
                            "pk": tag_index,
                            "fields": {"tag_name": tag_name}})
    print(f"已建立{len(output_activity_tags_fixture)}個activityTag物件")
    
    return output_activity_tags_fixture

    
def webcrawler_url_list(tags_list):
    basic_url = "https://api.accupass.com/v3/home/north/channel"
    url_list = []
    for tag in tags_list:
        url_list.append(f"{basic_url}/{tag}")   
    return url_list


def grab_test_webdata(url, name):
    response = requests.get(url, headers=headers).json()
    with open(f'{name}.json', 'w+', encoding='utf-8') as fp:
        json.dump(response, fp, indent=2, ensure_ascii=False)
        

if __name__ == "__main__":
    test_url = "https://api.accupass.com/v3/home/north/channel/learning"
    
    tags_list = ['travel', 'fashion', 'blockchain', 'investment', 'startup', 
                'entertainment', 'design', 'pet', 'sports', 'business', 'learning', 
                'family', 'food', 'film', 'health', 'charitable', 'music', 'technology', 
                'handmade', 'arts', 'photography']
    
    grab_test_webdata("https://api.accupass.com/v3/home/north/channel/learning", name="arts_activities_data")
    
    # output_activity_tags_fixture = generate_tags_fixture(tags_list)
    
    # output_activities_fixture = generate_multiple_activity_fixture(tags_list)
    
    # # 獲取當前py檔案絕對路徑
    # script_path = os.path.dirname(os.path.abspath(__file__))
    # # 構建寫入的完整路徑
    # activities_fixture_file_path = os.path.join(script_path, "activities_fixture.json")
    # activity_tags_fixture_file_path = os.path.join(script_path, "activity_tags_fixture.json")
    
    # with open(activities_fixture_file_path, "w+", encoding="utf-8") as fp:
    #     json.dump(output_activities_fixture, fp, indent=2, ensure_ascii=False)
        
    # with open(activity_tags_fixture_file_path, "w+", encoding="utf-8") as fp:
    #     json.dump(output_activity_tags_fixture, fp, indent=2, ensure_ascii=False)
        
    
          
    
