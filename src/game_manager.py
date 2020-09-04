import logging
import random
from itertools import product
from time import sleep, time

import numpy as np
import requests
from fuzzywuzzy import fuzz
from pyaxidraw.axidraw import AxiDraw
from quickdraw import QuickDrawData
from transitions import Machine

from utils import draw_pic_from_drawing
import urllib

log = logging.getLogger(__name__)
PEN_SLOW = 5
PEN_FAST = 100
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
        "handling_no_guess",
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
        {"trigger": "guess_timeout", "source": "final_guessing", "dest": "handling_no_guess"},
        {"trigger": "no_guess_handled", "source": "handling_no_guess", "dest": "drawing"},
        {"trigger": "give_up", "source": "handling_no_guess", "dest": "completing"},
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
        self.fast_forward_flag = False
        self.guessed_correctly_flag = False
        self.grid = _get_grid(self.scale + 1)
        self._reference_xy = (0, 0)
        self.retry_count = 0

    def on_enter_initializing_axidraw(self):
        if self._sim:
            log.info("SIMULATION sleeping")
            sleep(1)
        else:
            self._ad.interactive()
            self._ad.connect()
            self._ad.options.speed_pendown = PEN_SLOW
            self._ad.options.speed_penup = PEN_FAST
            self._ad.options.units = 2
            self._ad.update()
        self.axidraw_ready()

    def on_enter_loading_image(self):
        # Select a drawing at random
        self.drawing_name = random.choice(self._qd.drawing_names)
        self.drawing_object = self._qd.get_drawing(self.drawing_name)

        self._reference_xy = random.choice(self.grid)
        self.image_loaded()

    def on_enter_idle(self):
        if self._sim:
            log.info("SIMULATION sleeping")
            sleep(1)
        else:
            # Move back to home
            log.info('----Moving home!')
            self._ad.moveto(0, 0)
            self._ad.disconnect()

        self.retry_count = 0

    def on_enter_drawing(self):
        self.time = time()
        if self._sim:
            log.info("SIMULATION sleeping")
            sleep(10)
        else:
            self._draw_pic(self.drawing_object)
            self._ad.moveto(0, 0)
            log.info('----Drawing complete!')

        if self.guessed_correctly_flag:
            self.correct_guess_early()
        else:
            self.drawing_complete()

    def on_enter_final_guessing(self):
        for sleep_second in range(6):
            sleep(0.5)
            if self.guessed_correctly_flag:
                self.correct_guess_late()
                return

        self.guess_timeout()

    def on_enter_handling_no_guess(self):
        self.retry_count += 1
        try:
            hint = ''
            for index, char in enumerate(self.drawing_name):
                if index % self.retry_count + 1:
                    hint = hint.join(char)
                else:
                    hint = hint.join('*')
            log.debug(f"Hint: {hint}")
            response = requests.get(url=f"http://10.20.40.57:5000/noWinner/{urllib.parse.quote(hint)}", timeout=1)
            log.debug(f"No winner response status: {response.status_code}")
        except:
            pass

        # Choose a new drawing and speed up
        self._ad.options.speed_pendown = PEN_FAST
        self._ad.options.speed_penup = PEN_FAST
        self._ad.options.units = 2
        self._ad.update()
        self.drawing_object = self._qd.get_drawing(self.drawing_name)
        if self.retry_count < 3:
            self.no_guess_handled()
        else:
            self.give_up()
            try:
                response = requests.get(url=f"http://10.20.40.57:5000/noWinner/{urllib.parse.quote(self.drawing_name)}",
                                        timeout=1)
                log.debug(f"No winner response status: {response.status_code}")
            except:
                pass

    def on_enter_completing(self):
        log.info(f'The drawing was: {self.drawing_name}')

        self.guessed_correctly_flag = False
        self.drawing_name = None
        self.drawing_object = None

        self.completed()

    def flag_callback(self):
        tmp = self.fast_forward_flag
        if self.fast_forward_flag:
            print('---------------Flag was True, setting to False...')
            self.fast_forward_flag = False
        return tmp

    def _draw_pic(self, drawing):
        self.is_drawing = True
        draw_pic_from_drawing(self._ad, drawing, scale=self.scale,
                              reference_xy=self._reference_xy, flag_callback=self.flag_callback)
        self.is_drawing = False

    def try_guess(self, guess):
        guess = guess.lower()
        truth = self.drawing_name
        log.debug(f"Comparing guess {guess} to truth {truth}.")
        if len(truth.split()) > 1:
            # we have two words, let's guess at least one:
            guessed_correctly = np.any(
                [(fuzz.ratio(truth, word) > 85) for word in truth.split()]
            )
        else:
            guessed_correctly = fuzz.ratio(truth, guess) > 80

        if guessed_correctly:
            # Stop drawing, do next image
            log.info("Correct! Next image...")
            self.fast_forward_flag = True
            self.guessed_correctly_flag = True
        guess_time = time() - self.time
        return guessed_correctly, guess_time
