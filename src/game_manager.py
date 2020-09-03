from transitions import Machine
import logging
from quickdraw import QuickDrawData

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
        self._qd = QuickDrawData()

    def on_enter_started(self):
        self._qd.get_drawing("hamburger")

    def on_enter_stopped(self):
        pass
