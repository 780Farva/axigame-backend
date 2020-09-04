import logging
import random

from pyaxidraw.axidraw import AxiDraw
from quickdraw import QuickDrawData
from transitions.extensions.asyncio import AsyncMachine
from transitions import Machine
from utils import _reshape_strokes, draw_pic_from_drawing
from time import sleep, time
import numpy as np
from itertools import product

log = logging.getLogger(__name__)
PEN_SLOW = 5
MAXGAMES = 12


def _get_grid(scale=6):
    # Odd number of games
    x_dim = 300  # Total dim
    y_dim = 200  # Total dim
    # Max coordinates are 255, hence the size will be 255m / scale
    size_pic = 255 / scale  # 42 mm
    centers_x = np.linspace(0, x_dim, np.int64(np.floor(x_dim / size_pic)))[:-1]
    centers_y = np.linspace(0, y_dim, np.int64(np.floor(y_dim / size_pic)))[:-1]
    # Product of these centers will be reference points:
    grid = list(product(centers_x, centers_y))
    return grid


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
            "trigger": "correct_guess_late",
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
        self.time = None
        self.not_guessed = True
        self.game_count = 0
        self.scale = 6
        self.flag = False
        self.grid = _get_grid(self.scale + 1)

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
        # self.drawing_name = random.choice(self._qd.drawing_names)
        self.drawing_name = 'anvil'
        self.drawing_object = self._qd.get_drawing(self.drawing_name)
        self.image_loaded()

    def on_enter_idle(self):
        if self._sim:
            log.info("SIMULATION sleeping")
            sleep(1)
        else:
            # Move back to home
            print('----Moving home!')
            self._ad.moveto(0, 0)
            self._ad.disconnect()

    def on_enter_drawing(self):
        self.time = time()
        if self._sim:
            log.info("SIMULATION sleeping")
            sleep(10)
        else:
            self._draw_pic(self.drawing_object)
        self.drawing_complete()

    def on_enter_final_guessing(self):
        # Failed to guess here
        self.guess_timeout()

    def on_enter_completing(self):
        print(f'The drawing was: {self.drawing_name}')
        self.drawing_name = None
        self.drawing_object = None

        self.completed()

    def flag_callback(self):
        tmp = self.flag
        if self.flag:
            print('---------------Flag was True, setting to False...')
            self.flag = False
        return tmp

    def _draw_pic(self, drawing):
        self._ad.options.speed_pendown = PEN_SLOW
        self._ad.options.speed_penup = 100
        self._ad.options.units = 2
        self._ad.update()
        self.is_drawing = True
        xy = random.choice(self.grid)
        draw_pic_from_drawing(self._ad, drawing, scale=self.scale,
                              reference_xy=xy, flag_callback=self.flag_callback)
        self.is_drawing = False
