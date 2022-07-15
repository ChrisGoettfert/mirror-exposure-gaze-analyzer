import os
import shutil
from random import randrange
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import Fixation_Calculator


# Class Variables


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
            if (key == "Eye_Height"):
                d[key] = float(val) + 2  # Since the Camera is slightly above the eye we need to
                continue  # add a small amount to the eye height to fit the BoundingBox on the Eyes
            d[key] = float(val)
    return d, user_specific_data


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
def transform_centimeters_to_pixels(value, mirror_value_in_cm, mirror_value_in_px):
    if (value is 0):
        return
    transformed_value = mirror_value_in_px / mirror_value_in_cm * value
    print(mirror_value_in_px / mirror_value_in_cm)
    return transformed_value


def read_in_user_image():
    # read in image
    img = mpimg.imread("Input\\" + user_input_dictionary["VP_Image"])
    # get width and height of the picture
    imageWidth_in_pixels = img.shape[1]
    imageHeight_in_pixels = img.shape[0]
    print("Picture Width: " + str(imageWidth_in_pixels) + " Height: " + str(imageHeight_in_pixels))

    return imageHeight_in_pixels, imageWidth_in_pixels, img

    # check in user specific data maybe?
    # and add them but


def add_all_areas_of_interest_position_values_to_list():
    pass


# Visualize bounding boxes on the reference image
def create_visual_bounding_boxes_on_image(image, vp_index, vp_dir, aoi_heights_in_px, aoi_widths_in_px):
    # create Rectangles or for us called AoIs
    #
    #
    #                +------------------+
    #                |                  |
    #              height               |
    #                |                  |
    #               (xy)---- width -----+
    # Rectangles = (xy, width, height)
    scaling_factor_height = user_input_dictionary["scaling_factor_height"]
    middle_of_image = 0.5 * imageWidth_in_pixels
    # Get measured heights of the body parts for our bounding boxes
    boundingbox_height_head = user_input_dictionary["Head_Height"]
    boundingbox_height_hands = user_input_dictionary["Hands_Height"]
    boundingbox_height_feet = user_input_dictionary["Feet_Height"]
    rectangles = [
        # Rectangle( xy, width, height, color, filling, label)
        # head
        # Explanation:
        # Rectangles = (xy, width, height)
        # x = From the middle of the image (where the middle of the user should be located) we subtract
        #             half of the aoi widths (since half the width gives us the starting point)
        # y = The first aoi height position. This gives us the Tupple xy
        # width = The first calculated aoi width in px
        # height = 22 (avg. head height see paper) * scaling factor (gives us the pixel height) * 0.5 (intercept theorem)
        #                           same idea as in method calculate_heights_for_area_of_interest_positions()
        patches.Rectangle((middle_of_image - (aoi_widths_in_px[0] * 0.5), aoi_heights_in_px[0]),
                          aoi_widths_in_px[0], boundingbox_height_head * scaling_factor_height * 0.5, edgecolor='r',
                          facecolor="none",
                          label="head"),

        # right hand
        # Without the addition after the height position hand bounding boxes would be way to low
        # We add half of the average feet height since in the image the verse are higher than the toes
        # and technically we need to measure from the point zero but it gets very complicated here
        patches.Rectangle((middle_of_image - ((user_input_dictionary["user_width_px"] + 30) * 0.5),
                           aoi_heights_in_px[1] + (boundingbox_height_feet * scaling_factor_height * 0.5) * 0.5),
                          aoi_widths_in_px[1], boundingbox_height_hands * scaling_factor_height * 0.5, edgecolor='r',
                          facecolor="none",
                          label="right_hand"),

        # left hand
        patches.Rectangle((0.5 * imageWidth_in_pixels + ((user_input_dictionary["user_width_px"] - 30) * 0.5),
                           aoi_heights_in_px[1] + (boundingbox_height_feet * scaling_factor_height * 0.5) * 0.5),
                          aoi_widths_in_px[1], boundingbox_height_hands * scaling_factor_height * 0.5, edgecolor='r',
                          facecolor="none",
                          label="left_hand"),

        # Feet
        patches.Rectangle((middle_of_image - (aoi_widths_in_px[2] * 0.5), aoi_heights_in_px[2]),
                          aoi_widths_in_px[2], boundingbox_height_feet * scaling_factor_height * 0.5, edgecolor='r',
                          facecolor="none",
                          label="feet"),

        # Add here another rectangle for another boundingbox
        # patches.Rectangle((middle_of_image - (aoi_widths_in_px[x] * 0.5), aoi_heights_in_px[x]),
        #                 aoi_widths_in_px[x], your_avg_aoi_height * scaling_factor_height * 0.5, edgecolor='r',
        #                 facecolor="none", label="youraoi"),
    ]
    figure, ax = plt.subplots(1)
    bounding_boxes = []
    image = image[::-1, :, :]  # flip image for better processing

    # Draw Rectangle on to the image
    # Add Boundingbox information to boundingbox array for later usage
    for rects in rectangles:
        ax.add_patch(rects)
        bounding_boxes.append([rects.get_label(), rects.get_bbox()])
        print("Name of created Area of Interest: " + rects.get_label())
        print('{0} height px: {1} and width: {2}'.format(rects.get_label(), rects.get_height(), rects.get_width()))
    # Customize plot
    plt.imshow(image), plt.title(
        'BoundingBoxes on Image'), plt.gca().invert_yaxis()  # invert back so origin is at bottom left

    # Save Image with bounding boxes
    save_location_path = os.path.join(vp_dir,
                                      user_input_dictionary["Condition"] + "_BoundingBoxes_VP" + str(vp_index) + ".png")
    print("Figure saved in: {}".format(save_location_path))
    plt.savefig(save_location_path)

    # Show plot again for fast prototyping
    plt.show()

    return bounding_boxes, save_location_path, rectangles


# Calculate the height of the AoI in pixels on the reference
def calculate_heights_for_area_of_interest_positions(image_height, eye_height_in_px,
                                                     aoi_heights):
    aoi_diffs = []
    aoi_positions = []
    mirror_height = user_input_dictionary["Mirror_Height"]
    eye_height = user_input_dictionary["Eye_Height"]

    # Calculate the scaling Factor. => 1CM in the real world equal x px on the Image
    scaling_factor = image_height / mirror_height
    user_input_dictionary["scaling_factor_height"] = scaling_factor
    print("Scaling factor height : " + str(scaling_factor))

    for i in aoi_heights:
        aoi_diffs.append(eye_height - i)
    for j in aoi_diffs:
        aoi_positions.append(eye_height_in_px - (j * scaling_factor * 0.5))

    """ Below old code for our specific AoIs. The above one is more friendly to extentions of our system
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
    aoi_positions2.extend([head_height_px, hands_height_px, feet_height_px])
    """
    return aoi_positions


def calculate_widths_for_area_of_interest_positions(image_width, aoi_widths):
    aoi_width_positions = []
    mirror_width = user_input_dictionary["Mirror_Width"]
    user_width = user_input_dictionary["User_Width"]
    # Calculate scaling factor
    scaling_factor = image_width / mirror_width
    user_input_dictionary["scaling_factor_width"] = scaling_factor
    print("Scaling factor w : " + str(scaling_factor))
    # Calculate width of the AoI all in Pxs
    for i in aoi_widths:
        aoi_width_positions.append(i * scaling_factor)
    user_input_dictionary["user_width_px"] = user_width * scaling_factor

    """ Below again old code for our specific usecase
    head_width = head_width * scaling_factor
    hands_width = hands_width * scaling_factor
    feet_width = feet_width * scaling_factor
    user_width = user_width * scaling_factor
    # Add to array
    aoi_width_positions.extend([head_width, hands_width, feet_width, user_width])
    """
    return aoi_width_positions


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
vp_index = int(user_input_dictionary["VP_Index"])
vp_result_dir = create_results_folder(vp_index, input_file)
imageHeight_in_pixels, imageWidth_in_pixels, image = read_in_user_image()
eye_height_in_px = transform_centimeters_to_pixels(user_input_dictionary["Eye_Height"] -
                                                   user_input_dictionary["Distance_Mirror_Ground"],
                                                   user_input_dictionary["Mirror_Height"],
                                                   imageHeight_in_pixels)

# add all relevant aoi heights to a list
aoi_heights = [user_input_dictionary["Head_Height_Pos"],
               user_input_dictionary["Hands_Height_Pos"], user_input_dictionary["Feet_Height_Pos"]]
aoi_widths = [user_input_dictionary["Head_Width"], user_input_dictionary["Hands_Width"],
              user_input_dictionary["Feet_Width"]]
# Calculate pixel values from cms for both height and width
aoi_heights_in_px = calculate_heights_for_area_of_interest_positions(imageHeight_in_pixels,
                                                                     eye_height_in_px, aoi_heights)
aoi_widths_in_px = calculate_widths_for_area_of_interest_positions(imageWidth_in_pixels, aoi_widths)
# Create visual bounding boxes
boundingBoxes, image_with_bb, rectangles = create_visual_bounding_boxes_on_image(image,
                                                                                 vp_index,
                                                                                 vp_result_dir,
                                                                                 aoi_heights_in_px, aoi_widths_in_px)
normalize_bounding_box_positions(boundingBoxes)
# Call Fixation Detector with created Bounding Boxes
Fixation_Calculator.start_fixation_calculation(user_input_dictionary["Fixation_Filename"], boundingBoxes,
                                               user_input_dictionary["VP_Image"], image_with_bb,
                                               vp_index, user_input_dictionary["Start_time"])
