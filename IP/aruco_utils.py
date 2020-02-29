import cv2
import numpy as np
import cv2.aruco as aruco
import math 

BOT_ARUCO = 25

def angle_calculate(pt1,pt2, trigger = 0):  # function which returns angle between two points in the range of 0-359
    angle_list_1 = list(range(359,0,-1))
    #angle_list_1 = angle_list_1[90:] + angle_list_1[:90]
    angle_list_2 = list(range(359,0,-1))
    angle_list_2 = angle_list_2[-90:] + angle_list_2[:-90]
    x=pt2[0]-pt1[0] # unpacking tuple
    y=pt2[1]-pt1[1]
    angle=int(math.degrees(math.atan2(y,x))) #takes 2 points nad give angle with respect to horizontal axis in range(-180,180)
    if trigger == 0:
        angle = angle_list_2[angle]
    else:
        angle = angle_list_1[angle]
    return int(angle)

def detect_aruco(img):  #returns the detected aruco list dictionary with id: corners
    aruco_list = {}
    dict_flag = cv2.aruco.DICT_7X7_250
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)   #creating aruco_dict with 5x5 bits with max 250 ids..so ids ranges from 0-249
    parameters = cv2.aruco.DetectorParameters_create()  #refer opencv page for clarification
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters = parameters)
    gray = cv2.aruco.drawDetectedMarkers(gray, corners,ids)
    if len(corners):    
        for k in range(len(corners)):
            temp_1 = corners[k]
            temp_1 = temp_1[0]
            temp_2 = ids[k]
            temp_2 = temp_2[0]
            aruco_list[temp_2] = temp_1
        return aruco_list

def mark_Aruco(img, aruco_list):    #function to mark the centre and display the id
    key_list = aruco_list.keys()
    font = cv2.FONT_HERSHEY_SIMPLEX
    for key in key_list:
        dict_entry = aruco_list[key]    #dict_entry is a numpy array with shape (4,2)
        centre = dict_entry[0] + dict_entry[1] + dict_entry[2] + dict_entry[3]#so being numpy array, addition is not list addition
        centre[:] = [int(x / 4) for x in centre]    #finding the centre
        orient_centre = centre + [0.0,5.0]
        centre = tuple(centre)  
        orient_centre = tuple((dict_entry[0]+dict_entry[1])/2)
        
        cv2.circle(img,centre,1,(0,0,255),8)
        cv2.circle(img,orient_centre,1,(0,0,255),8)
        # cv2.circle(img,tuple(dict_entry[0]),1,(0,0,255),8)
        # cv2.circle(img,tuple(dict_entry[1]),1,(0,255,0),8)
        # cv2.circle(img,tuple(dict_entry[2]),1,(255,0,0),8)
        
        # draw a green square around the aruco
        #cv2.polylines(img,[dict_entry],1,(0,255,0),2)
        cv2.line(img,centre,orient_centre,(255,0,0),4) #marking the centre of aruco
        cv2.putText(img, str(key), (int(centre[0] + 20), int(centre[1])), font, 1, (0,0,255), 2, cv2.LINE_AA) # displaying the idno
    return img


# def draw_aruco(img,aruco_list):
#     key_list = aruco_list.keys()
#     for key in key_list:
#         dict_entry = aruco_list[key]    #dict_entry is a numpy array with shape (4,2)
#         centre = dict_entry[0] + dict_entry[1] + dict_entry[2] + dict_entry[3]#so being numpy array, addition is not list addition
#         centre[:] = [int(x / 4) for x in centre]    #finding the centre
#         orient_centre = centre + [0.0,5.0]
#         centre = tuple(centre)  
#         orient_centre = tuple((dict_entry[0]+dict_entry[1])/2)
#         # cv2.circle(img,centre,1,(0,0,255),8)
#         # cv2.circle(img,orient_centre,1,(0,0,255),8)
#         # cv2.line(img,centre,orient_centre,(255,0,0),4) #marking the centre of aruco
#         return img, centre

def get_aruco_center(aruco_dict_entry):
    centre = aruco_dict_entry[0] + aruco_dict_entry[1] + aruco_dict_entry[2] + aruco_dict_entry[3]#so being numpy array, addition is not list addition
    centre[:] = [int(x / 4) for x in centre]    #finding the centre
    return tuple(centre)  


def calculate_Robot_State(img,aruco_list):  #gives the state of the bot (centre(x), centre(y), angle)
    robot_state = {}
    key_list = aruco_list.keys()
    font = cv2.FONT_HERSHEY_SIMPLEX

    for key in key_list:
        dict_entry = aruco_list[key]
        pt1 , pt2 = tuple(dict_entry[0]) , tuple(dict_entry[1])
        centre = dict_entry[0] + dict_entry[1] + dict_entry[2] + dict_entry[3]
        centre[:] = [int(x / 4) for x in centre]
        centre = tuple(centre)
        #print centre
        angle = angle_calculate(pt1, pt2)
        cv2.putText(img, str(angle), (int(centre[0] - 80), int(centre[1])), font, 1, (0,0,255), 2, cv2.LINE_AA)
        robot_state[key] = [key, int(centre[0]), int(centre[1]), angle]#HOWEVER IF YOU ARE SCALING IMAGE AND ALL...THEN BETTER INVERT X AND Y...COZ THEN ONLY THE RATIO BECOMES SAME
    #print (robot_state)
    return robot_state 


def mask_bot(highway):
    aruco_list = detect_aruco(highway)
    center = get_aruco_center(aruco_list[BOT_ARUCO]) 
    x, y = center
    c1 = (x + 50, y + 50)
    c2 = (x + 50, y - 50)
    c3 = (x - 50, y - 50)
    c4 = (x - 50, y + 50)
    corners = np.int32([c1, c2, c3, c4])
    cv2.fillPoly(highway,[corners],(0,0,0))
    
    return highway

### Code to mark the extra arucos

def detect_other_arucos(img):  #returns the detected aruco list dictionary with id: corners
    aruco_list = {}
    dict_flag = cv2.aruco.DICT_7X7_250
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    aruco_dict = cv2.aruco.Dictionary_get(dict_flag)   #creating aruco_dict with 7x7 bits with max 250 ids..so ids ranges from 0-249
    parameters = cv2.aruco.DetectorParameters_create()  #refer opencv page for clarification
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters = parameters)
    gray = cv2.aruco.drawDetectedMarkers(gray, corners,ids)
    if len(corners):    
        for k in range(len(corners)):
            temp_1 = corners[k]
            temp_1 = temp_1[0]
            temp_2 = ids[k]
            temp_2 = temp_2[0]
            aruco_list[temp_2] = temp_1
        return aruco_list

def mark_other_arucos(img, aruco_list):    #function to mark the centre and display the id
    key_list = aruco_list.keys()
    font = cv2.FONT_HERSHEY_SIMPLEX
    for key in key_list:
        dict_entry = aruco_list[key]    #dict_entry is a numpy array with shape (4,2)
        centre = dict_entry[0] + dict_entry[1] + dict_entry[2] + dict_entry[3]#so being numpy array, addition is not list addition
        centre[:] = [int(x / 4) for x in centre]    #finding the centre
        #print centre
        orient_centre = centre + [0.0,5.0]
        #print orient_centre
        centre = tuple(centre)  
        # orient_centre = tuple((dict_entry[0]+dict_entry[1])/2)
        # cv2.circle(img,orient_centre,1,(0,0,255),8) #marking orient center 
        #cv2.line(img,centre,orient_centre,(255,0,0),4) #marking the centre of aruco
        dict_entry = np.int32(dict_entry)
        cv2.polylines(img,[dict_entry],1,(0,255,0),2)
        cv2.putText(img, str(key), (int(centre[0] + 20), int(centre[1])), font, 0.5, (255,0,0), 2, cv2.LINE_AA) # displaying the idno
    return img

def draw_other_arucos(img):

    #sharpening the image using sharpening kernel 
    #kernel = np.array([[0,-1,-0], [-1,5,-1], [0,-1,0]])
    #img = cv2.filter2D(img, -1, kernel)

    #detection and drawing other arucos
    aruco_list = detect_other_arucos(img)
    img = mark_other_arucos(img,aruco_list)
    return img