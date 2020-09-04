import numpy as np
from pyaxidraw.axidraw import AxiDraw


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


def _draw_one_line(ad, l):
    start = l["x"][0], l["y"][0]
    # Move to first point in stroke
    ad.move(*start)
    for x, y in zip(np.diff(l["x"]), np.diff(l["y"])):
        ad.line(x, y)


def _draw_lines(ad: AxiDraw, lines, reference_xy=(0, 0)):
    # Goto ref
    for l in lines:
        ad.moveto(reference_xy[0], reference_xy[1])
        _draw_one_line(ad, l)


def draw_pic_from_drawing(ad, drawing,scale,reference_xy = None):
    lines = _reshape_strokes(drawing, scale=scale)
    if reference_xy is None:
        reference_xy = (
            np.random.uniform(low=10, high=270, size=1).astype(np.int64)[0],
            np.random.uniform(low=10, high=190, size=1).astype(np.int64)[0],
        )
    try:
        _draw_lines(ad, lines, reference_xy=reference_xy)
        return True
    except Exception as e:
        print(f"Failed! {e}")
        return False
