from functools import partial

from kivy.clock import Clock

from constants import BERTEC_SPEED_STOP, BERTEC_ACC_LEFT, BERTEC_ACC_RIGHT, SUBTRIAL_MAX, MIN_WAIT_PREF


def initialize_pref(sm, dt):
    sm.statemachine.initialize_pref()

def prefschedule(sm):
    Clock.schedule_once(partial(initialize_pref, sm), 0)


def pause_exo_bertec(sm, dt):
    # Stop bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    
    # Pause exoboots
    sm.exoboot_remote.set_pause(mybool=True)

def trial_ready(sm, dt):
    sm.statemachine.next_screen()

def waitingscreenprefschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(trial_ready, sm), MIN_WAIT_PREF)


def finishscreenprefschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)

