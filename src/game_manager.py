from transitions import Machine
import logging
from quickdraw import QuickDrawData
from pyaxidraw.axidraw import AxiDraw

log = logging.getLogger(__name__)


class GameManager:
    """Handles the game's states and invokes AxiDraw commands"""

    states = ["stopped", "started"]

    def __init__(self):
        # Initialize the state machine
        self._machine = Machine(model=self, states=GameManager.states, initial="stopped")

        # Add state transitions
        self._machine.add_transition(trigger="start", source="stopped", dest="started")
        self._machine.add_transition(trigger="stop", source="started", dest="stopped")

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

    def on_enter_stopped(self):
        # TODO: Clean up, lift up pen, etc
        # Move back to home
        self._ad.moveto(0,0)
        self._ad.disconnect()
    def moveto(self,x,y):
        """
        For tests.

        """
        self._ad.moveto(x,y)