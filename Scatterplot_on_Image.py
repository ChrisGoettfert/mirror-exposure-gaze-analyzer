import os
import matplotlib.pyplot as plt
from PIL import Image


def draw_scatterplot_on_image(df, image, image_with_bb, vp_index, experiment_phase):
    img = plt.imread(image)
    image_width_in_pixels = img.shape[1]
    image_height_in_pixels = img.shape[0]
    df = df.copy()
    df['norm_pos_x'] = (df['norm_pos_x'] * image_width_in_pixels).astype(int)
    df['norm_pos_y'] = (df['norm_pos_y'] * image_height_in_pixels).astype(int)

    x_list = []
    yLy_list = []

    for entry in df.iterrows():
        point = [entry[1]['norm_pos_x'], entry[1]['norm_pos_y']]
        x_list.append(point[0])
        yLy_list.append(point[1])
    plt.scatter(x_list, yLy_list, alpha=0.5, zorder=1, color='red')
    ext = [0.0, image_width_in_pixels, 0.00, image_height_in_pixels]
    plt.imshow(img, zorder=0, extent=ext)

    aspect = img.shape[0] / float(img.shape[1]) * ((ext[1] - ext[0]) / (ext[3] - ext[2]))
    plt.gca().set_aspect(aspect)
    save_location_path = os.path.join(os.path.dirname(image_with_bb),
                                      "Scatterplot_VP" + str(vp_index) + "_" + experiment_phase + ".png")
    plt.savefig(save_location_path)
    image_with_scatter_plot = save_location_path
    plt.show()

    create_overlay_picture(image_with_bb, image_with_scatter_plot, vp_index, experiment_phase)


def create_overlay_picture(Image1, Image2, VP_Index, ExperimentPhase):
    background = Image.open(Image1)
    overlay = Image.open(Image2)

    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    overlay_img = Image.blend(background, overlay, 0.5)
    overlay_img.save((os.path.join(os.path.dirname(Image1),
                               "Overlay_VP" + str(VP_Index) + "_" + ExperimentPhase + ".png")), "PNG")

    plt.imshow(overlay_img)
    plt.show()
