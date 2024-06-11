#compression.py

import cv2
import numpy as np
import getpass
import platform
import os
import calendar
import time


# Compression levels for JPEG images
jpg = {
    'low': 25,     # Lowest quality, highest compression
    'medium': 50,  # Moderate quality, moderate compression
    'high': 75     # Highest quality, lowest compression
}

# Compression levels for PNG images
png = {
    'low': 0,     # Highest compression, smallest file size
    'medium': 5,  # Moderate compression
    'high': 9     # Lowest compression, highest quality
}


def save(path, image, jpg_quality=None, png_compression=None):
  if jpg_quality:
    cv2.imwrite(path, image, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])
  elif png_compression:
    cv2.imwrite(path, image, [int(cv2.IMWRITE_PNG_COMPRESSION), png_compression])         
  else:
    cv2.imwrite(path, image)

def compression(path, typ):
    username = getpass.getuser()
    folder = ''
    gmt = time.gmtime()
    ts = calendar.timegm(gmt)
    ts = str(ts)
    if platform.system() == 'Linux':
        folder += '/home/' + username + '/Downloads/'
    else:
        folder += 'C:\Downloads'
    image = cv2.imread(path)
    previous = os.getcwd()
    os.chdir(folder)
    try:
        if path.lower().endswith(('jpg', 'jpeg')) and typ in jpg:
            outpath = "ezEdit_compressed_" + ts + ".jpg"
            save(outpath, image, jpg_quality=jpg[typ])
        elif path.lower().endswith('png') and typ in png:
            outpath = "ezEdit_compressed_" + ts + ".png"
            save(outpath, image, png_compression=png[typ])
        else:
            raise ValueError("Unsupported image format or compression type")
    except ValueError as e:
        print(e)
    finally:
        os.chdir(previous)