import cv2
import numpy as np
import cv2.aruco as aruco

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
        orient_centre = tuple((dict_entry[0]+dict_entry[1])/2)
        cv2.circle(img,orient_centre,1,(0,0,255),8) #marking orient center 
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

# Testing
# img = cv2.imread("detect_red_hsv.png")
# img_with_arucos = draw_other_arucos(img)
# cv2.imshow("img",img_with_arucos)
# cv2.waitKey(0)