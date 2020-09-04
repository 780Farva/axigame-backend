import pickle
import random

import numpy as np
from pyaxidraw.axidraw import AxiDraw
from skimage.transform import resize
from tensorflow.python.keras.models import load_model

model = load_model('/home/anton/Repos/axigame-backend/model.h5')
with open('/home/anton/Repos/axigame-backend/le.pkl', 'rb') as f:
    le = pickle.load(f)


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    gray = resize(gray, (64, 64))
    return gray


def pred_image(drawing):
    im = rgb2gray(drawing.image)
    lab = model.predict(im.reshape(1, 64, 64, 1))
    top_10 = np.argsort(lab.flatten())[-10:]
    labels = random.shuffle(le.inverse_transform(top_10))

    return labels


def _reshape_strokes(drawing, scale=6):
    """
    Return list of dictionaries with strokes
    """
    lines = []
    for i, stroke in enumerate(drawing.strokes):
        x = np.array([pt[0] / scale for pt in stroke])
        y = np.array([pt[1] / scale for pt in stroke])
        id_stroke = i
        length = np.sum(np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2))
        line = {
            "id_stroke": id_stroke,
            "x": x,
            "y": y,
            "len": length,
            "n_pts": len(x),
        }
        lines.append(line)
    return lines


def _draw_one_line(ad, l, flag_callback):
    start = l["x"][0], l["y"][0]
    # Move to first point in stroke
    ad.move(*start)
    for x, y in zip(np.diff(l["x"]), np.diff(l["y"])):
        if not (flag_callback()):
            ad.line(x, y)
        else:
            print('Updating speeeeeeeeeeeeeeeeeeeeeeeeed!')
            ad.options.speed_pendown = 100
            ad.options.speed_penup = 100
            ad.options.units = 2
            ad.update()
            ad.line(x, y)


def _draw_lines(ad: AxiDraw, lines, reference_xy=(0, 0),
                flag_callback=None):
    # Goto ref
    for l in lines:
        ad.moveto(reference_xy[0], reference_xy[1])
        _draw_one_line(ad, l, flag_callback=flag_callback)


def draw_pic_from_drawing(ad, drawing, scale, reference_xy=None,
                          flag_callback=None):
    lines = _reshape_strokes(drawing, scale=scale)
    if reference_xy is None:
        reference_xy = (
            np.random.uniform(low=10, high=270, size=1).astype(np.int64)[0],
            np.random.uniform(low=10, high=190, size=1).astype(np.int64)[0],
        )
    try:
        _draw_lines(ad, lines, reference_xy=reference_xy,
                    flag_callback=flag_callback)
        return True
    except Exception as e:
        print(f"Failed! {e}")
        return False
