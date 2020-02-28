import cv2
import numpy as np
import os
import time
import math
import csv
import cv2.aruco as aruco
from aruco_utils import detect_aruco, calculate_Robot_State
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


def apply_kernel(img, kernel, S):
	new_img = np.zeros(img.shape)
	new_img[...,0] = wiener_filter(img[...,0], kernel, S)
	new_img[...,1] = wiener_filter(img[...,1], kernel, S)
	new_img[...,2] = wiener_filter(img[...,2], kernel, S)
	return new_img


def deblur(ip_image, len_psf, theta, beta, d, sigmaColor, sigmaSpace, orig_img):
    id_list = []
    
    # Increase the contrast of image
    # alpha = 2 # contrast
    # beta = 10   # brightness
    # ip_image = cv2.convertScaleAbs(ip_image, alpha=alpha, beta=beta)

    # Calculate power spectral density
    S = (np.absolute(np.fft.fftshift(np.fft.fft2(orig_img[...,0])))**2)/beta
    
    # weiner kernel
    h_kernel = calcPSF(20, 20, len_psf, theta)
    filtered_img = apply_kernel(ip_image, h_kernel, S)

    # Restored filtered image
    norm_img = cv2.normalize(filtered_img, None, alpha=0, beta=255, 
                                norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # # post processing to remove ringing
    # processed_img = cv2.medianBlur(norm_img, 3)
    norm_img = cv2.bilateralFilter(norm_img,d,sigmaColor,sigmaSpace)
    
    # # Increase contrast of filtered image
    alpha = 3   # contrast
    beta = 5   # brightness 
    output_img = cv2.convertScaleAbs(norm_img, alpha=alpha, beta=beta)
    # output_img = norm_img
    return output_img, h_kernel, S, filtered_img, norm_img

# def draw_ellipse(theta):
# 	h = np.zeros((400, 400))
# 	y, x = 200, 200
# 	h = cv2.ellipse(h, (y, x), (50, 200), theta, 0, 360, 255, cv2.FILLED)    # Drawing ellipse
# 	return h


# def callback(*arg):
#     pass


# def aruco_using_deblur(frame):
    
#     # frame_init = frame
#     # # trackbars for hyperparams 
#     # cv2.namedWindow("Frame")
#     # cv2.createTrackbar("Len_PSF","Frame",5,40,callback)
#     # cv2.createTrackbar("Beta","Frame",6000, 10000,callback)
#     # cv2.createTrackbar("d","Frame",4,20,callback)
#     # cv2.createTrackbar("sigmaColor","Frame",30,100,callback)
#     # cv2.createTrackbar("sigmaSpace","Frame",30, 100,callback)

#     # det_normal, det_deblur, nd = 0, 0, 0
#     # theta = 0
#     #ellipse = draw_ellipse(theta)
#     # deblurred_img = None
        
#     # Try finding aruco on normal image
#     # Else deblur then try again
#     aruco_list = detect_aruco(frame)            
#     if aruco_list is None:
#         try:
#             # len_psf = cv2.getTrackbarPos('Len_PSF','Frame')
#             # beta = cv2.getTrackbarPos('Beta','Frame')
#             # d = cv2.getTrackbarPos('d','Frame')
#             # sigmaColor = cv2.getTrackbarPos('sigmaColor','Frame')
#             # sigmaSpace = cv2.getTrackbarPos('sigmaSpace','Frame')
    
#             deblurred_img, kernel, S, filtered_img, norm_img = deblur(frame, len_psf, theta, beta, d, sigmaColor, sigmaSpace, frame_init)
#             aruco_list = detect_aruco(deblurred_img)
#             # frame, aruco_centre = mark_Aruco(frame, aruco_list)
#             state = calculate_Robot_State(deblurred_img, aruco_list)
#             # 1. The bot is moving anti-clockwise while ellipse moves clockwise hence negative
#             # 2. +90, cause deblurring is PERPENDICULAR to direction of ellipse
#             theta = -state[25][3] + 90
#             #ellipse = draw_ellipse(theta)
#             print(f"\t\t\tDetected Blurred Aruco\t theta:{theta}")
#             det_deblur += 1
#             aruco_center = track_aruco(deblurred_img)
#             return aruco_center
#         except:
#             print("ND")
#             return None 
#             nd += 1
#     else:
#         state = calculate_Robot_State(frame, aruco_list)
#         theta = -state[25][3] + 90
#         #ellipse = draw_ellipse(theta)
#         det_normal += 1
#         aruco_center = track_aruco(frame)
#         return aruco_center