# ********************************************* IMPORTING MODULES *********************************************
import numpy as np
import cv2
from matplotlib import pyplot as plt
import glob
# ********************************************* IMPORTING MODULES *********************************************


print("                     ####################################################################")
print("                     #                                                                  #")
print("                     #                                                                  #")
print("                     #               WELCOME TO STEREO DEPTH ESTIMATION                 #")
print("                     #         THE CODE IS OPTIMISED FOR KIITI ODOMETRY DATASET         #")
print("                     #                                                                  #")
print("                     #                                                                  #")
print("                     #                                                                  #")
print("                     ####################################################################")



left_img_file_path = input("Enter the left images folder path:\n")  
disparity_type = int(input("Enter the type of disparity, 1 for SBGM and 2 for BM:\n "))
disparity_value = int(input("Do you want to print the disparity value(Matrix)?, 1 for YES and 0 for NO:\n "))
image_show = int(input("Do you want to see anyone of the original stereo image?, 1 for YES and 0 for NO:\n "))



# ***************************************************** DATASET HANDLER *****************************************************

# getting the file path for my left image dataset
path_left = glob.glob(left_img_file_path+"/*.png") # LEFT IMAGES
# creating a list to store the file path consecutively 
lst_left = []
for file in path_left:
    lst_left.append(file)
# Sorting the images path according to the frame
lst_left.sort()
arr_left = np.array(lst_left)

# getting the file path for my right image dataset
right_img_file_path = left_img_file_path.replace("image_0", "image_1")
path_right = glob.glob(right_img_file_path+"/*.png") # RIGHT IMAGES
# creating a list to store the file path consecutively
lst_right = []
for file in path_right:
    lst_right.append(file)
# Sorting the images path according to the frame
lst_right.sort()
arr_right = np.array(lst_right)

# ***************************************************** DATASET HANDLER ENDS *****************************************************



# ***************************************************** PROJECTION MATRIX(calibration data) HANDLER *****************************************************

calibFile = open('/home/maaitrayo/Autonomous Vehicle/data_odometry_gray/dataset/sequences/00/calib.txt', 'r').readlines()

P_L_Vals = calibFile[0].split()

Projection_Mat_left = np.zeros((3,4))
for row in range(3):
    for column in range(4):
        Projection_Mat_left[row, column] = float(P_L_Vals[row*4 + column + 1])

P_R_Vals = calibFile[1].split()
Projection_Mat_right = np.zeros((3,4))
for row in range(3):
    for column in range(4):
        Projection_Mat_right[row, column] = float(P_R_Vals[row*4 + column + 1])

#print(Projection_Mat_left)
#print(Projection_Mat_right)

# ***************************************************** PROJECTION MATRIX(calibration data) HANDLER ENDS *****************************************************



# ***************************************************** DECOMPOSING PROJECTION MATRICES ***************************************************** 

k_left, r_left, t_left, _, _, _, _ = cv2.decomposeProjectionMatrix(Projection_Mat_left)
t_left = (t_left/t_left[3])[:3]
k_right, r_right, t_right, _, _, _, _ = cv2.decomposeProjectionMatrix(Projection_Mat_right)
t_right = (t_right/t_right[3])[:3]

# ***************************************************** DECOMPOSING PROJECTION MATRICES ENDS***************************************************** 

# ***************************************************** DEPTH FOR STEREO IMAGE PAIR HANDLER FUNCTION *****************************************************

def calculate_depth(disparity, k_left, t_left, t_right):

    base_line = t_right[0] - t_left[0]
    focal_length = k_left[0][0]

    disparity[disparity == 0.0] = 0.1
    disparity[disparity == -1.0] = 0.1

    depth_map = np.ones(disparity.shape)
    depth_map = focal_length * base_line / disparity
    #print(depth_map[0][0])
    cv2.imshow("Depth", depth_map)
    #plt.figure(figsize=(11,7))
    #plt.imshow(depth_map)

# ***************************************************** DEPTH FOR STEREO IMAGE PAIR HANDLER FUNCTION ENDS *****************************************************



# ***************************************************** DISPARITY FOR STEREO IMAGE PAIR HANDLER FUNCTIONS *****************************************************

#                                   ------------------------ Disparity type SBGM ------------------------
def calculate_disparity_SGBM(img_L_g, img_R_g):

    global disparity
    calc_disparity_SBGM = cv2.StereoSGBM_create(minDisparity = 0, 
                                            numDisparities = 96, 
                                            blockSize = 9, 
                                            P1 = 8 * 9 * 9,
                                            P2 = 32 * 9 * 9,
                                            disp12MaxDiff = 1, 
                                            preFilterCap = 63,
                                            uniquenessRatio = 10, 
                                            speckleWindowSize = 100, 
                                            speckleRange = 32)

    disparity = calc_disparity_SBGM.compute(img_L, img_R)

    if(disparity_value == 1):
        print("--------------------------Disparity value :-------------\n")
        print(disparity,"\n")
        print("--------------------------Disparity value ends:-------------\n")
    img_disparityA_SBGM = np.divide(disparity, 255.0)
    #cv2.imshow("disparity", img_disparityA_SBGM)
    #plt.imshow(img_disparityA_SBGM)
    #print(disparity[0][0])
    return(disparity)



#                                   ------------------------ Disparity type BM ------------------------
def calculate_disparity_BM(img_L_g, img_R_g):

    global disparity
    calc_disparity_BM = cv2.StereoBM_create(numDisparities = 96,
                                          blockSize = 9)

    disparity = calc_disparity_BM.compute(img_L_g, img_R_g)

    if(disparity_value == 1):
        print("--------------------------Disparity value :-------------\n")
        print(disparity,"\n")
        print("--------------------------Disparity value ends:-------------\n")
    img_disparityA_BM = np.divide(disparity, 255.0)
    #cv2.imshow("disparity", img_disparityA_BM)
    #plt.imshow(img_disparityA_BM)
    return(disparity)

# ***************************************************** DISPARITY FOR STEREO IMAGE PAIR HANDLER FUNCTIONS ENDS *****************************************************



for i in range(len(arr_right)):
#for i in range(1):
    img_L = cv2.imread(arr_left[i])
    img_R = cv2.imread(arr_right[i])

    # Converting to Grayscale/single channel
    img_L_g = cv2.cvtColor(img_L, cv2.COLOR_BGR2GRAY)
    img_R_g = cv2.cvtColor(img_R, cv2.COLOR_BGR2GRAY)

    if(image_show == 1):
        #Use any one of the image left or right
        cv2.imshow("Image Left", img_L_g)
    #cv2.imshow("Image Right", img_R_g)

    if(disparity_type == 1):
        calculate_disparity_SGBM(img_L_g, img_R_g)

    else:
        calculate_disparity_BM(img_L_g, img_R_g)

    calculate_depth(disparity, k_left, t_left, t_right)
    # ------- This portion is just to plot the original image, keep it commented out for smooth workflow of the algorithm -------
    '''plt.subplot(1,2,1)
    plt.title('LEFT IMAGE')
    plt.imshow(img_L_g)

    plt.subplot(1,2,2)
    plt.title('RIGHT IMAGE')
    plt.imshow(img_R_g)'''
    # ------- This portion is just to plot the original image, keep it commented out for smooth workflow of the algorithm -------


    plt.show()
    cv2.waitKey(30)

cv2.destroyAllWindows()

