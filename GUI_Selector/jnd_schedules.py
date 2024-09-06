from functools import partial

from kivy.clock import Clock

from constants import BERTEC_SPEED_STOP, BERTEC_ACC_LEFT, BERTEC_ACC_RIGHT, SUBTRIAL_MAX, WAITING_MIN

def splitsameschedule(sm):
    Clock.schedule_once(partial(initialize_comparison, sm), 0)
    Clock.schedule_once(partial(subtrial_timelimit, sm), SUBTRIAL_MAX)

def initialize_comparison(sm, dt):
    sm.statemachine.subtrial_limit = False
    sm.statemachine.next_comparison()

def subtrial_timelimit(sm, dt):
    sm.statemachine.subtrial_limit = True


def waitingscreenjndschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(trial_ready, sm), WAITING_MIN)

def pause_exo_bertec(sm, dt):
    # Stop bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    
    # Pause exoboots
    sm.exoboot_remote.set_pause(mybool=True)

def trial_ready(sm, dt):
    sm.statemachine.next_screen()


def finishscreenjndschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
