import requests
import json

url = "https://api.bhuntr.com/cms/bhuntr/contest?language=tw&target=competition&limit=1000&page=1&sort=mixed&keyword=&timeline=notEnded&identify=&prizeRange=none&location=taiwan&deadline=none&category=&canApplyCertificate=no"

r = requests.get(url)
print(r.status_code)
raw_json = r.json()
# print(r.encoding)

with open("bhunter_data.json", "w", encoding="utf-8") as fp:
    json.dump(raw_json, fp, ensure_ascii=False) 
