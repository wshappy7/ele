#===========以json形式保存全国各个地方坐标=============
import requests
import json
headers={
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }
url=f'https://www.ele.me/restapi/shopping/v1/cities'
response=requests.get(url,headers=headers,verify=False).text
data_list=json.loads(response)
list=[]
for word,data in data_list.items():

    for d in data:
        # print(d)
        name=d.get('name')
        latitude=d.get('latitude')
        longitude=d.get('longitude')
        dict={}
        dict['name']=name
        dict['latitude']=latitude
        dict['longitude']=longitude
        list.append(dict)
print(list)
with open('city.json','w',encoding='utf-8')as fp:
    fp.write(json.dumps(list,ensure_ascii=False))