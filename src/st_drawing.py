import streamlit as st
import pandas as pd
from quickdraw import QuickDrawData

qd = QuickDrawData(recognized=True, jit_loading=False, max_drawings=1000)
qd.load_all_drawings()
drawings = qd.loaded_drawings
n_strokes = [d.no_of_strokes for d in drawings]

anvil = qd.get_drawing(name="dolphin")
st.image(anvil.image)
st.write(f"Groups loaded: {qd.drawing_names}")
