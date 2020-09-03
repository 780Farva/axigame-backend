import logging
import random

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from pyaxidraw.axidraw import AxiDraw
from quickdraw import QuickDrawData
from transitions import Machine

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
        self._ad.options.speed_pendown = 1
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
        try:
            self._draw_pic(self.drawing_object)
        except:
            pass
        finally:
            self.drawing_complete()

    def on_enter_final_guessing(self):
        self.guess_timeout()

    def on_enter_completing(self):
        self.completed()

    def _draw_pic(self, drawing):
        fig, ax = plt.subplots(figsize=(2, 2))
        for stroke in drawing.strokes:
            x = [pt[0] for pt in stroke]
            y = [pt[1] for pt in stroke]
            ax.plot(x, y)
        ax.set_title(drawing.name)
        return fig, ax

    def _reshape_strokes(self, drawing, scale=5):
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

    def _draw_one_line(self, ad, l):
        start = l["x"][0], l["y"][0]
        # Move to first point in stroke
        ad.move(*start)
        for x, y in zip(np.diff(l["x"]), np.diff(l["y"])):
            ad.line(x, y)

    def _draw_lines(self, ad: AxiDraw, lines, reference_xy=(0, 0)):
        # Goto ref
        for l in lines:
            ad.moveto(reference_xy[0], reference_xy[1])
            self._draw_one_line(ad, l)

    def test(self):
        try:
            drawing = self._qd.get_drawing(name="key", index=1)

            st.write(f"strokes : {drawing.no_of_strokes}")
            fig, ax = self._draw_pic(drawing)
            fig.savefig("test.png")
            lines = self._reshape_strokes(drawing, scale=5)
            self._draw_lines(self._ad, lines, reference_xy=(102, 102))
        #     st.pyplot(fig,figsize=(2, 2))
        #    st.write(lines)

        finally:
            self._ad.moveto(0, 0)
            self._ad.disconnect()
