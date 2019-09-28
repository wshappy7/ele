import requests
import json
import time

import re

headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Mobile Safari/537.36',
        'Referer': 'https://h5.ele.me/',
        'X-Shard': 'loc=106.499063,29.586717, loc=106.499063,29.586717',
        'x-uab': '120#bX1bSBNWreISfhCvhLXLzzU/qNHWY+ZGzm0UO3RWJgihcFMCkyI9FCYac12ag/cL+6RiP8FsfskrBTF4gjwEUOBUUJa66Y38ETkztF9TAwYWlDqrnXbYH1T4+NlEC9bCbjcyknLFlAPs0l7Saz+bNFYvSi5/ybbS7UGPWWl/oYk6ymfVEfFcDIxYg6ikmtf6RNdPTbjg8/I9iVXZZeQzsjfnaGINO+vtehnTO/7qhyw7B2z1ZwLbmojBiw9divBeHPr8LDdaVHnlUGIrRc4QoEJlvFFnS9N/VZ7RPGnGkkSPT22xtP/bMrewnJF6YSZ+ubEuDsQDxIOXGYUg/39npjQ6uhRvIReQqPO4IJl1yY6JQZcjaCZJaIZ9GpCgGjjLTkyOeCtBtOQSX23jqWo37UCgIQ6+5YqM84xPMwHnQGJ0XsxYfc6GT4wELOqLRlRIJa8VUO9aC2UXrjgan9Nk4wnI7n15jkDs6a0mgWTLVOfoiZj9i2j19lom/Vw+cG9vIrmJe9Zy3JGNzkme+q3lLsCw/GE7C8LxeaV9p2D='
    }
#========导入cookie===============
from get_cookie import getCookie
from selenium import webdriver
while True:
    driver = webdriver.Chrome(executable_path=r'chromedriver.exe')
    try:
        c=getCookie(driver).get_phone()
        break
    except Exception as e:
        print(e)
        driver.close()

        pass
headers['Cookie']=c


#或取userid以便详情页提取
userid=re.findall(r'USERID=(.*?);',headers.get('Cookie'),re.S)[0]


import redis
pool =redis.ConnectionPool(host='127.0.0.1',password='')
r=redis.Redis(connection_pool=pool)
while True:

    url=r.lpop('anxin').decode('utf8')#返回并删除列表的第一个value

    print(url)

    try:
        response=requests.get(url,headers=headers,verify=False,timeout=3).text
        time.sleep(2)
        print(response)
        if '用户网络信息异常' in response:
            for i in range(10):
                response = requests.get(url, headers=headers, verify=False, proxies=proxies, timeout=3).text
                if '用户网络信息异常' not in response:
                    break
                time.sleep(2)
        print(response)
        data=json.loads(response)
        item_list=data['items']
        for item in item_list:
            restaurant=item.get('restaurant')
            name=restaurant.get('name').strip()
            print(name)
            id = restaurant.get('id')
            print(id)


    except Exception as e:
        print(e)
        print("列表页列表页列表页列表页列表页列表页列表页列表页")

        # proxies = CheckIp().check_ip()






