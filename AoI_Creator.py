import os
import shutil
from random import randrange

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import Fixation_Calculator


# We use this function to normalize our Positions in the Real World e.g. CM to be the exact same on Pixel Coordinates
# IMPORTANT: For this to work, our Original Picture must always be the same size, if we Focus on our Mirror
# it should be 200cm x 50cm

#import FixationCorrector

# Class Variables
distance_mirror_to_ground = 0
distance_user_to_mirror = 0
image_height_in_cm = 0
image_width_in_cm = 0
user_height = 0
user_width = 0
head_height = 0
head_width = 0
eye_height = 0
hands_height = 0
hands_width = 0
feet_height = 0
feet_width = 0
VP_Image = ""
Fixation_FileName = ""
VP_Index = 0
userInputDictionary = {}
middle_of_body_on_image = 0
Condition = ""
start_time = 0

# Reads all necessary data from a txt file about the User and the Environment
# Read from txt file and convert it to a dictionary
def readInUserSpecificData(user_specific_data):
    d = {}
    with open(user_specific_data) as f:
        for line in f:
            line = line.replace('\n','')   # Remove useless stuff
            if('#' in line or line is ''):                   # Only relevant lines should taken into account
                continue
            (key, val) = line.split(':')
            if(key == 'VP_Image' or key == 'Fixation_Filename' or key == 'Condition'):           # cant convert string to int so do it alone
                d[key] = val
                continue
            d[key] = float(val)
    return d, user_specific_data

# Sets the class variables needed for the calculation to the specific user data from the txt file
def updateUserVariables(userInputDictionary, input_file):

    global distance_mirror_to_ground, distance_user_to_mirror, image_height_in_cm, image_width_in_cm, user_width, \
        user_height, eye_height, head_height, head_width, hands_height, hands_width, VP_Image, middle_of_body_on_image, Fixation_FileName,\
        VP_Index, feet_height, feet_width, Condition, start_time

    for key in userInputDictionary:
        if(key == 'Distance_Mirror_Ground'):
            distance_mirror_to_ground = userInputDictionary.get(key)
        if(key == 'Distance_User_Mirror'):
            distance_user_to_mirror = userInputDictionary.get(key)
        if(key == 'Mirror_Height'):
            image_height_in_cm = userInputDictionary.get(key)
        if (key == 'Mirror_Width'):
            image_width_in_cm = userInputDictionary.get(key)
        if (key == 'User_Height'):
            user_height = userInputDictionary.get(key)
        if (key == 'User_Width'):
            user_width = userInputDictionary.get(key)
        if (key == 'Eye_Height'):
            # Since the Camera is slightly above the eye we need to add a small amount to the eye height to fit the
            # BoundingBox on the Eyes
            eye_height = userInputDictionary.get(key) + 2
        if (key == 'Head_Height'):
            head_height = userInputDictionary.get(key)
        if (key == 'Head_Width'):
            head_width = userInputDictionary.get(key)
        if (key == 'Hands_Height'):
            hands_height = userInputDictionary.get(key)
        if (key == 'Hands_Width'):
            hands_width = userInputDictionary.get(key)
        if (key == 'Feet_Width'):
            feet_width = userInputDictionary.get(key)
        if (key == 'Feet_Height'):
            feet_height = userInputDictionary.get(key)
        if (key == 'VP_Image'):
            VP_Image = userInputDictionary.get(key)
        if (key == 'Fixation_Filename'):
            Fixation_FileName = userInputDictionary.get(key)
        if (key == 'Condition'):
            Condition = userInputDictionary.get(key)
        if (key == 'Start_time'):
            start_time = userInputDictionary.get(key)
        if (key == 'VP_Index'):
            VP_Index = int(userInputDictionary.get(key))
            # Create Results dir and folder for every VP
            current_dir = os.getcwd()
            result_dir = os.path.join(current_dir, r'Results')
            if not os.path.exists(result_dir):
                os.makedirs(result_dir)
            vp_index = "VP" + str(VP_Index)
            vp_dir = os.path.join(result_dir, vp_index)
            if os.path.exists(vp_dir):
                random_num = str(randrange(0,10000))
                os.makedirs(vp_dir + "_duplicate_" + random_num)
                vp_dir = result_dir + "\\" + vp_index + "_duplicate_" + random_num
                print(vp_dir)
            else:
                os.makedirs(vp_dir)
            # Copy input txt file and move to results folder
            shutil.copy(input_file, vp_dir + "\\user_specific_data.txt")

        middle_of_body_on_image = int(image_height_in_cm / 2)
    return vp_dir

# calculate cm values to pixel values
def calculateCentimetersToPixels(value, isHeight):
    if(value is 0):
        return
    if(isHeight):
        height_in_pixel = imageHeight_in_pixels / image_height_in_cm * value    # Calculate centimeter in pixels for our value
        return height_in_pixel
    else:
        width_in_pixel = imageWidth_in_pixels / image_width_in_cm * value
        return width_in_pixel
def readInUserImage():
    # read in image
    im = mpimg.imread("Input\\" + VP_Image)
    #im = cv2.imread(VP_Image)
    flip = im[::-1,:,:]
    #plt.imshow(flip[:, :, :]), plt.title('flip vertical with inverted y-axis'), plt.gca().invert_yaxis(), plt.show()

    # get width and height of the picture
    imageWidth_in_pixels = im.shape[1]
    imageHeight_in_pixels = im.shape[0]
    print("Picture Width: " + str(imageWidth_in_pixels) + " Height: " + str(imageHeight_in_pixels))

    return imageHeight_in_pixels, imageWidth_in_pixels, flip

# TODO: Calculate where the eyes are on a given image and Calculate Points for Bounding Boxes from there
def createVisualBoundingBoxesOnImage(image, VP_Index, vp_dir, AoI_Heights_in_px, AoI_Widths_in_px):
    # Create plot for image
    figure, ax = plt.subplots(1)
    # We need to substract the distance of our mirror to the ground to determine where the user is
    user_height_px = calculateCentimetersToPixels(user_height - distance_mirror_to_ground, isHeight=True)
    user_width_px = calculateCentimetersToPixels(user_width, isHeight=False)

    print("User Width in Pixels: " + str(user_width_px))
    print("User Height in Pixels: " + str(user_height_px))
    print("Mirror Height " + str(image_height_in_cm))

    # Starting point should equal something like Middle of image (because person should stand there) - half the body width
    # But body width could be different


    # create Rectangles or for us called AoIs
    #
    #
    #                +------------------+
    #                |                  |
    #              height               |
    #                |                  |
    #               (xy)---- width -----+
    # 0 0 is bottom left width 0 is bottom right
    # 0 height is top left, width height is top right

    # For rectangles: First is the X position and second one is the Y Position where the rectangle starts.
    # Then comes the width of the rectangle and after that the height
    # For eyes it should be: around middle, eye position in pixels, width, height

    rectangles = [
        # Rectangle( bottom left point X, Top left point Y,
        #              width, height, color, filling, label)
        # calculated one
        patches.Rectangle((0.5 * imageWidth_in_pixels - 0.5 * AoI_Widths_in_px[0] - 10, AoI_Heights_in_px[0] + 34),
                          AoI_Widths_in_px[0], 55, edgecolor='r', facecolor="none", label="head"),

        # right hand
        patches.Rectangle((0.5 * imageWidth_in_pixels - 0.5 * user_width_px - 8, AoI_Heights_in_px[1] + 65),
                          AoI_Widths_in_px[1] - 5, 40, edgecolor='r', facecolor="none", label="right_hand"),

        # left hand
        patches.Rectangle((0.5 * imageWidth_in_pixels + 0.5 * user_width_px - 37, AoI_Heights_in_px[1] + 65),
                          AoI_Widths_in_px[1] - 5, 40, edgecolor='r', facecolor="none", label="left_hand"),

        # Feet
        patches.Rectangle((0.5 * imageWidth_in_pixels - 0.5 * AoI_Widths_in_px[2] - 24, AoI_Heights_in_px[2] + 40),
                          AoI_Widths_in_px[2] + 48, 50, edgecolor='r', facecolor="none", label="feet"),

        # Full Width
        # patches.Rectangle((0.15, 200), imageWidth_in_pixels, -50, edgecolor='r', facecolor="none", label="fullwidth"),

        # patches.Rectangle((0.1,200), imageWidth_in_pixels, 50, edgecolor='r', facecolor="none"),
        # patches.Rectangle((0.1,350), imageWidth_in_pixels, 50, edgecolor='r', facecolor="none"),
        # patches.Rectangle((0.1,600), imageWidth_in_pixels, 50, edgecolor='r', facecolor="none")

    ]
    boundingBoxes = []
    # Draw Rectangle on to the image
    # Add Boundingbox Position information for later usage
    #
    for rects in rectangles:
        ax.add_patch(rects)
        boundingBoxes.append([rects.get_label(), rects.get_bbox()])
        print("Name of created Area of Interest: " + rects.get_label())

    ax.imshow(image)

    # Format Axes to Max size (+1 so 400 is there because width is 399) not needed later on maybe
    ax.set_xlim(0, imageWidth_in_pixels + 1)
    ax.set_ylim(imageHeight_in_pixels, 0)
    plt.imshow(image[:, :, :]), plt.title('BoundingBoxes on Image'), plt.gca().invert_yaxis()
    print(os.path.join(vp_dir,
                             Condition + "_BoundingBoxes_VP" + str(VP_Index) + ".png"))
    plt.savefig(os.path.join(vp_dir,
                             Condition + "_BoundingBoxes_VP" + str(VP_Index) + ".png"))
    plt.show()

    image_with_bb = os.path.join(vp_dir, Condition + "_BoundingBoxes_VP" + str(VP_Index) + ".png")
    return boundingBoxes, image_with_bb, rectangles

def calculateHeightsForAreaOfInterestPositions(image_height, mirror_height, eye_height_in_px, eye_height, head_height, hands_height, feet_height):
    AoI_Positions = []
    # Calculate the scaling Factor. => 1CM in the real world equal x px on the Image
    scaling_factor = image_height / mirror_height
    # Calculate centimeter differences of the AoIs always from eyes
    diff_eye_head = eye_height - head_height
    diff_eye_hands = eye_height - hands_height
    diff_eye_feet = eye_height - feet_height
    # Calculate it based on px values and multiply it by 0.5 because of the Strahlensatz
    diff_eye_head_in_px = diff_eye_head * scaling_factor * 0.5
    diff_eye_hands_in_px = diff_eye_hands * scaling_factor * 0.5
    diff_eye_feet_in_px = diff_eye_feet * scaling_factor * 0.5
    # Subtract the px difference from the eyes to determine where the AoIs are
    head_height_px = eye_height_in_px - diff_eye_head_in_px
    hands_height_px = eye_height_in_px - diff_eye_hands_in_px
    feet_height_px = eye_height_in_px - diff_eye_feet_in_px
    print("Eye Height in Px: " + str(eye_height_in_px))
    AoI_Positions.extend([ head_height_px, hands_height_px, feet_height_px])

    return AoI_Positions
def calculateWidthsForAreaOfInterestPositions(image_width, mirror_width, head_width, hands_width,  feet_width):
    AoI_Width_Positions = []
    # Calculate scaling factor
    scaling_factor = image_width / mirror_width
    # Calculate width of the AoI all in Pxs
    head_width = head_width * scaling_factor
    hands_width = hands_width * scaling_factor
    feet_width = feet_width * scaling_factor
    # Add to array
    AoI_Width_Positions.extend([head_width, hands_width, feet_width])

    return AoI_Width_Positions
def normalizeBoundingBoxPositions(boundingBoxes):
    # Transform Pixel Information to normalized (0 to 1) for Fixation Detector
    for bb in boundingBoxes:
        bb[1].x0 = bb[1].x0 / imageWidth_in_pixels
        bb[1].x1 = bb[1].x1 / imageWidth_in_pixels
        bb[1].y0 = bb[1].y0 / imageHeight_in_pixels
        bb[1].y1 = bb[1].y1 / imageHeight_in_pixels

    return boundingBoxes
# read in user specific data and update variables with new data
userInputDictionary, input_file = readInUserSpecificData('Input\\User_Specific_Data_VP2.txt')
vp_result_dir = updateUserVariables(userInputDictionary, input_file)
imageHeight_in_pixels, imageWidth_in_pixels, image = readInUserImage()
eye_height_in_px = calculateCentimetersToPixels(eye_height - distance_mirror_to_ground, True)
AoI_Heights_in_px = calculateHeightsForAreaOfInterestPositions(imageHeight_in_pixels, image_height_in_cm, eye_height_in_px,
                                                               eye_height, head_height, hands_height, feet_height)
AoI_Widths_in_px = calculateWidthsForAreaOfInterestPositions(imageWidth_in_pixels, image_width_in_cm, head_width,
                                                             hands_width, feet_width)

boundingBoxes, image_with_bb, rectangles = createVisualBoundingBoxesOnImage(image, VP_Index, vp_result_dir, AoI_Heights_in_px, AoI_Widths_in_px)
normalizeBoundingBoxPositions(boundingBoxes)


# Call Fixation Detector with Bounding Boxes
Fixation_Calculator.startFixationCalculationOnBoundingBoxes(Fixation_FileName, boundingBoxes, VP_Image, image_with_bb, VP_Index, start_time)
