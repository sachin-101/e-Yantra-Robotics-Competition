import cv2
import numpy as np

from aruco_utils import detect_aruco

def filter_img(mask):
    #filtering the mask
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    dilate = cv2.dilate(opening,kernel,iterations = 1)  ###increase iterations for detection in low light 
    return dilate

def extract_region(img,shape,colour_low, colour_high):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    colour_mask = cv2.inRange(img_hsv,colour_low,colour_high)
    colour_mask = filter_img(colour_mask)
    contours, hierarchy = cv2.findContours(colour_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    colour_region = np.zeros(shape, dtype = np.uint8)
    cv2.drawContours(colour_region, contours, -1, (255,255,255), -1)
    cv2.destroyAllWindows()
    return colour_region


def detect_origin(purple_region,img):
    #origin detection
    img_gray = cv2.cvtColor(purple_region,cv2.COLOR_BGR2GRAY)
    ret,mask_origin = cv2.threshold(img_gray,180,255,cv2.THRESH_BINARY)
    mask_origin = filter_img(mask_origin)
    origin = min_area_contour(mask_origin,img,"white")
    x0 = origin[0][0]
    y0 = origin[0][1]
    return (x0, y0),img


def detect_coins(purple_region,low,high,colour):
    purple_region = cv2.cvtColor(purple_region,cv2.COLOR_BGR2HSV)
    final_mask = np.zeros_like(purple_region)[..., 0]
    colour_mask = cv2.inRange(purple_region, low, high)
    colour_mask = filter_img(colour_mask)
    coins = min_area_contour(colour_mask,purple_region,colour)
    return coins


def show_img(img, name):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def min_area_contour(mask,img,colour):
    cnt,hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area = []
    coins = []
    for i in range(len(cnt)):
        area.append(cv2.contourArea(cnt[i]))
    area_min = np.argmin(area)
    (x1,y1),rad1 = cv2.minEnclosingCircle(cnt[area_min])
    coin1 = (int(x1),int(y1))
    coins.append(coin1)
   
    if colour == "green":
        del area[area_min]
        del cnt[area_min]
        area_min_2 = np.argmin(area)
        (x2,y2),rad2 = cv2.minEnclosingCircle(cnt[area_min_2])
        coin2 = (int(x2),int(y2))
        coins.append(coin2)
    return coins
     
def get_coordinates(highway,img):
    #get the nodes in the ROI
    ret,th1 = cv2.threshold(highway,100,255,cv2.THRESH_BINARY)
    kernel1 = np.ones((3,3),np.uint8)
    kernel2 = np.ones((3,3),np.uint8)
    erosion = cv2.erode(th1,kernel1,iterations = 1)
    opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel2)
    contours_nodes, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    coordinates = []
    for i in range(len(contours_nodes)):
        (x,y),rad = cv2.minEnclosingCircle(contours_nodes[i])
        coordinates.append((int(x),int(y)))
    return coordinates,img




