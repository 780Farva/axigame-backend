import streamlit as st
import pandas as pd
from quickdraw import QuickDrawData
import matplotlib.pyplot as plt
import numpy as np
from pyaxidraw.axidraw import AxiDraw

qd = QuickDrawData(jit_loading=True, max_drawings=100)


def draw_pic(drawing):
    fig, ax = plt.subplots(figsize=(2, 2))
    for stroke in drawing.strokes:
        x = [pt[0] for pt in stroke]
        y = [pt[1] for pt in stroke]
        ax.plot(x, y)
    ax.set_title(drawing.name)
    return fig, ax


def reshape_strokes(drawing, scale=5):
    """
    Return list of dictionaries with strokes
    """
    lines = []
    for i, stroke in enumerate(drawing.strokes):
        x = np.array([pt[0] / scale for pt in stroke])
        y = np.array([pt[1] / scale for pt in stroke])
        id_stroke = i
        length = np.sum(np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2))
        line = {'id_stroke': id_stroke, 'x': x, 'y': y, 'len': length,
                'n_pts': len(x)}
        lines.append(line)
    return lines


def draw_one_line(ad, l):
    start = l['x'][0], l['y'][0]
    # Move to first point in stroke
    ad.move(*start)
    for x, y in zip(np.diff(l['x']), np.diff(l['y'])):
        ad.line(x, y)


def draw_lines(ad: AxiDraw, lines, reference_xy=(0, 0)):
    # Goto ref
    for l in lines:
        ad.moveto(reference_xy[0], reference_xy[1])
        draw_one_line(ad, l)

def draw_pic_from_lines(lines, reference_xy=(0, 0)):
    # Goto ref
    fig, ax = plt.subplots(figsize=(2, 2))

    for l in lines:
        ax.plot(l['x'],l['y'])
    return fig,ax

ad = AxiDraw()
ad.interactive()
ad.connect()
ad.options.speed_pendown=5
ad.options.speed_penup=100
ad.options.units = 2
ad.update()
try:
    # 6435186029887488
    drawing = qd.get_drawing(name='key')

    st.write(f'strokes : {drawing.no_of_strokes}')
    lines = reshape_strokes(drawing,scale=6)
    fig, ax = draw_pic_from_lines(lines)
    fig.savefig('test.png')

    reference_xy = np.random.uniform(low=0,high=250,size=1)[0],  np.random.uniform(low=0, high=150, size=1)[0]
    #draw_lines(ad,lines,reference_xy=reference_xy)
#     st.pyplot(fig,figsize=(2, 2))
#    st.write(lines)

finally:
    ad.moveto(0, 0)
    ad.disconnect()
