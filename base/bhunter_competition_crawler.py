import requests
import json
from .models import CompetitionTag, Competition

url = "https://api.bhuntr.com/cms/bhuntr/contest?language=tw&target=competition&limit=1000&page=1&sort=mixed&keyword=&timeline=notEnded&identify=&prizeRange=none&location=taiwan&deadline=none&category=&canApplyCertificate=no"

response = requests.get(url).text

res_json = json.loads(response)

competition_data_list = res_json["payload"]["list"]

n = 0
for data in competition_data_list:
    limit_highschool = data['identifyLimit']['highSchool']
    limit_none = data['identifyLimit']['none']
    limit_other = data['identifyLimit']['other']
    if limit_highschool or limit_none or limit_other:
        name = data["title"]
        url = data["officialUrl"]
        coverImage = data["coverImage"]["url"]
        startime = data["startTime"]
        endtime = data['endTime']
        guideline = data["guideline"]
        agencyTitle = data["agencyTitle"]
        pageViews = data["analyticsFlag"]["pageViews"]
        contactEmail = data["contactEmail"]
        contactName = data["contactName"]
        contactPhone = data["contactPhone"]
        
        # 處理
        tags = data["tags"]
        if tags != []:
            for tag in tags:
                competition_tag, created = CompetitionTag.objects.get_or_create(tag_name=tag)
                if created:
                    n += 1
                    print(f"成功建立物件{n}")
        
        # # 在資料庫中新增room
        # Competition.objects.create(host=name,
        #                            topic=url,
        #                            name=coverImage,
        #                            description=request.POST.get("description"))
        

    else:
        print("不再範圍內")
    
    
    
    
    
