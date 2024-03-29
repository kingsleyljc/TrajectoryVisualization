import json
import urllib
import math
import os
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方


class Geocoding:
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address):
        """
        利用高德geocoding服务解析地址获取位置坐标
        :param address:需要解析的地址
        :return:
        """
        geocoding = {'s': 'rsv3',
                     'key': self.api_key,
                     'city': '全国',
                     'address': address}
        geocoding = urllib.urlencode(geocoding)
        ret = urllib.urlopen("%s?%s" % ("http://restapi.amap.com/v3/geocode/geo", geocoding))

        if ret.getcode() == 200:
            res = ret.read()
            json_obj = json.loads(res)
            if json_obj['status'] == '1' and int(json_obj['count']) >= 1:
                geocodes = json_obj['geocodes'][0]
                lng = float(geocodes.get('location').split(',')[0])
                lat = float(geocodes.get('location').split(',')[1])
                return [lng, lat]
            else:
                return None
        else:
            return None


def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import xml.dom.minidom
import json
import time

import pandas as pd
PORT_NUMBER = 8080


def do_osm(osm: str):
    doc = xml.dom.minidom.parse(curdir + sep + osm)
    collection = doc.documentElement
    nodes = collection.getElementsByTagName('node')
    content = []
    ids = []
    for i in nodes:
        lat = i.getAttribute('lat')
        lon = i.getAttribute('lon')
        the_id = i.getAttribute('id')
        lon,lat = wgs84_to_bd09(float(lon), float(lat))
        obj ={'value':[lon,lat],'name':the_id}
        content.append(obj)
    data = {'content': content}

    with open(curdir + sep + 'data/{}.json'.format(osm.split('.')[0]), 'w+') as f:
        json.dump(data, f)
    f.close()

def get_directory(dir:str,id:int):
    if not os.path.exists(dir):
        return -1
    files = os.listdir(dir)
    data = {'dir':files,'amount':len(files)}
    with open('./tmp_data/{}.json'.format(id), 'w+') as f:
        json.dump(data, f)
    f.close()

def get_points(dir:str,id:int,coor_type:int,amount:int,offset:int):
    '''
        coor_type：
         1 = 百度坐标系
         2 = wgs坐标系
         3 = gcj坐标系
    '''
    if not os.path.exists(dir):
        return -1
    coor_type = int(coor_type)
    df = pd.read_csv(dir, sep=',')
    points = []

    if amount == -1:
        amount = float('inf')

    off = 0
    cnt = 0
    for index, row in df.iterrows():
        if off<offset:
            off+=1
            continue
        if cnt>=amount:
            break
        alat = row['lat']
        alon = row['lon']
        if coor_type == 2:
            lon_lat = wgs84_to_bd09(alon, alat)
        elif coor_type == 3 :
            lon_lat = gcj02_to_bd09(alon, alat)
        elif coor_type == 1 :
            lon_lat = (alon, alat)
        obj ={'value':[lon_lat[0],lon_lat[1]],'name':cnt}
        # points.append([lon_lat[0],lon_lat[1]])
        points.append(obj)
        cnt += 1
    data = {'content':points,'amount':len(df)}
    with open('./tmp_data/{}.json'.format(id), 'w+') as f:
        json.dump(data, f)
    f.close()

def get_query(path:str):
    query = path.split('?')[1]
    query_arr = {}
    attrs = query.split('&')
    for attr in attrs:
        pair = attr.split('=')
        query_arr[pair[0]] = pair[1]
    return query_arr

def get_transform(lat,lon,from_type,to_type,id:int):
    '''
        coor_type：
         1 = 百度坐标系
         2 = wgs坐标系
         3 = gcj坐标系
    '''
    if from_type == to_type:
        result =[lon,lat]
    elif from_type == 1:
        if to_type == 2:
            result = bd09_to_wgs84(lon,lat)
        elif to_type == 3:
            result = bd09_to_gcj02(lon,lat)
    elif from_type == 2:
        if to_type == 1:
            result = wgs84_to_bd09(lon,lat)
        elif to_type == 3:
            result = wgs84_to_gcj02(lon,lat)
    elif from_type == 3:
        if to_type == 1:
            result = gcj02_to_bd09(lon,lat)
        elif to_type == 2:
            result = gcj02_to_wgs84(lon,lat)
    data = {'content':result}
    with open('./tmp_data/{}.json'.format(id), 'w+') as f:
        json.dump(data, f)
    f.close()


class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        self.path = '.{}'.format(self.path)
        sendReply = False
        time_now = time.time()
        if self.path.find('?') == -1:
            print('goal_path:',self.path)
            mimetype = 'application/json'
            if get_directory(self.path,time_now) != -1:
                sendReply = True
        else:
            goal_path = self.path.split('?')[0]
            query = get_query(self.path)
            # type = self.path.split('&')[0].split('=')[1]
            # amount = self.path.split('&')[1].split('=')[1]
            print(query)
            mimetype = 'application/json'
            if query['transform'] == 'true':
                get_transform(float(query['lat']),float(query['lon']),int(query['from_type']),int(query['to_type']),time_now)
                sendReply = True
            elif get_points(goal_path,time_now,int(query['type']),int(query['count']),int(query['offset'])) != -1:
                sendReply = True

        if sendReply:
            print('./tmp_data/{}.json'.format(time_now))
            f = open('./tmp_data/{}.json'.format(time_now))
            self.send_response(200)
            self.send_header('Content-type', mimetype)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control","no-cache")
            self.end_headers()
            self.wfile.write(bytes(f.read(), encoding='utf8'))
            f.close()
            os.remove('./tmp_data/{}.json'.format(time_now))
        else:
            self.send_response(404)
        return


try:
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print('Started httpserver on port ', PORT_NUMBER)
    server.serve_forever()
except KeyboardInterrupt:
    server.socket.close()
