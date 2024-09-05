from functools import partial

from kivy.clock import Clock

from constants import *

def splitlegschedule(sm):
    Clock.schedule_once(partial(initialize_comparison, sm), 0)

def initialize_comparison(sm, dt):
    sm.statemachine.next_comparison()