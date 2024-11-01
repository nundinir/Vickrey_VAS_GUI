from functools import partial

from kivy.clock import Clock

from constants import *


def pause_exo_bertec(sm, dt):
    # Stop bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    
    # Pause exoboots
    sm.exoboot_remote.set_pause(mybool=True)


def waitingscreevasschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(sm.statemachine.next_screen, MIN_WAIT_VAS)


def finishscreenvasschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
