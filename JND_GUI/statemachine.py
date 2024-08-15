from constants import *
from Robobidders import *

# Statemachine class
class JNDStateMachine:
    def __init__(self, screenmanager):
        self.sm = screenmanager

        # JND Params
        self.torque_delta = 0
        self.higher_side = 'None'

        # Screen states
        self.next_screen_dict = {"dummy": "pushtostartscreen", 
                                 "pushtostartscreen": "leftorright"
                                 }

    def send_treadmill_msg(self, state):
        self.sm.callergrpc.treadmill_message(state)

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        self.sm.current = self.next_screen_dict[self.sm.current]