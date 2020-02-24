import cv2
import numpy as np
import os
import math
import csv
import cv2.aruco as aruco
from aruco_utils import detect_aruco,draw_aruco,calculate_Robot_State
import copy


def wiener_filter(img, kernel, S):
    kernel /= np.sum(kernel) 
    f_img = np.fft.fft2(np.copy(img))
    kernel = np.fft.fft2(kernel, s = np.array(S.shape))
    x = (np.abs(kernel)**2)*S
    m,n = x.shape
    for i in range(m):
        for j in range(n):
            if int(x[i][j])==0:
                x[i][j] =1
    kernel = (np.conj(kernel)*S) / x
    f_img = f_img * kernel
    deblurred_img = np.abs(np.fft.ifft2(f_img))
    return deblurred_img

def calcPSF(filter_height, filter_width, length, theta):
	h = np.zeros((filter_height, filter_width))
	y, x = int(filter_height / 2), int(filter_width / 2)
	h = cv2.ellipse(h, (y, x), (0, int(length/2)), theta, 0, 360, 255, cv2.FILLED)    # Drawing ellipse
	sum_h = cv2.sumElems(h)[0]
	h = h #/ sum_h
	return h

def power_spectral_density(orig_img, beta):
    S_0 =  (np.absolute(np.fft.fftshift(np.fft.fft2(orig_img[...,0])))**2)/beta
    S_1 =  (np.absolute(np.fft.fftshift(np.fft.fft2(orig_img[...,1])))**2)/beta
    S_2 =  (np.absolute(np.fft.fftshift(np.fft.fft2(orig_img[...,2])))**2)/beta
    return S_0, S_1, S_2


def apply_kernel(img, kernel, S):
	new_img = np.zeros(img.shape)
	new_img[...,0] = wiener_filter(img[...,0], kernel, S[0])
	new_img[...,1] = wiener_filter(img[...,1], kernel, S[1])
	new_img[...,2] = wiener_filter(img[...,2], kernel, S[2])
	return new_img


def deblur(ip_image, len_psf, theta, beta, orig_img):
    id_list = []
    
    # Increase the contrast of image
    # alpha = 2 # contrast
    # beta = 10   # brightness
    # ip_image = cv2.convertScaleAbs(ip_image, alpha=alpha, beta=beta)

    # Calculate power spectral density
    S = power_spectral_density(orig_img, beta)
    
    # weiner kernel
    h_kernel = calcPSF(20, 20, len_psf, theta)
    filtered_img = apply_kernel(ip_image, h_kernel, S)

    # Restored filtered image
    norm_img = cv2.normalize(filtered_img, None, alpha=0, beta=255, 
                                norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # # post processing to remove ringing
    # processed_img = cv2.medianBlur(norm_img, 3)

    # # Increase contrast of filtered image
    # alpha = 2.5   # contrast
    # beta = 5   # brightness 
    # output_img = cv2.convertScaleAbs(processed_img, alpha=alpha, beta=beta)
    output_img = norm_img
    return output_img, h_kernel, S[0], filtered_img, norm_img

def callback(*arg):
    pass

def main():
    cap = cv2.VideoCapture("Videos/WIN_20200204_22_29_57_Pro.mp4")
    fps = cap.get(cv2.CAP_PROP_FPS)
    # setting video counter to frame sequence
    cap.set(3, 640)
    cap.set(4, 480)
 
    # add frame_init here (picture of the arena)
    # frame_init = cv2.imread("original_img.jpg") 
    ret,frame_init = cap.read() 
 
    # trackbars for hyperparams 
    cv2.namedWindow("Frame")
    cv2.createTrackbar("Len_PSF","Frame",2,40,callback)
    cv2.createTrackbar("Beta","Frame",1000, 10000,callback)

    theta = 0
    while(ret):
        ret,frame = cap.read()
        cv2.imshow("Frame",frame)
        
        len_psf = cv2.getTrackbarPos('Len_PSF','Frame')
        beta = cv2.getTrackbarPos('Beta','Frame')
        deblurred_img, kernel, S, filtered_img, norm_img = deblur(frame, len_psf, theta, beta, frame_init)

        # Marking aruco 
        try:
            aruco_list = detect_aruco(deblurred_img)
            # frame, aruco_centre = mark_Aruco(frame, aruco_list)
            state = calculate_Robot_State(deblurred_img, aruco_list)
            theta = state[0][3]
            print("Detected Aruco")
        except:
            pass

        cv2.imshow("S", S)
        cv2.imshow("h_kernel", kernel)
        cv2.imshow("filtered_img_1",filtered_img)
        # cv2.imshow("norm_img_2",norm_img)
        # cv2.imshow("processed_img_3",processed_img)
        cv2.imshow("deblurred_img_4",deblurred_img)
        
        cv2.waitKey(int(100/fps))
    cv2.destroyAllWindows()
    
    cap.release()
    cv2.destroyAllWindows()

main()