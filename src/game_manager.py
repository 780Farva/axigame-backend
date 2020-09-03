import logging
import random

from pyaxidraw.axidraw import AxiDraw
from quickdraw import QuickDrawData
from transitions.extensions.asyncio import AsyncMachine
from transitions import Machine
from utils import _reshape_strokes, draw_pic_from_drawing
from time import sleep

log = logging.getLogger(__name__)
PEN_SLOW = 50

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

    def __init__(self, axidraw_client: AxiDraw, quick_draw_data: QuickDrawData, sim=False):
        # Initialize the state machine
        self._machine = Machine(
            model=self,
            states=GameManager.states,
            transitions=GameManager.transitions,
            initial="idle",
        )

        self._sim = sim
        self._qd = quick_draw_data
        self._ad = axidraw_client

        self.drawing_name = None
        self.drawing_object = None

    def on_enter_initializing_axidraw(self):
        if self._sim:
            log.info("SIMULATION sleeping")
            sleep(1)
        else:
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
        #self.drawing_name = 'frying pan'
        self.drawing_object = self._qd.get_drawing(self.drawing_name)
        self.image_loaded()

    def on_enter_idle(self):
        if self._sim:
            log.info("SIMULATION sleeping")
            sleep(1)
        else:
            # Move back to home
            self._ad.moveto(0, 0)
            self._ad.disconnect()

    def on_enter_drawing(self):
        if self._sim:
            log.info("SIMULATION sleeping")
            sleep(10)
        else:
            self._draw_pic(self.drawing_object)
        self.drawing_complete()

    def on_enter_final_guessing(self):
        self.guess_timeout()

    def on_enter_completing(self):
        self.drawing_name = None
        self.drawing_object = None
        if not self._sim:
            self._ad.options.speed_pendown = 75
            self._ad.options.speed_penup = 100
            self._ad.options.units = 2
            self._ad.update()

        self.completed()

    def _draw_pic(self, drawing):
        self._ad.options.speed_pendown = PEN_SLOW
        self._ad.options.speed_penup = 100
        self._ad.options.units = 2
        self._ad.update()
        draw_pic_from_drawing(self._ad, drawing)
