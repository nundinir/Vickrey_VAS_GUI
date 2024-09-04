from functools import partial

from kivy.clock import Clock

from constants import *

def vas_schedule(sm):
    
    Clock.schedule_once(partial(map_torques_to_buttons, sm), 0)


def map_torques_to_buttons(sm, dt):
    # trial = sm.trial
    # presentation = sm.presentation
    # TODO implement
    pass

    