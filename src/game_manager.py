
from transitions import Machine

class GameManager:
    """Handles the game's states and invokes AxiDraw commands"""
    states = ['stopped', 'started']
    def __init__(self):
        # Initialize the state machine
        self.machine = Machine(model=self, states=GameManager.states, initial='stopped')

        # Add state transitions
        self.machine.add_transition(trigger='start', source='stopped', dest='started')
        self.machine.add_transition(trigger='stop', source='started', dest='stopped')
