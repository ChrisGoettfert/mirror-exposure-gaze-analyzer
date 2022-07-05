import math
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import Scatterplot_on_Image

# List for eyes, chest, hips, feet
aoi_fixation_lists = [[], [], [], []]
average_errors = []
fixations_during_timephases = []
guided_dataframes = []
exploration_dataframes = []


def read_in_fixation_data(fixations_filename):
    # read in data
    df = pd.read_csv(fixations_filename)

    # drop all rows where fixation is not on surface
    df = df.loc[df['on_surf'] == True]
    # delete unneccessary columns from dataframe
    df = df[['fixation_id', 'norm_pos_x', 'norm_pos_y', 'duration', 'world_timestamp']]
    # For each fixation id in dataframe calculate the average of the norm_pos_x and norm_pos_y as there are multiply entrys
    aggregation_functions = {'fixation_id': 'first', 'norm_pos_x': 'mean', 'norm_pos_y': 'mean', 'duration': 'mean',
                             'world_timestamp': 'mean'}
    df_grouped = df.groupby(df['fixation_id']).aggregate(aggregation_functions)

    # Calculate Timestamps of the fixations
    df_grouped = calculate_timestamps(df_grouped)
    x_positions = df_grouped['norm_pos_x']
    y_positions = df_grouped['norm_pos_y']

    return df_grouped, x_positions, y_positions


# We need to calculate the time of the Fixation relevant to our video time so we can assign fixations to different tasks
# e.g. Seconds 30-40 voice command was look at your eyes then we want only those fixations
# Need to recalculate it, because the time in the results is in UNIX Time
def calculate_timestamps(df):
    world_timestamps = pd.read_csv("Input\\world_timestamps.csv")
    # Get the timestamp in seconds of the first frame recorded by our video => point zero
    first_frame_time = world_timestamps['# timestamps [seconds]'][0]
    # to get the time value of our fixations we simply need to subtract the first_frame_time from our fixation times
    df["world_timestamp"] = df["world_timestamp"] - first_frame_time
    df = df.rename(columns={"world_timestamp": "time_in_video (seconds)", "duration": "duration (ms)"})
    return df


def calculate_fixations_on_aois(bounding_boxes, df, aoi_fixation_lists):
    areas_of_interest = []
    durations = []

    for datapoint in df.iterrows():
        x = datapoint[1]["norm_pos_x"]
        y = datapoint[1]["norm_pos_y"]
        duration = datapoint[1]["duration (ms)"]
        fixation_id = datapoint[0]

        datapoint_added = False
        for bb in bounding_boxes:
            if (bb[1].x0 <= x <= bb[1].x1 and bb[1].y0 <= y <= bb[1].y1):
                datapoint_added = True
                if (bb[0] == "head"):
                    aoi_fixation_lists[0].append(fixation_id)
                    areas_of_interest.append(bb[0])
                    durations.append(duration)
                elif (bb[0] == "right_hand"):
                    aoi_fixation_lists[1].append(fixation_id)
                    areas_of_interest.append(bb[0])
                    durations.append(duration)
                elif (bb[0] == "left_hand"):
                    aoi_fixation_lists[2].append(fixation_id)
                    areas_of_interest.append(bb[0])
                    durations.append(duration)
                elif (bb[0] == "feet"):
                    aoi_fixation_lists[3].append(fixation_id)
                    areas_of_interest.append(bb[0])
                    durations.append(duration)
            # datapoint not in bounds of bb
        if not datapoint_added:
            areas_of_interest.append(None)
            durations.append(None)

    df['AoI'] = areas_of_interest
    df['Durations'] = durations
    fixations_on_bounding_box = df.pivot_table(index=['AoI'], aggfunc='size')
    durations_in_aois = df.groupby(['AoI'])['Durations'].agg(lambda x: x.unique().sum())
    print(durations_in_aois)
    print(fixations_on_bounding_box)
    results_list = [fixations_on_bounding_box, durations_in_aois]
    return results_list, df


def save_results_in_logfile(results_list, image_with_bb, average_errors, fixationsInTimePhases, df_explo1, df_explo2):
    # get path of result folder
    result_folder = os.path.dirname(image_with_bb)
    dfexplo1res, dfexplo2res = explorationPhaseDataProcessing(df_explo1, df_explo2)
    with open(result_folder + '\\Overallresults.txt', 'w') as f:
        for item in results_list:
            f.write("%s\n" % item)
        f.write("\n")
        f.write("Errors:")
        for item2 in average_errors:
            f.write("%s\n" % item2)
        f.write("\n")
        f.write("Fixations During Phases: " + "\n")
        for item3 in fixationsInTimePhases:
            f.write("%s\n" % item3)
        f.write("\n")
        f.write("Explo1: " + "\n")
        f.write("%s\n" % dfexplo1res)
        f.write("\n")
        f.write("Explo2: " + "\n")

        f.write("%s\n" % dfexplo2res)
    print(result_folder)


def explorationPhaseDataProcessing(df_explo1, df_explo2):
    df_explo1 = df_explo1.fillna("Not in any bb")
    dfExplo1res = df_explo1.pivot_table(index=['AoI'], aggfunc='size')
    df_explo2 = df_explo2.fillna("Not in any bb")
    dfExplo2res = df_explo2.pivot_table(index=['AoI'], aggfunc='size')
    print(dfExplo1res)
    return dfExplo1res, dfExplo2res


def create_heatmap(x, y, image, image_with_bb, vp_ndex):
    # Construct 2D histogram from data using the 'plasma' colormap
    plt.hist2d(x, y, bins=15, range=[[0, 1], [0, 1]], density=True, cmap='plasma')

    # Plot a colorbar with label.
    cb = plt.colorbar()
    cb.set_label('Number of Fixations')

    # Add title and labels to plot.
    plt.title('Heatmap of detected Fixations')
    plt.xlabel('x axis')
    plt.ylabel('y axis')

    map_img = mpimg.imread(image)
    plt.imshow(map_img, zorder=0)

    plt.savefig(os.path.join(os.path.dirname(image_with_bb),
                             "Heatmap_VP" + str(vp_ndex) + ".png"))

    plt.show()


def calculate_fixations_with_timestamps(df, bounding_boxes, phasename):
    bb = None
    counter = 0
    duration = 0
    for b in bounding_boxes:
        if (b[0] == phasename):
            bb = b
    for datapoint in df.iterrows():
        x = datapoint[1]["norm_pos_x"]
        y = datapoint[1]["norm_pos_y"]
        if (bb[1].x0 <= x <= bb[1].x1 and bb[1].y0 <= y <= bb[1].y1):
            counter += 1
            duration += datapoint[1]["duration (ms)"]

    duration = round((duration / 1000), 2)  # to seconds
    return [phasename, "Fixations Inside " + phasename + " " + str(counter), "Duration: " + str(duration) + " seconds"]


def calculate_average_error_to_bounding_boxes(df, boundingBox, boundingBoxName):
    bb = None
    for b in boundingBox:
        if (b[0] == boundingBoxName):
            bb = b
    Mirror_Height = 112
    Mirror_Width = 59.3
    middlePointOfBoundingBoxXInCm = ((bb[1].x1 + bb[1].x0) / 2) * Mirror_Width
    middlePointOfBoundingBoxYInCm = ((bb[1].y1 + bb[1].y0) / 2) * Mirror_Height
    results = []
    for datapoint in df.iterrows():
        distance = math.hypot(datapoint[1]["norm_pos_x"] * Mirror_Width - middlePointOfBoundingBoxXInCm,
                              datapoint[1]["norm_pos_y"] * Mirror_Height - middlePointOfBoundingBoxYInCm)
        results.append(distance)
    res = np.mean(results)
    return res


def perform_timestamp_based_calculations(df, start_time, bounding_boxes):
    df_all, df_explo1, df_head, df_right_hand, df_left_hand, df_feet, df_explo2 = split_dataframes_by_timestamps(df,
                                                                                                                 start_time)

    average_errors.append(["Head", calculate_average_error_to_bounding_boxes(df_head, bounding_boxes, "head")])
    average_errors.append(
        ["RightHand", calculate_average_error_to_bounding_boxes(df_right_hand, bounding_boxes, "right_hand")])
    average_errors.append(
        ["LeftHand", calculate_average_error_to_bounding_boxes(df_left_hand, bounding_boxes, "left_hand")])
    average_errors.append(["Feet", calculate_average_error_to_bounding_boxes(df_feet, bounding_boxes, "feet")])

    head_fixations = calculate_fixations_with_timestamps(df_head, bounding_boxes, "head")
    right_hand_fixations = calculate_fixations_with_timestamps(df_right_hand, bounding_boxes, "right_hand")
    left_hand_fixations = calculate_fixations_with_timestamps(df_left_hand, bounding_boxes, "left_hand")
    feet_fixations = calculate_fixations_with_timestamps(df_feet, bounding_boxes, "feet")

    fixations_during_timephases.extend(
        [[head_fixations], [right_hand_fixations], [left_hand_fixations], [feet_fixations]])
    guided_dataframes.extend([df_head, df_right_hand, df_left_hand, df_feet])
    exploration_dataframes.extend([df_explo1, df_explo2])


def create_scatterplots_on_image(df_all, image, image_with_bb, vp_index):
    iterator = [[df_all, "All"], [guided_dataframes[0], "Head"], [guided_dataframes[1], "RightHand"], [
        guided_dataframes[2], "LeftHand"],
                [guided_dataframes[3], "Feet"], [exploration_dataframes[0], "Explorative1"], [exploration_dataframes[1],
                                                                                              "Explorative2"]]

    for i in iterator:
        Scatterplot_on_Image.drawScatterplotOnImage(i[0], image, image_with_bb, vp_index, i[1])


def start_fixation_calculation(fixations_filename, boundingboxes, image, image_with_bb, vp_index,
                               start_time):
    image = "Input\\" + image
    fixations_filename = "Input\\" + fixations_filename
    print("Processing fixations in file: " + fixations_filename)

    df, x_positions, y_positions = read_in_fixation_data(fixations_filename)
    results_list, df = calculate_fixations_on_aois(boundingboxes, df, aoi_fixation_lists)

    perform_timestamp_based_calculations(df, start_time, boundingboxes)
    save_results_in_logfile(results_list, image_with_bb, average_errors, fixations_during_timephases,
                            exploration_dataframes[0], exploration_dataframes[1])

    create_heatmap(df['norm_pos_x'], df['norm_pos_y'], image, image_with_bb, vp_index)
    create_scatterplots_on_image(df, image, image_with_bb, vp_index)


# Cut Dataframe by seconds based on the audioinstructions
def split_dataframes_by_timestamps(df, start_time):
    # Start at 14 since instruction was 14 seconds long. 84 = end of audio file
    mask = (df['time_in_video (seconds)'] > start_time + 14) & (df['time_in_video (seconds)'] <= start_time + 84)
    df_all = df.loc[mask]
    mask_explorative1 = (df['time_in_video (seconds)'] > start_time + 19) & (
                df['time_in_video (seconds)'] <= start_time + 41)
    df_explorative1 = df.loc[mask_explorative1]
    mask_head = (df['time_in_video (seconds)'] > start_time + 44) & (df['time_in_video (seconds)'] <= start_time + 49)
    df_head = df.loc[mask_head]
    mask_left_hand = (df['time_in_video (seconds)'] > start_time + 52) & (
                df['time_in_video (seconds)'] <= start_time + 57)
    df_left_hand = df.loc[mask_left_hand]
    mask_right_hand = (df['time_in_video (seconds)'] > start_time + 60) & (
                df['time_in_video (seconds)'] <= start_time + 65)
    df_right_hand = df.loc[mask_right_hand]
    mask_feet = (df['time_in_video (seconds)'] > start_time + 68) & (df['time_in_video (seconds)'] <= start_time + 73)
    df_feet = df.loc[mask_feet]
    mask_explorative2 = (df['time_in_video (seconds)'] > start_time + 76) & (
                df['time_in_video (seconds)'] <= start_time + 84)
    df_explorative2 = df.loc[mask_explorative2]

    return df_all, df_explorative1, df_head, df_left_hand, df_right_hand, df_feet, df_explorative2


if __name__ == '__main__':
    print()
