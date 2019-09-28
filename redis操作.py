# #存入redis数据库
import redis
import time


pool =redis.ConnectionPool(host='127.0.0.1',password='')
r=redis.Redis(connection_pool=pool)
for x in range(-80,80,20):#经度
    for y in range(-80,80,20):#维度
        # time.sleep(3)
        # latitude=39.90469 #北京
        # longitude = 116.407173
        latitude = 29.564711  # 重庆
        longitude = 106.550728
        latitude = str('%.6f' % (latitude+x/1000))#拼接生成经度
        longitude = str('%.6f' % (longitude + y/1000)) #拼接生成纬度
        print(latitude,longitude)
        for i in range(0, 120, 30):#设置offset的起始位置
            print(f"===={x}==={y}=====" + str(i))
            url=f'https://h5.ele.me/restapi/shopping/v3/restaurants?latitude={latitude}&longitude={longitude}&offset={i}&limit=30&extras[]=activities&extras[]=tags&extra_filters=home&rank_id=18fbf58702554919b399dce3a4830bcc&terminal=h5'
            print(url)
            # r.rpush('ele:url',url)#列表插入
            r.rpush('chongqing',url)#列表插入
            # r.sadd('first_urlsss',url)#集合插入，有去重的效果

# pool =redis.ConnectionPool(host='127.0.0.1',password='')
# r=redis.Redis(connection_pool=pool)
# while True:
#     time.sleep(2)
#     url=r.lpop('chongqing').decode('utf8')#返回并删除列表的第一个value
#     # url=r.spop('ele:url').decode('utf8')#返回并删除集合随机的一个value
#     print(url)


#==================插入所有城市所有url===============
# import redis
# import json
# pool = redis.ConnectionPool(host='127.0.0.1', password='')
# r = redis.Redis(connection_pool=pool)
# with open('city.json',encoding='utf-8') as fp:  # with在不需要访问文件后将其关闭。
#     contents = json.loads(fp.read())
#     for con in contents:
#         name=con.get('name')
#         latitude=con.get('latitude')
#         longitude=con.get('longitude')
#         print(name,latitude,longitude)
#         for x in range(-80, 80, 20):  # 经度
#             for y in range(-80, 80, 20):  # 维度
#                 # time.sleep(3)
#                 latitude = float(latitude)  # 北京
#                 longitude = float(longitude)
#                 # latitude = 29.564711  # 重庆
#                 # longitude = 106.550728
#                 latitude = str('%.6f' % (latitude + x / 1000))  # 拼接生成经度
#                 longitude = str('%.6f' % (longitude + y / 1000))  # 拼接生成纬度
#                 # print(latitude, longitude)
#                 for i in range(0, 120, 30):  # 设置offset的起始位置
#                     # print(f"===={x}==={y}=====" + str(i))
#                     url = f'https://h5.ele.me/restapi/shopping/v3/restaurants?latitude={latitude}&longitude={longitude}&offset={i}&limit=30&extras[]=activities&extras[]=tags&extra_filters=home&rank_id=18fbf58702554919b399dce3a4830bcc&terminal=h5'
#                     # print(url)
#                     # r.rpush('ele:url',url)#列表插入
#                     r.rpush('city', url)  # 列表插入
#                     # r.sadd('first_urlsss',url)#集合插入，有去重的效果