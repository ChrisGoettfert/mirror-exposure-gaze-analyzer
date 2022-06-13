import math
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import Scatterplot_on_Image

input_features = 3
filename = ""
boundingboxes = None
# List for eyes, chest, hips, feet
AoI_Fixation_Lists = [[], [], [], []]


def readInFixationData(filename):
    # read in data
    df = pd.read_csv(filename)

    # drop all rows where fixation is not on surface
    df = df.loc[df['on_surf'] == True]
    # Clean DF
    df = df[['fixation_id', 'norm_pos_x', 'norm_pos_y', 'duration', 'world_timestamp']]

    #df.to_csv("fixations_on_surface_Surface 1_TRUE.csv")
    # For each id in dataframe calculate the average of the norm_pos_x and norm_pos_y
    aggregation_functions = {'fixation_id': 'first', 'norm_pos_x': 'mean', 'norm_pos_y': 'mean', 'duration': 'mean',
                             'world_timestamp': 'mean'}
    df_new = df.groupby(df['fixation_id']).aggregate(aggregation_functions)

    # Calculate Timestamps of the fixations
    df_new = calculateTimestamps(df_new)

    # load the coordinates file
    x = df_new['norm_pos_x']
    y = df_new['norm_pos_y']

    return df_new, x, y

# We need to calculate the time of the Fixation relevant to our video time so we can assign fixations to different tasks
# e.g. Seconds 30-40 voice command was look at your eyes then we want those fixations and only those
# Need to recalculate it, because the time in the results is in UNIX Time
def calculateTimestamps(df):
    world_timestamps = pd.read_csv("Input\\world_timestamps.csv")
    # Get the timestamp in seconds of the first frame recorded by our video from the world_timestamps csv (always exported)
    # this is our reference to a point zero
    first_frame_time = world_timestamps['# timestamps [seconds]'][0]
    # to get the time value of our fixations we simply need to subtract the first_frame_time from our fixation times
    df["world_timestamp"] = df["world_timestamp"] - first_frame_time
    df = df.rename(columns={"world_timestamp": "time_in_video (seconds)", "duration": "duration (ms)"})
    print()

    return df


def calculateFixationsOnAoIs(boundingBoxes, df, AoI_Fixation_Lists):
    print()
    features = []
    durations = []

    for datapoint in df.iterrows():
        x = datapoint[1]["norm_pos_x"]
        y = datapoint[1]["norm_pos_y"]
        duration = datapoint[1]["duration (ms)"]
        fixation_id = datapoint[0]

        datapoint_added = False
        for bb in boundingBoxes:
            if(bb[1].x0 <= x <= bb[1].x1 and bb[1].y0 <= y <= bb[1].y1):
                datapoint_added = True
                if(bb[0] == "head"):
                    AoI_Fixation_Lists[0].append(fixation_id)
                    features.append(bb[0])
                    durations.append(duration)
                elif(bb[0] == "right_hand"):
                    AoI_Fixation_Lists[1].append(fixation_id)
                    features.append(bb[0])
                    durations.append(duration)
                elif (bb[0] == "left_hand"):
                    AoI_Fixation_Lists[2].append(fixation_id)
                    features.append(bb[0])
                    durations.append(duration)
                elif(bb[0] == "feet"):
                    AoI_Fixation_Lists[3].append(fixation_id)
                    features.append(bb[0])
                    durations.append(duration)
            # datapoint not in bounds of bb
        if not datapoint_added:
            features.append(None)
            durations.append(None)

    df['AoI'] = features
    df['Durations'] = durations
    Fixations_On_BoundingBox = df.pivot_table(index=['AoI'], aggfunc='size')
    durations_in_AoIs = df.groupby(['AoI'])['Durations'].agg(lambda x: x.unique().sum())
    print(durations_in_AoIs)
    print (Fixations_On_BoundingBox)
    results_list = [Fixations_On_BoundingBox, durations_in_AoIs]
    return results_list, df



def saveResultsInLogFile(results_list, image_with_bb, average_errors, fixationsInTimePhases, dfExplo1, dfExplo2):
    # get path of result folder
    result_folder = os.path.dirname(image_with_bb)
    dfexplo1res, dfexplo2res = explorationPhaseDataProcessing(dfExplo1, dfExplo2)
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

def explorationPhaseDataProcessing(dfExplo1, dfExplo2):
    dfExplo1 = dfExplo1.fillna("Not in any bb")
    dfExplo1res = dfExplo1.pivot_table(index=['AoI'], aggfunc='size')
    dfExplo2 = dfExplo2.fillna("Not in any bb")
    dfExplo2res = dfExplo2.pivot_table(index=['AoI'], aggfunc='size')
    print(dfExplo1res)
    return dfExplo1res, dfExplo2res
def createHeatmapOnImage(x, y, feature_width, image, image_with_bb, VP_Index):
    # Construct 2D histogram from data using the 'plasma' colormap
    plt.hist2d(x, y, bins=15, range= [[0, 1], [0,1]], density=True, cmap='plasma')

    # Plot a colorbar with label.
    cb = plt.colorbar()
    cb.set_label('Number of Fixations')

    # Add title and labels to plot.
    plt.title('Heatmap of detected Fixations')
    plt.xlabel('x axis')
    plt.ylabel('y axis')

    xcoords = [feature_width, feature_width * 2, feature_width * 3]
    colors = ['r','r','r']

    # Draw vertical line on image
    #for xc,c in zip(xcoords,colors):
        #plt.axvline(x=xc, label='line at x = {}'.format(xc), c=c)

    # Show the plot.

    map_img = mpimg.imread(image)
    plt.imshow(map_img, zorder=0)

    # Need to save before showing else its blank
    plt.savefig(os.path.join(os.path.dirname(image_with_bb),
                              "Heatmap_VP" + str(VP_Index) + ".png"))

    plt.show()

def calculateFixationsWithTimestamps(df, boundingboxes, phasename):
    bb = None
    counter = 0
    duration = 0
    for b in boundingboxes:
        if (b[0] == phasename):
            bb = b
    for datapoint in df.iterrows():
        x = datapoint[1]["norm_pos_x"]
        y = datapoint[1]["norm_pos_y"]
        if (bb[1].x0 <= x <= bb[1].x1 and bb[1].y0 <= y <= bb[1].y1):
            counter += 1
            duration += datapoint[1]["duration (ms)"]

    duration = round((duration / 1000), 2)    # to seconds
    return [phasename, "Fixations Inside " + phasename + " " + str(counter), "Duration: " + str(duration) + " seconds"]


def CalculateAverageErrorToBoundingBoxes(df, boundingBox, boundingBoxName):
    bb = None
    for b in boundingBox:
        if(b[0] == boundingBoxName):
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
    res =  np.mean(results)
    return res




def startFixationCalculationOnBoundingBoxes(filename, boundingboxes, image, image_with_bb, VP_Index, start_time):
    average_Errors = []
    fixationsInTimePhases = []
    image = "Input\\" + image
    filename = "Input\\" + filename
    print("FileName: " + filename)
    print(os.path.dirname(os.path.realpath(__file__)))
    df, x, y = readInFixationData(filename)
    results_list, df  = calculateFixationsOnAoIs(boundingboxes, df, AoI_Fixation_Lists)
    df_all, dfExplo1, dfHead, dfRightHand, dfLeftHand, dfFeet, dfExplo2 = SplitDataframesByTimeStamps(df, start_time)
    average_Errors.append(["Head", CalculateAverageErrorToBoundingBoxes(dfHead, boundingboxes, "head")])
    average_Errors.append(["RightHand", CalculateAverageErrorToBoundingBoxes(dfRightHand, boundingboxes, "right_hand")])
    average_Errors.append(["LeftHand", CalculateAverageErrorToBoundingBoxes(dfLeftHand, boundingboxes, "left_hand")])
    average_Errors.append(["Feet", CalculateAverageErrorToBoundingBoxes(dfFeet, boundingboxes, "feet")])



    headFixations = calculateFixationsWithTimestamps(dfHead, boundingboxes, "head")
    rightHandFixations = calculateFixationsWithTimestamps(dfRightHand, boundingboxes, "right_hand")
    leftHandFixations = calculateFixationsWithTimestamps(dfLeftHand, boundingboxes, "left_hand")
    feetFixations = calculateFixationsWithTimestamps(dfFeet, boundingboxes, "feet")

    fixationsInTimePhases.extend([[headFixations], [rightHandFixations], [leftHandFixations], [feetFixations]])
    saveResultsInLogFile(results_list, image_with_bb, average_Errors, fixationsInTimePhases, dfExplo1, dfExplo2)
    createHeatmapOnImage(x, y, 0.33, image, image_with_bb, VP_Index)
    Scatterplot_on_Image.drawScatterplotOnImage(df, image, image_with_bb, VP_Index, "All")
    Scatterplot_on_Image.drawScatterplotOnImage(dfHead, image, image_with_bb, VP_Index, "Head")
    Scatterplot_on_Image.drawScatterplotOnImage(dfRightHand, image, image_with_bb, VP_Index, "RightHand")
    Scatterplot_on_Image.drawScatterplotOnImage(dfLeftHand, image, image_with_bb, VP_Index, "LeftHand")
    Scatterplot_on_Image.drawScatterplotOnImage(dfFeet, image, image_with_bb, VP_Index, "Feet")
    Scatterplot_on_Image.drawScatterplotOnImage(dfExplo1, image, image_with_bb, VP_Index, "Explo1")
    Scatterplot_on_Image.drawScatterplotOnImage(dfExplo2, image, image_with_bb, VP_Index, "Explo2")

def SplitDataframesByTimeStamps(df, start_time):
    starttime = start_time
    dfExplo1 = None
    dfHead = None
    dfRightHand = None
    dfLeftHand = None
    dfFeet = None
                        # + 14 weil nach 14 gehts los mit der betrachtung, + 85 weil so lang ging die Betrachtung
    mask = (df['time_in_video (seconds)'] > starttime + 14) & (df['time_in_video (seconds)'] <= starttime + 84)
    df_all = df.loc[mask]
    mask_Explo1 = (df['time_in_video (seconds)'] > starttime + 19) & (df['time_in_video (seconds)'] <= starttime + 41)
    dfExplo1 = df.loc[mask_Explo1]
    mask_Head = (df['time_in_video (seconds)'] > starttime + 44) & (df['time_in_video (seconds)'] <= starttime + 49)
    dfHead = df.loc[mask_Head]
    maskLeftHand = (df['time_in_video (seconds)'] > starttime + 52) & (df['time_in_video (seconds)'] <= starttime + 57)
    dfLeftHand = df.loc[maskLeftHand]
    maskRightHand = (df['time_in_video (seconds)'] > starttime + 60) & (df['time_in_video (seconds)'] <= starttime + 65)
    dfRightHand = df.loc[maskRightHand]
    maskFeet = (df['time_in_video (seconds)'] > starttime + 68) & (df['time_in_video (seconds)'] <= starttime + 73)
    dfFeet = df.loc[maskFeet]
    maskExplo2 = (df['time_in_video (seconds)'] > starttime + 76) & (df['time_in_video (seconds)'] <= starttime + 84)
    dfExplo2 = df.loc[maskExplo2]


    return df_all, dfExplo1, dfHead, dfLeftHand, dfRightHand, dfFeet, dfExplo2






if __name__ == '__main__':
    print()




