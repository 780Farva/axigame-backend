import logging
import random

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from pyaxidraw.axidraw import AxiDraw
from quickdraw import QuickDrawData
from transitions import Machine
from utils import _reshape_strokes, draw_pic_from_drawing

log = logging.getLogger(__name__)


class GameManager:
    """Handles the game's states and invokes AxiDraw commands"""

    states = [
        "idle",
        "initializing_axidraw",
        "loading_image",
        "drawing",
        "final_guessing",
        "completing",
    ]
    transitions = [
        {"trigger": "start", "source": "idle", "dest": "initializing_axidraw"},
        {
            "trigger": "axidraw_ready",
            "source": "initializing_axidraw",
            "dest": "loading_image",
        },
        {"trigger": "image_loaded", "source": "loading_image", "dest": "drawing"},
        {"trigger": "correct_guess_early", "source": "drawing", "dest": "completing"},
        {"trigger": "drawing_complete", "source": "drawing", "dest": "final_guessing"},
        {
            "trigger": "corrrect_guess_late",
            "source": "final_guessing",
            "dest": "completing",
        },
        {"trigger": "guess_timeout", "source": "final_guessing", "dest": "completing"},
        {"trigger": "completed", "source": "completing", "dest": "idle"},
    ]

    def __init__(self, axidraw_client: AxiDraw, quick_draw_data: QuickDrawData):
        # Initialize the state machine
        self._machine = Machine(
            model=self,
            states=GameManager.states,
            transitions=GameManager.transitions,
            initial="idle",
        )

        self._qd = quick_draw_data
        self._ad = axidraw_client

        self.drawing_name = None
        self.drawing_object = None

    def on_enter_initializing_axidraw(self):
        self._ad.interactive()
        self._ad.connect()
        self._ad.options.speed_pendown = 5
        self._ad.options.speed_penup = 100
        self._ad.options.units = 2
        self._ad.update()
        self.axidraw_ready()

    def on_enter_loading_image(self):
        # Select a drawing at random
        self.drawing_name = random.choice(self._qd.drawing_names)
        self.drawing_object = self._qd.get_drawing(self.drawing_name)
        self.image_loaded()

    def on_enter_idle(self):
        # Move back to home
        self._ad.moveto(0, 0)
        self._ad.disconnect()

    def on_enter_drawing(self):
        self._draw_pic(self.drawing_object)
        self.drawing_complete()

    def on_enter_final_guessing(self):
        self.guess_timeout()

    def on_enter_completing(self):
        self.drawing_name = None
        self.drawing_object = None
        self.completed()

    def _draw_pic(self, drawing):
        draw_pic_from_drawing(self._ad, drawing)

    # def test(self):
    #     reference_xy = np.random.uniform(low=0, high=250, size=1)[0], \
    #                    np.random.uniform(low=0, high=150, size=1)[0]
    #     try:
    #         drawing = self._qd.get_drawing(name="key", index=1)
    #         st.write(f"strokes : {drawing.no_of_strokes}")
    #         fig, ax = self._draw_pic(drawing)
    #         fig.savefig("test.png")
    #         lines = self._reshape_strokes(drawing, scale=5)
    #         self._draw_lines(self._ad, lines, reference_xy=reference_xy)
    #     finally:
    #         self._ad.moveto(0, 0)
    #         self._ad.disconnect()
