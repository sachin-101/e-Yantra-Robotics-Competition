import serial
import time

import cv2
import numpy as np
import pandas as pd
import math

from aruco_utils import mask_bot, detect_aruco, mark_Aruco, calculate_Robot_State, get_aruco_center, draw_other_arucos
from arena_utils import extract_region, get_coordinates, detect_origin, detect_coins
from node import Node, sort_nodes
from deblurring import deblur

# # ranges of hsv values
# purple_low = np.array([100,100,20])
# purple_high = np.array([155,255,255])
# black_low = np.array([0,0,0])
# black_high = np.array([255,255,80])
# green_low = np.array([20,80,150])
# green_high = np.array([50,250,255])
# red_low = np.array([160,190,50])
# red_high = np.array([179,255,255])

# ranges of hsv values
purple_low = np.array([100,100,20])
purple_high = np.array([155,255,255])
black_low = np.array([0,0,0])
black_high = np.array([255,255,80])
green_low = np.array([20,80,150])
green_high = np.array([50,250,255])
red_low = np.array([160,10,100])
red_high = np.array([255,255,255])
BOT_ARUCO = 25
    
def calc_angle(origin,pt1,pt2):
    x0,y0 = origin
    x1,y1 = pt1
    x2,y2 = pt2
    a = ((y0-y1)**2 + (x0-x1)**2)**0.5                  
    b = ((y0-y2)**2 + (x0-x2)**2)**0.5
    c = ((y1-y2)**2 + (x1-x2)**2)**0.5
    num = a**2 + b**2 - c**2
    den = 2*a*b
    angle = math.acos(num/den)  # rads
    angle = (angle*180)/math.pi
    angle = round(angle, 2)
    return angle
    
def get_nearest_node(nodes, cords):
    distance = []
    for n in nodes:
        distance.append(((n.x-cords[0])**2 + (n.y-cords[1])**2))
    closest_node_idx = distance.index(min(distance))
    return nodes[closest_node_idx], closest_node_idx

def order_green_coins(origin, nodes, cur_node, g_cords):
    n_green1, g1_index = get_nearest_node(nodes, g_cords[0]) # Node
    n_green2, g2_index = get_nearest_node(nodes, g_cords[1])
    
    angle1 = calc_angle(origin, (cur_node.x, cur_node.y), (n_green1.x, n_green1.y))
    angle2 = calc_angle(origin, (cur_node.x, cur_node.y), (n_green2.x, n_green2.y))
    
    # mag_angle1 = calc_angle(origin, (cur_node.x, cur_node.y), (n_green1.x, n_green1.y))
    # mag_angle2 = calc_angle(origin, (cur_node.x, cur_node.y), (n_green2.x, n_green2.y))
    
    # Effective angle = 360 - |angle| if below line else |angle|
    
    # below_1 = n_green1.below_line(origin, aruco_center)
    # below_2 = n_green2.below_line(origin, aruco_center)

    # angle1 = 360 - mag_angle1 if below_1 else mag_angle1
    # angle2 = 360 - mag_angle2 if below_2 else mag_angle2

    # if angle1 < angle2:
    #     return (n_green2, g2_index), (n_green1, g1_index)
    # else:
    #     return (n_green1, g1_index), (n_green2, g2_index)

    if angle1 < angle2:
        return (n_green2, g2_index), (n_green1, g1_index)
    else:
        return (n_green1, g1_index), (n_green2, g2_index)

def show_img(img, name):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
   

def get_trajectory(img):
    shape = img.shape
    
    outer_black = extract_region(img,shape,black_low,black_high)        #binary mask with the arena
    arena = np.bitwise_and(outer_black,img)
    #show_img(arena, 'arena')

    # extract purple region
    purple = extract_region(arena,shape,purple_low,purple_high)     #binary mask of purple regions
    purple_region = np.bitwise_and(purple,img)                  
    #show_img(purple_region, 'purple_region')

    # extract the highway by removing the purple region and aruco
    highway = np.bitwise_and(np.invert(purple),arena)   
    highway = mask_bot(highway)         
    highway = cv2.cvtColor(highway, cv2.COLOR_BGR2GRAY)     
    cords,img_with_nodes = get_coordinates(highway,img) 

    origin, _ = detect_origin(purple_region,img)

    # detect coin cords
    red_cords = detect_coins(purple_region,red_low,red_high,"red")[0]
    green_cords = detect_coins(purple_region,green_low,green_high,"green")

    detected_nodes = [Node(x, y) for (x, y) in cords]
    
    # track aruco
    aruco_list = detect_aruco(img)
    aruco_center = get_aruco_center(aruco_list[BOT_ARUCO]) 
    
    # Appending the capital node(which is the aruco center) to the nodes list
    aruco_center_node = Node(aruco_center[0],aruco_center[1])
    detected_nodes.append(aruco_center_node)

    for n in detected_nodes:
        n.calc_angle(origin, aruco_center)
    nodes = sort_nodes(detected_nodes, origin, aruco_center) # sorted nodes

    red_coin_node, red_index = get_nearest_node(nodes, red_cords)

    # order green coins # cur node is red_coin_node cause angle will be measured as per that
    g_coin1, g_coin2 = order_green_coins(origin, nodes, cur_node=red_coin_node, g_cords=green_cords)
    cv2.circle(img,red_cords,3,(255,0,0),-1)
    n_green1, g1_index = g_coin1
    n_green2, g2_index = g_coin2
    
    trajectory = [red_coin_node, n_green1, n_green2, aruco_center_node]    
    
    # Write Red to CSV
    offset = 1
    supplies = {'Node no.': [red_index+offset, g1_index+offset, g2_index+offset],
                'Type of Relief Aid': ['Medical Aid', 'Food Supply', 'Food Supply']}
    output = pd.DataFrame(supplies)#, columns=['Node no.', 'Type of Relief Aid'])
    print(output.head())
    output.to_csv('Run_SupplyBot.csv') 

    return trajectory, origin, nodes

def send_data(sender, data):
    #print('Send data:', data)
    output = sender.write(str.encode(str(data)))
    # time.sleep(0.2)
    

def main():
    
    port = "COM11"
    sender = serial.Serial(port,9600)
    
    #threshold values 
    coin_threshold = 6
    reset_threshold = 20

    # deblurring params
    len_psf = 4
    beta = 6000
    d = 4
    sigmaColor = 30
    sigmaSpace = 30
    
    stopped, reset, done = False, False, False
    stopped_frames, end_frames = 0, 0

    cap = cv2.VideoCapture(0) # webcam, then 1
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # setting video counter to frame sequence
    cap.set(3, 640)
    cap.set(4, 480)
    
    #serial communication
    print("Waiting for 5 seconds to start the bot")
    time.sleep(5)

    
    # get initial frame
    ret, frame = cap.read()  
    frame_init = frame

    trajectory, origin, nodes = get_trajectory(frame)
    path_checkpoint = 0
    n_target = trajectory[path_checkpoint]

    send_data(sender, data='m')  # c denotes start data
    print("Send data: m \t Bot starts moving")

    aruco_list = detect_aruco(frame)
    aruco_center = get_aruco_center(aruco_list[BOT_ARUCO])

    while (ret):
        ret, frame = cap.read()     
        cv2.imshow('raw_feed', frame)
    
        try:
            # Detecting aruco 
            aruco_list = detect_aruco(frame)
            #########################################
            # DEBLURRING
            # if aruco_list is None:
            #     deblurring = True
            #     frame, kernel, S, filtered_img, norm_img = deblur(frame, len_psf, theta, beta, d, sigmaColor, sigmaSpace, frame_init)
            #     aruco_list = detect_aruco(frame)
            #     if aruco_list is not None:
            #         print("Deblurred and detected aruco")

            aruco_center = get_aruco_center(aruco_list[BOT_ARUCO]) 
            frame = mark_Aruco(frame, aruco_list)
            # state = calculate_Robot_State(frame, aruco_list)
            #other_arucos = draw_other_arucos(frame)
            #cv2.imshow("other_arucos",other_arucos)
            #theta = -state[25][3] + 90
                
        except Exception as e:
            #print("Error", e)
            #print("Could not detected even after deblurring")
            pass
        # marking nodes
        for i, n in enumerate(nodes):
            cv2.circle(frame,(n.x,n.y),3,(255,255,0),-1)
            cv2.putText(frame, f'{i+1}', (int(n.x), int(n.y)), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)

        
        img_with_arucos = draw_other_arucos(frame)
        cv2.imshow("Processed", frame)
        cv2.waitKey(int(1000/fps))

        angle = calc_angle(origin, (n_target.x, n_target.y), aruco_center)
        #print("Bot starts moving",angle)
        
        if not done:
            if angle < coin_threshold:
                if not stopped:
                    send_data(sender, data='s') # s denotes stop
                    print("Send data: s \t Bot stops")        
                    stopped = True      
                else:
                    stopped_frames += 1
                
                # 4 seconds to hit the coin
                if stopped: 
                    if stopped_frames == int(fps*1):  # Beep the buzzer twice
                        for _ in range(2):  # Beep buzzer twice
                            send_data(sender, data='b')
                            time.sleep(0.5)
                    elif stopped_frames == int(fps*2): # hit the coin
                        send_data(sender, data='h')
                        print("Send data: h \t Hit the coin")
                    elif stopped_frames == int(fps*4):
                        path_checkpoint += 1
                        if path_checkpoint == 3:
                            done = True
                            send_data(sender, data='l') # l denotes long beep
                            print("Send data: l \t Long Beep")
                        else:
                            send_data(sender, data='b') # l denotes long beep
                            time.sleep(0.5)
                            n_target = trajectory[path_checkpoint] # update the target node
                            send_data(sender, data='m') # c denotes move
                            print('-'*10, '\n', "Send data: m \t Bot starts moving")
                            stopped = False
                            stopped_frames = 0
                    
        else:  # To stop the feed from closing after reaching capital
            if end_frames >= int(fps*3):
                cap.release() # stop video capture
                cv2.destroyAllWindows()
                print("program finished")
                break
            else:
                end_frames += 1

if __name__ == "__main__":
    main()
