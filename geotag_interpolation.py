#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# THETAで撮影した写真に、iPhoneで撮影した写真についている位置情報から時間による線形補間をして
# 位置情報を付加する

from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime as dt
from sortedcontainers import SortedDict
from bisect import bisect_left
from glob import glob
import math
import piexif
import shutil
import os
import time

# exif取得
def get_exif_of_image(file):
    """Get EXIF of an image if exists.

    指定した画像のEXIFデータを取り出す関数
    @return exif_table Exif データを格納した辞書
    """
    im = Image.open(file)

    # Exif データを取得
    # 存在しなければそのまま終了 空の辞書を返す
    try:
        exif = im._getexif()
    except AttributeError:
        return {}

    # タグIDそのままでは人が読めないのでデコードして
    # テーブルに格納する
    exif_table = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        exif_table[tag] = value

    im.close()

    return exif_table

# exifの度分秒をfloatに変換
def arcTupleToFloat(arcTuple):
    return arcTuple[0][0] / arcTuple[0][1] + (arcTuple[1][0] / arcTuple[1][1]) / 60 + (arcTuple[2][0] / arcTuple[2][1]) / 3600

# floatから度分秒に変換
def floatToArcTuple(lat):
    deg = math.floor(lat)
    lat -= deg
    lat *= 60
    min = math.floor(lat)
    lat -= min
    lat *= 60 * 100
    sec = round(lat)
    return ((deg, 1), (min, 1), (sec, 100))

# exifの緯度経度をfloatの緯度経度に変換
def gpsTuplesToFloat(gpsinfo):
    ns = 1 if 'N' == gpsinfo[1] else -1
    ew = 1 if 'E' == gpsinfo[3] else -1
    return (ns * arcTupleToFloat(gpsinfo[2]), ew * arcTupleToFloat(gpsinfo[4]))

# floatの緯度経度からexifの緯度経度に変換
def floatLatLngToGpsTuple(latlng):
    (lat, lng) = latlng

    nsSign = b'N'
    if lat < 0:
        nsSign = b'S'
        lat = -lat

    ewSign = b'E'
    if lng < 0:
        ewSign = b'W'
        lng = -lng

    return {1: nsSign, 2:floatToArcTuple(lat), 3:ewSign, 4:floatToArcTuple(lng), 18: b'WGS-84'}

# 時間から緯度経度を引くdict
datetimeLatLng = SortedDict()

# iPhoneの写真ファイル一覧を取得
iphone_filenames = glob('2017*.jpg')

# iPhoneの写真ファイルを全部見て時間と緯度経度の対応をdatetimeLatLngに入れる
for filename in iphone_filenames:
    exif = get_exif_of_image(filename)
    # print(exif)
    if ('GPSInfo' in exif):
        # print(exif['DateTimeOriginal'])
        date = dt.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
        # print(date)
        gpsinfo = exif['GPSInfo']
        print(gpsinfo)
        (lat, lng) = gpsTuplesToFloat(gpsinfo)
        # print(lng)
        datetimeLatLng[date] = (lat,lng)

# THETAの写真ファイル一覧を取得
theta_filenames = glob('R*.jpg')

# THETAの写真ファイルに直近のiPhoneの写真ファイルの緯度経度から時間で内挿した緯度経度を入れる
for filename in theta_filenames:
    exif2 = get_exif_of_image(filename)

    dto = dt.strptime(exif2['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    bisectDto = datetimeLatLng.bisect(dto)
    #print(bisectDto)
    # print(type(dto))
    # print(type(keys[0]))
    item1 = datetimeLatLng.items()[max(bisectDto - 1, 0)]
    item2 = datetimeLatLng.items()[min(bisectDto, len(datetimeLatLng) - 1)]
    print(item1)
    print(item2)
    # print(dto)
    k = (dto - item1[0])/(item2[0] - item1[0])
    lat = item1[1][0] + k * (item2[1][0] - item1[1][0])
    lng = item1[1][1] + k * (item2[1][1] - item1[1][1])
    print((dto, (lat,lng)))

    exif_dict2 = piexif.load(filename)
    exif_dict2['GPS'] = floatLatLngToGpsTuple((lat, lng))

    shutil.copy2(filename, '_' + filename)
    piexif.insert(piexif.dump(exif_dict2), '_' + filename)
    os.utime('_' + filename, (time.mktime(dto.timetuple()),time.mktime(dto.timetuple())))
