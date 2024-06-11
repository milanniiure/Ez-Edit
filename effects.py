#effects.py

import cv2
import numpy as np
import getpass
import platform
import os
import calendar
import time
from skimage import color
from rembg import remove

def apply(path,effect_img,name="intermediate"):
   if path.count("jpg")>0 or path.count("jpeg")>0:
      cv2.imwrite(name+'.jpg',effect_img)
   elif path.count("png")>0:
      cv2.imwrite(name+'.png',effect_img)


def remove_background(path):  
    input_image = cv2.imread(path)
    input_image_rgb = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    result = remove(input_image_rgb)  # Remove background
    result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)  # Convert back to BGR format
    apply(path, result_bgr)
   
def photo_to_sketch(path):
    image = cv2.imread(path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_image = 255 - gray_image
    blurred = cv2.GaussianBlur(inverted_image, (21, 21), 0)
    inverted_blurred = 255 - blurred
    sketch = cv2.divide(gray_image, inverted_blurred, scale=256.0)
    adjusted_sketch = cv2.equalizeHist(sketch)
    apply(path, adjusted_sketch)


 
def photo_to_cartoon(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(image, 9, 75, 75)
    sharpened = cv2.addWeighted(color, 1.5, color, -0.5, 0)
    cartoon = cv2.medianBlur(sharpened, 7)
    cartoon_with_edges = cv2.bitwise_and(cartoon, cartoon, mask=edges)
    gamma = 1.2
    gamma_corrected = np.array(255 * (cartoon_with_edges / 255) ** gamma, dtype='uint8')
    apply(path, gamma_corrected)


def photo_to_oil_painting(path):
    image = cv2.imread(path)
    oil_painting = cv2.xphoto.oilPainting(image, 7, 1)
    apply(path, oil_painting)


def photo_to_sepia(path):
    image = cv2.imread(path)
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia_image = cv2.transform(image, kernel)
    sepia_image = np.clip(sepia_image, 0, 255)
    apply(path, sepia_image)                    
   

def unblur_to_blur(path):
    image = cv2.imread(path)
    blur_image = cv2.bilateralFilter(image, 60, 600, 600)
    apply(path,blur_image)


def photo_to_pixel(path):
    image = cv2.imread(path)
    pixel_size = 30  # Adjust the size of each pixel
    small_image = cv2.resize(image, (0, 0), fx=1/pixel_size, fy=1/pixel_size)
    pixelated_image = cv2.resize(small_image, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)    
    apply(path, pixelated_image)




def photo_to_vintage(path):
    image = cv2.imread(path)
    vintage_filter = np.array([[0.393, 0.769, 0.189],[0.349, 0.686, 0.168],[0.272, 0.534, 0.131]])
    vintage_image = cv2.transform(image, vintage_filter)
    vintage_image = np.clip(vintage_image, 0, 255).astype(np.uint8)
    apply(path, vintage_image)


def photo_to_warhol(path):
    image = cv2.imread(path)    
    b, g, r = cv2.split(image)
    b_inv = 255 - b
    g_inv = 255 - g
    r_inv = 255 - r
    pop_art_image = cv2.merge((b_inv, g_inv, r_inv))
    apply(path, pop_art_image)


def photo_to_hdr_effect(path):
    image = cv2.imread(path)
    image = image.astype(np.float32) / 255.0
    tonemap = cv2.createTonemapReinhard()
    hdr_image = tonemap.process(image)
    hdr_image = (hdr_image * 255).astype(np.uint8)
    apply(path, hdr_image)


def line_art(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    line_art = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    line_art = cv2.cvtColor(line_art, cv2.COLOR_GRAY2BGR)
    apply(path, line_art)



def crayon_drawing(path):
    image = cv2.imread(path)
    smooth = cv2.bilateralFilter(image, 9, 75, 75)
    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    sketch = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)
    crayon_drawing = cv2.bitwise_and(smooth, smooth, mask=sketch)
    apply(path, crayon_drawing)


def download(path):
    username = getpass.getuser()
    folder = ''
    gmt = time.gmtime()
    ts = calendar.timegm(gmt)
    ts=str(ts)
    if platform.system()=='Linux':
        folder += '/home/'+username+'/Downloads/'
    else:
        folder += 'C:\Downloads'
    image = cv2.imread(path)
    previous = os.getcwd()
    os.chdir(folder)
    if path.count('jpg')>0 or path.count('jpeg')>0 :
       outpath = "ezEdit_Effects_"+ts+".jpg"
       cv2.imwrite(outpath,image)                 
    elif path.count('png')>0:
       outpath = "ezEdit_Effects_"+ts+".png"
       cv2.imwrite(outpath,image)              
    os.chdir(previous)



