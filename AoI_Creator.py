import os
import shutil
from random import randrange
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import Fixation_Calculator

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
vp_image = ""
fixation_filename = ""
vp_Index = 0
user_input_dictionary = {}
middle_of_body_on_image = 0
condition = ""
start_time = 0
scaling_factor_height = 0
scale_f_w = 0


# Reads all necessary data from a txt file about the User and the Environment
# Read from txt file and convert it to a dictionary
def read_in_user_specific_data(user_specific_data):
    d = {}
    with open(user_specific_data) as f:
        for line in f:
            line = line.replace('\n', '')
            if ('#' in line or line is ''):  # Only relevant lines should taken into account
                continue
            (key, val) = line.split(':')
            if (key == 'VP_Image' or key == 'Fixation_Filename' or key == 'Condition'):  # convert strings
                d[key] = val
                continue
            d[key] = float(val)
    return d, user_specific_data


# Sets the class variables needed for the calculation to the specific user data from the txt file
def update_user_variable(userInputDictionary):
    global distance_mirror_to_ground, distance_user_to_mirror, image_height_in_cm, image_width_in_cm, user_width, \
        user_height, eye_height, head_height, head_width, hands_height, hands_width, vp_image, middle_of_body_on_image, fixation_filename, \
        vp_Index, feet_height, feet_width, condition, start_time

    for key in userInputDictionary:
        if (key == 'Distance_Mirror_Ground'):
            distance_mirror_to_ground = userInputDictionary.get(key)
        if (key == 'Distance_User_Mirror'):
            distance_user_to_mirror = userInputDictionary.get(key)
        if (key == 'Mirror_Height'):
            image_height_in_cm = userInputDictionary.get(key)
            middle_of_body_on_image = int(image_height_in_cm / 2)
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
            vp_image = userInputDictionary.get(key)
        if (key == 'Fixation_Filename'):
            fixation_filename = userInputDictionary.get(key)
        if (key == 'Condition'):
            condition = userInputDictionary.get(key)
        if (key == 'Start_time'):
            start_time = userInputDictionary.get(key)
        if (key == 'VP_Index'):
            vp_Index = int(userInputDictionary.get(key))


# Create Results dir and folder for every VP
def create_results_folder(vp_index, input_file):
    result_dir = os.path.join(os.getcwd(), r'Results')
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    vp_index = "VP" + str(vp_index)
    vp_dir = os.path.join(result_dir, vp_index)
    if os.path.exists(vp_dir):  # quick fix to prevent overwriting existings folders
        random_num = str(randrange(0, 100000))
        os.makedirs(vp_dir + "_duplicate_" + random_num)
        vp_dir = result_dir + "\\" + vp_index + "_duplicate_" + random_num
    else:
        os.makedirs(vp_dir)
    # Copy input txt file and move to results folder
    shutil.copy(input_file, vp_dir)
    return vp_dir


# transform the measured centimeter values to pixel values on our reference image
def transform_centimeters_to_pixels(value, isHeight):
    if (value is 0):
        return
    if (isHeight):
        height_in_pixel = imageHeight_in_pixels / image_height_in_cm * value
        print(imageHeight_in_pixels / image_height_in_cm)
        return height_in_pixel
    else:
        width_in_pixel = imageWidth_in_pixels / image_width_in_cm * value
        return width_in_pixel


def read_in_user_image():
    # read in image
    img = mpimg.imread("Input\\" + vp_image)
    flip = img[::-1, :, :]  # flip image as it makes later calculations easier
    # get width and height of the picture
    imageWidth_in_pixels = img.shape[1]
    imageHeight_in_pixels = img.shape[0]
    print("Picture Width: " + str(imageWidth_in_pixels) + " Height: " + str(imageHeight_in_pixels))

    return imageHeight_in_pixels, imageWidth_in_pixels, img  # flip


# Visualize bounding boxes on the reference image
def create_visual_bounding_boxes_on_image(image, VP_Index, vp_dir, AoI_Heights_in_px, AoI_Widths_in_px):
    # create Rectangles or for us called AoIs
    #
    #
    #                +------------------+
    #                |                  |
    #              height               |
    #                |                  |
    #               (xy)---- width -----+
    # Rectangles = (xy, width, height)
    rectangles = [
        # Rectangle( bottom left point X, Top left point Y,
        #              width, height, color, filling, label)
        # head
        patches.Rectangle((0.5 * imageWidth_in_pixels - (AoI_Widths_in_px[0] * 0.5), AoI_Heights_in_px[0]),
                          AoI_Widths_in_px[0], 22 * 7.37 * 0.5, edgecolor='r', facecolor="none", label="head"),

        # right hand
        patches.Rectangle((0.5 * imageWidth_in_pixels - ((AoI_Widths_in_px[3] + 30) * 0.5), AoI_Heights_in_px[1]),
                          AoI_Widths_in_px[1], 17 * 7.37 * 0.5, edgecolor='r', facecolor="none", label="right_hand"),

        # left hand
        patches.Rectangle((0.5 * imageWidth_in_pixels + ((AoI_Widths_in_px[3] - 30) * 0.5), AoI_Heights_in_px[1]),
                          AoI_Widths_in_px[1], 17 * 7.37 * 0.5, edgecolor='r', facecolor="none", label="left_hand"),

        # Feet
        patches.Rectangle((0.5 * (imageWidth_in_pixels - AoI_Widths_in_px[2]), AoI_Heights_in_px[2]),
                          AoI_Widths_in_px[2], 22 * 7.37 * 0.5, edgecolor='r', facecolor="none", label="feet"),

        # Test
        #patches.Rectangle((0.5 * imageWidth_in_pixels + 50, AoI_Heights_in_px[0]),
                          #AoI_Widths_in_px[2], 22 * scaling_factor_height * 0.5, edgecolor='g', facecolor="none",
                          #label="x")
    ]
    figure, ax = plt.subplots(1)
    boundingBoxes = []
    image = image[::-1, :, :]  # flip image for better processing

    # Draw Rectangle on to the image
    # Add Boundingbox information to boundingbox array for later usage
    for rects in rectangles:
        ax.add_patch(rects)
        boundingBoxes.append([rects.get_label(), rects.get_bbox()])
        print("Name of created Area of Interest: " + rects.get_label())
        print('{0} height px: {1} and width: {2}'.format(rects.get_label(), rects.get_height(), rects.get_width()))
    # Customize plot
    plt.imshow(image), plt.title(
        'BoundingBoxes on Image'), plt.gca().invert_yaxis()  # invert back so origin is at bottom left

    # Save Image with bounding boxes
    save_location_path = os.path.join(vp_dir,
                                      condition + "_BoundingBoxes_VP" + str(VP_Index) + ".png")
    print("Figure saved in: {}".format(save_location_path))
    plt.savefig(save_location_path)

    # Show plot again for fast prototyping
    plt.show()

    return boundingBoxes, save_location_path, rectangles


# Calculate the height of the AoI in pixels on the reference
def calculate_heights_for_area_of_interest_positions(image_height, mirror_height, eye_height_in_px, eye_height,
                                                     head_height,
                                                     hands_height, feet_height):
    global scaling_factor_height
    aoi_positions = []
    # Calculate the scaling Factor. => 1CM in the real world equal x px on the Image
    scaling_factor = image_height / mirror_height
    scaling_factor_height = scaling_factor  # update  global variable for usage outside method
    print("Scaling factor height : " + str(scaling_factor))
    # Calculate centimeter differences of the AoIs from eyes
    diff_eye_head = eye_height - head_height
    diff_eye_hands = eye_height - hands_height
    diff_eye_feet = eye_height - feet_height
    # Transform it to px values and multiply it by 0.5 (intercept theorem)
    diff_eye_head_in_px = diff_eye_head * scaling_factor * 0.5
    diff_eye_hands_in_px = diff_eye_hands * scaling_factor * 0.5
    diff_eye_feet_in_px = diff_eye_feet * scaling_factor * 0.5
    # Subtract the px difference from the eyes to determine the height position of the Aoi
    head_height_px = eye_height_in_px - diff_eye_head_in_px
    hands_height_px = eye_height_in_px - diff_eye_hands_in_px
    feet_height_px = eye_height_in_px - diff_eye_feet_in_px
    aoi_positions.extend([head_height_px, hands_height_px, feet_height_px])

    return aoi_positions


def calculate_widths_for_area_of_interest_positions(image_width, mirror_width, head_width, hands_width, feet_width,
                                                    user_width):
    global scale_f_w
    AoI_Width_Positions = []
    # Calculate scaling factor
    scaling_factor = image_width / mirror_width
    scale_f_w = scaling_factor
    print("Scaling factor w : " + str(scaling_factor))
    # Calculate width of the AoI all in Pxs
    head_width = head_width * scaling_factor
    hands_width = hands_width * scaling_factor
    feet_width = feet_width * scaling_factor
    user_width = user_width * scaling_factor
    # Add to array
    AoI_Width_Positions.extend([head_width, hands_width, feet_width, user_width])

    return AoI_Width_Positions


def normalize_bounding_box_positions(boundingBoxes):
    # Transform Pixel Information to normalized (0 to 1) for the Fixation Detector.py
    for bb in boundingBoxes:
        bb[1].x0 = bb[1].x0 / imageWidth_in_pixels
        bb[1].x1 = bb[1].x1 / imageWidth_in_pixels
        bb[1].y0 = bb[1].y0 / imageHeight_in_pixels
        bb[1].y1 = bb[1].y1 / imageHeight_in_pixels
    return boundingBoxes


# Start of pipeline
user_input_dictionary, input_file = read_in_user_specific_data('Input\\User_Specific_Data.txt')
update_user_variable(user_input_dictionary)
vp_result_dir = create_results_folder(vp_Index, input_file)
imageHeight_in_pixels, imageWidth_in_pixels, image = read_in_user_image()
eye_height_in_px = transform_centimeters_to_pixels(eye_height - distance_mirror_to_ground, isHeight=True)
aoi_heights_in_px = calculate_heights_for_area_of_interest_positions(imageHeight_in_pixels, image_height_in_cm,
                                                                     eye_height_in_px,
                                                                     eye_height, head_height, hands_height, feet_height)
aoi_widths_in_px = calculate_widths_for_area_of_interest_positions(imageWidth_in_pixels, image_width_in_cm, head_width,
                                                                   hands_width, feet_width, user_width)

boundingBoxes, image_with_bb, rectangles = create_visual_bounding_boxes_on_image(image, vp_Index, vp_result_dir,
                                                                                 aoi_heights_in_px, aoi_widths_in_px)
normalize_bounding_box_positions(boundingBoxes)

# Call Fixation Detector with created Bounding Boxes
Fixation_Calculator.start_fixation_calculation(fixation_filename, boundingBoxes, vp_image, image_with_bb,
                                               vp_Index, start_time)
