# -*- coding: utf-8 -*-
import urllib.request
from urllib.parse import quote
import numpy as np
import json, redis
import pandas as pd
from xpinyin import Pinyin
from pandas import Series, DataFrame
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s: %(message)s')


class Point:
	lng = ''
	lat = ''

	def __init__(self, lng, lat):
		self.lng = lng
		self.lat = lat


class Handle_LatLng(object):
	def __init__(self, key, addr_name, n):
		self.gd_key = key
		self.address = addr_name
		self.n = n
		self.distance_m = '{}m'.format(self.n * 1000)
		pool = redis.ConnectionPool(decode_responses=True)
		self.redis_conn = redis.Redis(connection_pool=pool)
		self.url = 'http://restapi.amap.com/v3/config/district?'

		self.pinyin = Pinyin()
		self.address_pinyin = self.pinyin.get_pinyin(self.address, "")
		self.all_name = "latlng:all:{}_{}m".format(self.address_pinyin, self.distance_m)
		self.all_name_list = "latlng:all:list_{}_{}m".format(self.address_pinyin, self.distance_m)
		self.polyline_name = "latlng:polyline:{}_{}m".format(self.address_pinyin, self.distance_m)
		self.set_name = "latlng:set:{}_{}m".format(self.address_pinyin, self.distance_m)
		self.set_name_1 = "latlng:set:{}_1_{}m".format(self.address_pinyin, self.distance_m)
		self.addr_20 = 'latlng:addr20:{}_{}m'.format(self.address_pinyin, self.distance_m)

	def get_polygon_bounds(self, points):
		'''求外包矩形'''
		length = len(points)
		top = down = left = right = points[0]
		for i in range(1, length):
			if points[i].lng > top.lng:
				top = points[i]
			elif points[i].lng < down.lng:
				down = points[i]
			else:
				pass
			if points[i].lat > right.lat:
				right = points[i]
			elif points[i].lat < left.lat:
				left = points[i]
			else:
				pass
		top_left = Point(top.lng, left.lat)
		top_right = Point(top.lng, right.lat)
		down_right = Point(down.lng, right.lat)
		down_left = Point(down.lng, left.lat)
		return [top_left, top_right, down_right, down_left]

	def is_point_in_rect(self, point, polygon_bounds):
		'''判断点是否在外包矩形外'''
		top_left = polygon_bounds[0]
		top_right = polygon_bounds[1]
		down_right = polygon_bounds[2]
		down_left = polygon_bounds[3]
		return (down_left.lng <= point.lng <= top_right.lng and top_left.lat <= point.lat <= down_right.lat)

	def is_point_in_polygon(self, point, points):
		polygon_bounds = self.get_polygon_bounds(points)
		if not self.is_point_in_rect(point, polygon_bounds):
			return False
		length = len(points)
		point_start = points[0]
		flag = False
		for i in range(1, length):
			point_end = points[i]
			# 点与多边形顶点重合
			if (point.lng == point_start.lng and point.lat == point_start.lat) or (
					point.lng == point_end.lng and point.lat == point_end.lat):
				return True
			# 判断线段两端点是否在射线两侧
			if (point_end.lat < point.lat <= point_start.lat) or (
					point_end.lat >= point.lat > point_start.lat):
				# 线段上与射线 Y 坐标相同的点的 X 坐标
				if point_end.lat == point_start.lat:
					x = (point_start.lng + point_end.lng) / 2
				else:
					x = point_end.lng - (point_end.lat - point.lat) * (
							point_end.lng - point_start.lng) / (
								point_end.lat - point_start.lat)
				# 点在多边形的边上
				if x == point.lng:
					return True
				# 射线穿过多边形的边界
				if x > point.lng:
					flag = not flag
				else:
					pass
			else:
				pass
			point_start = point_end
		return flag

	def check_latlng(self, polyline: list, input_lng, input_lat):
		'''
		polyline 是多个坐标点，形如
		['116.732617,39.722676', '116.732617,39.722676', '116.732617,39.722676',
		'116.732617,39.722676', '116.732617,39.722676']
		'''
		points = []
		for line in polyline:
			if line:
				try:
					lng, lat = line.split(',')
					points.append(Point(float(lng), float(lat)))
				except ValueError:
					pass
		if points:
			flag = self.is_point_in_polygon(Point(float(input_lng), float(input_lat)), points)
			return flag

	def getGDLatLng(self, address):
		uri = self.url + 'keywords=' + quote(address) + '&key=' + self.gd_key + '&subdistrict=1' + '&extensions=all'
		# 访问链接后，api会回传给一个json格式的数据
		temp = urllib.request.urlopen(uri)
		temp = json.loads(temp.read())
		# polyline是坐标，name是区域的名字
		Data = temp["districts"][0]['polyline']
		name = temp["districts"][0]['name']
		# polyline数据是一整个纯文本数据，不同的地理块按照|分，块里面的地理信息按照；分，横纵坐标按照，分，因此要对文本进行三次处理
		Data_Div1 = Data.split('|')  # 对结果进行第一次切割，按照|符号
		len_Div1 = len(Data_Div1)  # 求得第一次切割长度
		num = 0
		len_Div2 = 0  # 求得第二次切割长度，也即整个数据的总长度
		while num < len_Div1:
			len_Div2 += len(Data_Div1[num].split(';'))
			num += 1
		num = 0
		num_base = 0
		output = np.zeros((len_Div2, 5)).astype(np.float)  # 循环2次，分割；与，
		while num < len_Div1:
			temp = Data_Div1[num].split(';')
			len_temp = len(temp)
			num_temp = 0
			while num_temp < len_temp:
				output[num_temp + num_base, :2] = np.array(temp[num_temp].split(','))  # 得到横纵坐标
				output[num_temp + num_base, 2] = num_temp + 1  # 得到横纵坐标的连接顺序
				output[num_temp + num_base, 3] = num + 1  # 得到块的序号
				num_temp += 1
			num_base += len_temp
			num += 1
		output = DataFrame(output, columns=['经度', '纬度', '连接顺序', '块', '名称'])
		output['名称'] = name
		return output

	def getGDSubName(self, address):
		'''获取搜索区域的名称，部分区域例如鼓楼重名太多，因此返回城市代码，将城市代码作为参数给上述函数'''
		uri = self.url + 'keywords=' + quote(address) + '&key=' + self.gd_key + '&subdistrict=1' + '&extensions=all'
		temp = urllib.request.urlopen(uri)
		temp = json.loads(temp.read())
		list0 = temp['districts'][0]['districts']
		num_Qu = 0
		output = []
		while num_Qu < len(list0):
			output.append(list0[num_Qu]['adcode'])
			num_Qu += 1
		return output

	def getGDCSV(self):
		'''获取csv文件'''
		num = 0
		ad = self.getGDSubName(self.address)  # 得到福州下属区域的城市代码
		add = self.getGDLatLng(self.address)  # 得到福州整个的边界数据
		while num < len(ad):
			add = pd.concat([add, self.getGDLatLng(ad[num].encode("utf-8"))])  # 得到福州下属的全部区域的边界数据
			num += 1
		add.to_csv('{0}.csv'.format(self.address), encoding='gbk')

	def getMaxAndMinLatLng(self):
		'''获取最小和最大经纬度'''
		maxLng, maxLat, minLng, minLat = 0, 0, 99999, 99999
		with open('{0}.csv'.format(self.address)) as f:
			for i in list(f)[1:]:
				info = i.split(',')
				lng, lat = float(info[1]), float(info[2])
				if maxLng < lng:
					maxLng = lng
				if maxLat < lat:
					maxLat = lat
				if minLng > lng:
					minLng = lng
				if minLat > lat:
					minLat = lat
		return minLng, minLat, maxLng, maxLat

	def getPolyline(self):
		'''获取范围经纬度'''
		polyline = []
		with open('{0}.csv'.format(self.address)) as f:
			for i in list(f)[1:]:
				info = i.split(',')
				lng, lat, number = float(info[1]), float(info[2]), int(float(info[3]))
				latlng = "{:x<6f},{:x<6f}".format(lng, lat)
				if number <= 1:
					logging.info("polyline: {}".format(polyline))
					if polyline:
						self.redis_conn.lpush(self.polyline_name, json.dumps(polyline))
						polyline.clear()
					polyline.append(latlng)
				else:
					polyline.append(latlng)
			self.redis_conn.lpush(self.polyline_name, json.dumps(polyline))

	def getAllLatLng(self):
		'''通过最大最小经纬度得到全部经纬度'''
		minLng, minLat, maxLng, maxLat = self.getMaxAndMinLatLng()
		lng, lat = minLng, minLat
		while True:
			if lat > maxLat:
				break
			else:
				lng = minLng
				while True:
					if lng > maxLng:
						lat += 0.008949 * self.n
						break
					new_latlng = "{:x<6f},{:x<6f}".format(lng, lat)
					self.redis_conn.lpush(self.all_name, new_latlng)
					self.redis_conn.lpush(self.all_name_list, new_latlng)
					logging.info('全部坐标: {}'.format(new_latlng))
					lng += 0.010493 * self.n

	def getLatLngList(self):
		'''判断经纬度是否在范围内'''
		logging.info("Start!")
		while True:
			latlng_str = self.redis_conn.lpop(self.all_name_list)
			if latlng_str:
				latlng = latlng_str.split(',')
				lat, lng = float(latlng[1]), float(latlng[0])
				logging.info('检测坐标: {} {}'.format(lat, lng))
				for i in self.redis_conn.lrange(self.polyline_name, 0, -1):
					polyline = json.loads(i)
					if self.check_latlng(polyline=polyline, input_lng=lng, input_lat=lat):
						LatLng = json.dumps({"lng": lng, "lat": lat})
						self.redis_conn.sadd(self.set_name, LatLng)
						logging.info('--区域内坐标: {}'.format(LatLng))
			else:
				break
		logging.info("Stop!")

	def begin_thread_getlatlng(self, number):
		threadList = []
		for _ in range(int(number)):
			th = Thread(target=self.getLatLngList)
			threadList.append(th)

		for th in threadList:
			th.start()
		for th in threadList:
			th.join()

	def handleLatLngToAddr(self):
		'''把经纬度生成 格式'''
		latlngList = []
		count = 1
		for i in self.redis_conn.smembers(self.set_name):
			data = json.loads(i)
			latlng = '{},{}'.format(data['lng'], data['lat'])
			if count == 20:
				latlngList.append(latlng)
				addr_latlng = json.dumps([self.address, '|'.join(latlngList)], ensure_ascii=False)
				self.redis_conn.lpush(self.addr_20, addr_latlng)
				print(len(latlngList))
				latlngList.clear()
				count = 1
			else:
				latlngList.append(latlng)
				count += 1
		addr_latlng = json.dumps([self.address, '|'.join(latlngList)], ensure_ascii=False)
		self.redis_conn.lpush(self.addr_20, addr_latlng)
		print(len(latlngList))
		latlngList.clear()


if __name__ == "__main__":
	# TODO  高德上申请的key
	key = '2e3402fcdb4f1d5b3e314193c8b0f4de'
	# TODO  搜素的城市名(全名)
	addr_name = '重庆市'
	n = 0.5
	h = Handle_LatLng(key=key, addr_name=addr_name, n=n)
	h.getGDCSV()
	h.getPolyline()
	h.getAllLatLng()
	h.begin_thread_getlatlng(500)
	h.handleLatLngToAddr()
