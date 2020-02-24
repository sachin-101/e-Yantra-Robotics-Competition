import serial
import time

import cv2
import numpy as np
import math

from aruco_utils import track_aruco,calculate_Robot_State,detect_aruco, mask_bot, mark_Aruco
from arena_utils import extract_region, get_coordinates, detect_origin, detect_coins
from node import Node, sort_nodes

# ranges of hsv values
purple_low = np.array([100,100,20])
purple_high = np.array([155,255,255])
black_low = np.array([0,0,0])
black_high = np.array([255,255,80])
red_1_low = np.array([160,190,100])
red_1_high = np.array([179,255,255])
red_2_low = np.array([0,190,100])
red_2_high = np.array([20,255,255])

def show_img(img, name):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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

def get_trajectory(img):
    shape = img.shape
    
    outer_black = extract_region(img,shape,black_low,black_high)        #binary mask with the arena
    arena = np.bitwise_and(outer_black,img)
    #show_img(arena, 'arena')
    
    # extract purple region
    purple = extract_region(arena,shape,purple_low,purple_high)     #binary mask of purple regions
    purple_region = np.bitwise_and(purple,img)     
    #show_img(purple, 'purple')

    # extract the highway by removing the purple region and aruco
    highway = np.bitwise_and(np.invert(purple),arena)   
    highway = mask_bot(highway)         
    highway = cv2.cvtColor(highway, cv2.COLOR_BGR2GRAY)     
    cords,img_with_nodes = get_coordinates(highway,img) 

    origin, _ = detect_origin(purple_region,img)
    #purple_region_filled = fill_purple()
    # detect coin cords
    red_cords = detect_coins(purple_region,[red_1_low,red_2_low],[red_1_high,red_2_high],"red")[0]
    #print('r_cords (x,y)', red_cords)
     
    detected_nodes = [Node(x, y) for (x, y) in cords]
    
    aruco_center = track_aruco(img)    
    #Appending the capital node(which is the aruco center) to the nodes list
    aruco_center_node = Node(aruco_center[0],aruco_center[1])
    detected_nodes.append(aruco_center_node)
    
    # MAY BE MAKE IT MORE READABLE
    for n in detected_nodes:
        n.calc_angle(origin, aruco_center)
    nodes = sort_nodes(detected_nodes, origin, aruco_center) # sorted nodes

    red_coin_node, red_index = get_nearest_node(nodes, red_cords)
    reset_node = nodes[red_index - 1]

    cv2.circle(img,red_cords,3,(255,0,0),-1)
    trajectory = [reset_node, red_coin_node, aruco_center_node]    
    
    # Write Red to CSV
    offset = 1
    supplies = {'Node Type': ['Medical Aid'],
                'Node Number': [red_index+offset]}
    # output = pd.DataFrame(supplies)
    # print(output.head())
    # print('-'*10)
    # output.to_csv('Run_SupplyBot.csv') 

    # # Decoration
    # for i, n in enumerate(nodes):
    #     cv2.circle(img,(n.x,n.y),3,(255,255,0),-1)
    #     cv2.putText(img, f'{i+1}', (int(n.x), int(n.y)), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
    return trajectory, origin, nodes, red_cords


def send_data(sender, data):
    #print('Send data:', data)
    output = sender.write(str.encode(str(data)))
    time.sleep(0.1)
    
    
def main():
    
    time.sleep(8)

    #serial communication
    port = "COM11"
    sender = serial.Serial(port,9600)
        
    cap = cv2.VideoCapture(0) # webcam, then 1
    fps = cap.get(cv2.CAP_PROP_FPS)
    # setting video counter to frame sequence
    cap.set(3, 640)
    cap.set(4, 480)
    #try:
    # get initial frame
    ret, frame = cap.read()
        
    trajectory, origin, nodes, red_cords = get_trajectory(frame)   
    path_checkpoint = 0
    n_target = trajectory[path_checkpoint]
    threshold = 8     # minimum angle 
    
    stopped, done = False, False
    stopped_frames, end_frames = 0, 0
    
    send_data(sender, data='c')  # c denotes start data
    print("Send data: c \t Bot starts moving")

    while (ret):          
        ret, frame = cap.read()          
        cv2.imshow("Raw Feed", frame)
        
        try:
            # Marking aruco 
            aruco_list = detect_aruco(frame)
            frame, aruco_centre = mark_Aruco(frame, aruco_list)
            state = calculate_Robot_State(frame, aruco_list)
        except:
            pass
        # marking red coin
        cv2.circle(frame,red_cords,7,(255,0,0),2)

        # marking nodes
        for i, n in enumerate(nodes):
            cv2.circle(frame,(n.x,n.y),3,(255,255,0),-1)
            cv2.putText(frame, f'{i+1}', (int(n.x), int(n.y)), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
        
        cv2.imshow("Processed", frame)
        cv2.waitKey(int(1000/fps))

        angle = calc_angle(origin, (n_target.x, n_target.y), aruco_centre)
        #print("Bot starts moving",angle)
        #print("Bot moves",angle)
        if angle < threshold and not done:
            if path_checkpoint == 0 :
                send_data(sender, data='r') # r denotes reset servo
                print("Send data: r \t Striking mechanism reset")
                path_checkpoint += 1
                n_target = trajectory[path_checkpoint] # update the target node
            elif path_checkpoint == 1:
                if not stopped:
                    send_data(sender, data='s') # s denotes stop
                    print("Send data: s \t Bot stops to strike")
                    stopped = True         
                else:
                    stopped_frames += 1

                # 40 seconds to hit the coin
                if stopped and stopped_frames == int(fps*40):
                    path_checkpoint += 1
                    n_target = trajectory[path_checkpoint] # update the target node
                    send_data(sender, data='c') # c denotes move
                    print("Send data: c \t Bot starts moving")
                    stopped = False
            elif path_checkpoint == 2:
                done = True
                send_data(sender, data='l') # l denotes long beep
                print("Send data: l \t Bot reached capital")
       
        if done:
            if end_frames >= int(fps*4):
                cap.release() # stop video capture
                cv2.destroyAllWindows()
                print("program finished")
                break
            else:
                end_frames += 1
                
if __name__ == "__main__":
    main()
