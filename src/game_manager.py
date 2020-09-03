from transitions import Machine
import logging
from quickdraw import QuickDrawData
from pyaxidraw.axidraw import AxiDraw

log = logging.getLogger(__name__)


class GameManager:
    """Handles the game's states and invokes AxiDraw commands"""

    states = ["idle", "initializing_axidraw", 'loading_image', 'drawing', 'final_guessing', 'completing']
    transitions = [
        {'trigger': 'start', 'source': 'idle', 'dest': 'initializing_axidraw'},
        {'trigger': 'axidraw_ready', 'source': 'initializing_axidraw', 'dest': 'loading_image'},
        {'trigger': 'image_loaded', 'source': 'loading_image', 'dest': 'drawing'},
        {'trigger': 'correct_guess_early', 'source': 'drawing', 'dest': 'completing'},
        {'trigger': 'drawing_complete', 'source': 'drawing', 'dest': 'final_guessing'},
        {'trigger': 'corrrect_guess_late', 'source': 'final_guessing', 'dest': 'completing'},
        {'trigger': 'guess_timeout', 'source': 'final_guessing', 'dest': 'completing'},
        {'trigger': 'completed', 'source': 'completing', 'dest': 'idle'},
    ]

    def __init__(self):
        # Initialize the state machine
        self._machine = Machine(model=self, states=GameManager.states, transitions=GameManager.transitions, initial="idle")

        # Init the quickdraw api client
        self._qd = QuickDrawData()

        # Init the axidraw client
        self._ad = AxiDraw()

    def on_enter_started(self):
        # Go grab a hamburger
        # TODO: Make this chose a random topic from a group of valid topics
#        self._qd.get_drawing("hamburger")

        # Show some sign of life on the axidraw
        # TODO: Make this start drawing out the hamburger or what have you.
        self._ad.interactive()
        self._ad.connect()
        self._ad.moveto(1,1)

    def on_enter_idle(self):
        # TODO: Clean up, lift up pen, etc
        # Move back to home
        self._ad.moveto(0,0)
        self._ad.disconnect()
    def moveto(self,x,y):
        """
        For tests.

        """
        self._ad.moveto(x,y)