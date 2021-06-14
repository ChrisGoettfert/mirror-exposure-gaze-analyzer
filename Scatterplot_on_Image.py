import io
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde as kde
from matplotlib.colors import Normalize
from matplotlib import cm
from PIL import Image

def drawScatterplotOnImage(df, image, image_with_bb, VP_Index, ExperimentPhase):
    fig = plt.figure()
    img = plt.imread(image)
    imageWidth_in_pixels = img.shape[1]
    imageHeight_in_pixels = img.shape[0]

    data = df.copy()
    data['norm_pos_x'] = (data['norm_pos_x'] * imageWidth_in_pixels).astype(int)
    data['norm_pos_y'] = (data['norm_pos_y'] * imageHeight_in_pixels).astype(int)

    xList = []
    yList = []
    for entry in data.iterrows():
        point = [entry[1]['norm_pos_x'], entry[1]['norm_pos_y']]
        xList.append(point[0])
        yList.append(point[1])
        #print(point)
        #print()
    plt.scatter(xList, yList, alpha=0.5, zorder=1, color='red')


    ext = [0.0, imageWidth_in_pixels, 0.00,  imageHeight_in_pixels]
    plt.imshow(img, zorder=0, extent=ext)

    aspect = img.shape[0] / float(img.shape[1]) * ((ext[1] - ext[0]) / (ext[3] - ext[2]))
    plt.gca().set_aspect(aspect)

    plt.savefig(os.path.join(os.path.dirname(image_with_bb),
                              "Scatterplot_VP" + str(VP_Index) + "_" + ExperimentPhase + ".png"))
    image_with_scatter_plot =  os.path.join(os.path.dirname(image_with_bb), "Scatterplot_VP" + str(VP_Index)  + "_" + ExperimentPhase + ".png")
    plt.show()


    overLayTwoImages(image_with_bb, image_with_scatter_plot, VP_Index, ExperimentPhase)


def overLayTwoImages(Image1, Image2, VP_Index, ExperimentPhase):
    background = Image.open(Image1)
    overlay = Image.open(Image2)

    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    new_img = Image.blend(background, overlay, 0.5)
    new_img.save((os.path.join(os.path.dirname(Image1),
                              "Overlay_VP" + str(VP_Index) + "_" + ExperimentPhase + ".png")), "PNG")

    plt.imshow(new_img)
    plt.show()

def makeColours( vals ):
    colours = np.zeros( (len(vals),3) )
    norm = Normalize( vmin=vals.min(), vmax=vals.max() )

    #Can put any colormap you like here.
    colours = [cm.ScalarMappable( norm=norm, cmap='jet').to_rgba( val ) for val in vals]

    return colours
#colours = makeColours( densObj.evaluate( [xList,yList] ) )
#plt.scatter( xList, yList, color=colours )
#plt.show()
