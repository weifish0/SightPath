import requests
import json
import os
from tqdm import tqdm


def accupass_crawler(payload_data: dict) -> object:
    url = 'https://api.accupass.com/v3/search/SearchEvents'
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
    res = requests.post(url, json=payload_data, headers=headers, )
    return res.json()
    
    
def load_download_path(fn: str) -> str:
    # 獲取當前py檔案目錄的絕對路徑
    script_path = os.path.dirname(os.path.abspath(__file__))
    # 構建寫入的完整路徑
    file_full_path = os.path.join(script_path, fn)
    return file_full_path


def download_json_fixtures(data: list, file_name: str):
    with open(load_download_path(f'{file_name}.json'), 'w', encoding='utf-8') as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False) 
    print(f'{file_name}下載完畢')


def required_post_times(category_index):
    payload = {"categoryTypeList": [f"{category_index}"],
                "simpleEventPlaceTypeList": [],
                "cityLocationList": [],
                "sortBy": "4",
                "timeType": "0",
                "currentIndex": 0}
    res_json = accupass_crawler(payload)
    rpt = (res_json['total'] // 25) + 1
    return rpt
    

def generate_multiple_activities_fixture(category_index_list: dict) -> list:
    output_activities_fixture = []
    activities_tags_list = []
    activity_num = 0
    for category, category_index in category_index_list.items():
        op_a, op_a_tags = generate_activities_fixture(category, category_index, activity_num)
        activity_num += len(op_a)
        output_activities_fixture.extend(op_a)
        activities_tags_list.extend(op_a_tags)

    # 不留重複的tags
    activities_tags_list = list(set(activities_tags_list))
    return output_activities_fixture, activities_tags_list
        

def generate_activities_fixture(category: str, category_index: int, 
                                activity_num: int = 0):
    activity_index = 0 # 作為活動物件的pk值
    
    # 建立儲存爬蟲資料的List
    output_activities_fixture = []
    activities_tags_list = []
    
    # 載入上一次活動爬蟲的pk值
    activity_index += activity_num
    
    payload = {"categoryTypeList": [f"{category_index}"],
                "simpleEventPlaceTypeList": [],
                "cityLocationList": [],
                "sortBy": "4",
                "timeType": "0",
                "currentIndex": 0}
    
    for current_index in tqdm(range(required_post_times(category_index)), desc=f'爬取{category}相關活動'):
        payload = {"categoryTypeList": [f"{category_index}"],
                    "simpleEventPlaceTypeList": [],
                    "cityLocationList": [],
                    "sortBy": "4",
                    "timeType": "0",
                    "currentIndex": current_index}
        res_json = accupass_crawler(payload)
        
        activities_data_list = res_json["items"]
        for activity in activities_data_list:
            name = activity["name"]
            eventIdNumber = activity["eventIdNumber"]
            startDateTime = activity["startDateTime"]
            endDateTime = activity["endDateTime"]
            eventPlaceType = activity["eventPlaceType"]
            location = activity["location"]
            likeCount = activity["likeCount"]
            pageView = activity["pageView"]
            isAD = activity["isAD"]
            photoUrl = activity["photoUrl"]
            
            tags = []
            web_tags_list = activity["tags"]
            for tag in web_tags_list:
                activities_tags_list.append(tag['name'])
                tags.append(tag['name'])
            if category not in tags:
                tags.append(category)
            
            activity_index += 1
            
            output_activities_fixture.append({"model": "base.activity",
                                                "pk": activity_index,
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
                                                        "tags": tags}})   

        activities_tags_list.append(category)
        activities_tags_list = list(set(activities_tags_list))

    return output_activities_fixture, activities_tags_list
         

def generate_activities_tags_fixture(tags: list) -> list:                    
    output_activities_tags_fixture = []
    for tag_index, tag in enumerate(tags):
        output_activities_tags_fixture.append({"model": "base.activitytag",
                                                    "pk": tag_index+1,
                                                    "fields": {"tag_name": tag}})
    return output_activities_tags_fixture
    
    
def transfer_activity_fixture_tags_to_pk(output_activities_fixture: list, activities_tags_list: list) -> list:
    for a in output_activities_fixture:
        for a_tag_index, a_tag in enumerate(a['fields']['tags']):
            a['fields']['tags'][a_tag_index] = activities_tags_list.index(a_tag) + 1


def change_json_file_timefield_format(fn: str) -> list:
    f = None
    with open(load_download_path(fn), 'r', encoding='utf-8') as f_json:
        f = json.load(f_json)
        for a in f:
            a['fields']['start_time'] = a['fields']['start_time'].replace('T', ' ')
            a['fields']['start_time'] = a['fields']['start_time'].replace('Z', '')
            a['fields']['end_time'] = a['fields']['end_time'].replace('T', ' ')
            a['fields']['end_time'] = a['fields']['end_time'].replace('Z', '')
    
    with open(load_download_path(fn), 'w', encoding='utf-8') as f_json:
        json.dump(f, f_json, indent=2, ensure_ascii=False)
        
        
def format_test(fn: str) -> list:
    f = None
    with open(load_download_path(fn), 'r', encoding='utf-8') as f_json:
        f = json.load(f_json)
        for a in f:
            a['fields'].pop("eventPlaceType")
            a['fields'].pop("eventPlaceType")
    with open(load_download_path(fn), 'w', encoding='utf-8') as f_json:
        json.dump(f, f_json, indent=2, ensure_ascii=False)

    

if __name__ == "__main__":
    tags_list = ['travel', 'fashion', 'blockchain', 'investment', 'startup', 
                'entertainment', 'design', 'pet', 'sports', 'business', 'learning', 
                'family', 'food', 'film', 'health', 'charitable', 'music', 'technology', 
                'handmade', 'arts', 'photography']
    category_index_list = {
        '戶外體驗': 4,
        '學習': 7,
        '藝文': 1,
        '手作': 20,
        '運動': 3,
        '寵物': 16,
        '攝影': 10,
        '科技': 5,
        '電影': 23,
        '設計': 19,
        '遊戲': 21,
        '音樂': 22,
        '健康': 12,
        '創業': 17,
        '公益': 9
    }

    # output_activities_fixture, activities_tags_list = generate_multiple_activities_fixture(category_index_list)
    
    # output_activities_tags_fixture = generate_activities_tags_fixture(activities_tags_list)
    
    # transfer_activity_fixture_tags_to_pk(output_activities_fixture, activities_tags_list)
    
    # print(f'新增{len(output_activities_fixture)}個 activity物件')
    # print(f'新增{len(output_activities_tags_fixture)}個 tag物件')
    
    # download_json_fixtures(output_activities_fixture, 'activities_fixture')
    # download_json_fixtures(output_activities_tags_fixture, 'activities_tags_fixture')
        
    change_json_file_timefield_format('activities_fixture.json')
    
          
    
