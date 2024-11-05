from functools import partial

from kivy.clock import Clock

from constants import *


def pause_exo_bertec(sm, dt):
    """
    Stop bertec, exoboots, logging, vicon
    """
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    sm.exoboot_remote.set_pause(mybool=True)
    sm.exoboot_remote.set_log(mybool=True)
    sm.vicon.stop_recording()

def loggingvicon_event(sm, dt):
    """
    Start logging/Vicon
    """
    b, t, p = sm.statemachine.peak_btp()
    sm.exoboot_remote.newpres(b, t, p)
    sm.exoboot_remote.set_log(mybool=False)
    
    btpname = "{}_B{}_T{}_P{}".format(sm.file_prefix, b, t, p)
    sm.vicon.start_recording(btpname)

def waitingscreevasschedule(sm):
    """
    Waiting screen events and timings    
    """
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(loggingvicon_event, sm), MIN_WAIT_VAS)
    Clock.schedule_once(sm.statemachine.next_screen, MIN_WAIT_VAS)


def finishscreenvasschedule(sm):
    """
    Finish screen event and timings
    """
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
