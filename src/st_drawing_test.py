import streamlit as st
import pandas as pd
from quickdraw import QuickDrawData
import matplotlib.pyplot as plt
import numpy as np

qd = QuickDrawData(jit_loading=True, max_drawings=100)


def draw_pic(drawing):
    fig, ax = plt.subplots(figsize=(2, 2))
    for stroke in drawing.strokes:
        x = [pt[0] for pt in stroke]
        y = [pt[1] for pt in stroke]
        ax.plot(x, y)
    ax.set_title(drawing.name)
    return fig, ax


def reshape_strokes(drawing):
    """
    Return list of dictionaries with strokes
    """
    lines = []
    for i, stroke in enumerate(drawing.strokes):
        x = ([pt[0] for pt in stroke])
        y = ([pt[1] for pt in stroke])
        id_stroke = i
        length = np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2))
        line = {'id_stroke': id_stroke, 'x': x, 'y': y,'len':length,
                'n_pts':len(x)}
        lines.append(line)
    return lines


drawing = qd.get_drawing(name='key')
st.write(f'strokes : {drawing.no_of_strokes}')
fig, ax = draw_pic(drawing)
lines = reshape_strokes(drawing)
st.pyplot(fig,figsize=(2, 2))
st.write(lines)