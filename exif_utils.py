#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

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
    print(gpsinfo)
    print(type(gpsinfo[1]))
    if type(gpsinfo[1]) == bytes:
        gpsinfo[1] = gpsinfo[1].decode('utf-8')
    if type(gpsinfo[3]) == bytes:
        gpsinfo[3] = gpsinfo[3].decode('utf-8')

    ns = 1 if u'N' == gpsinfo[1] else -1
    ew = 1 if u'E' == gpsinfo[3] else -1

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
