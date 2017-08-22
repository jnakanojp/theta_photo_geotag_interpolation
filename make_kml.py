#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# 写真ファイル群からKMLを作成する

import sys
from glob import glob
import piexif
import exif_utils

import simplekml

kml = simplekml.Kml()

iphone_filenames = glob('2017*.jpg')

for filename in iphone_filenames:
    exif_dict = piexif.load(filename)
    (lat, lng) = exif_utils.gpsTuplesToFloat(exif_dict['GPS'])
    heading = exif_dict['GPS'][piexif.GPSIFD.GPSImgDirection][0] / exif_dict['GPS'][piexif.GPSIFD.GPSImgDirection][1]

    # kml.newpoint(name=filename, coords=[(lng, lat)])
    photo = kml.newphotooverlay(name=filename)
    photo.camera = simplekml.Camera(longitude=lng, latitude=lat, heading=heading, tilt=90, altitude=1.2, altitudemode=simplekml.AltitudeMode.relativetoground)
    photo.point.coords = [(lng, lat)]
    photo.icon.href = filename
    photo.viewvolume = simplekml.ViewVolume(-30,30,-18,18,10)

theta_filenames = glob('_R*.jpg')

for filename in theta_filenames:
    exif_dict = piexif.load(filename)
    (lat, lng) = exif_utils.gpsTuplesToFloat(exif_dict['GPS'])

    # kml.newpoint(name=filename, coords=[(lng, lat)])
    photo = kml.newphotooverlay(name=filename)
    photo.camera = simplekml.Camera(longitude=lng, latitude=lat, tilt=90, altitude=1.5, altitudemode=simplekml.AltitudeMode.relativetoground)
    photo.point.coords = [(lng, lat)]
    photo.icon.href = filename
    photo.shape = simplekml.Shape.sphere
    photo.viewvolume = simplekml.ViewVolume(-180, 180, -90, 90, 20)

kml.save('test.kml')
