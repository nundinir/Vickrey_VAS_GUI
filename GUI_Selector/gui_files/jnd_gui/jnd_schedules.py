from functools import partial

from kivy.clock import Clock

from constants import BERTEC_SPEED_STOP, BERTEC_ACC_LEFT, BERTEC_ACC_RIGHT, SUBTRIAL_MAX, MIN_WAIT_JND


def initialize_comparison(sm, dt):
    """
    Start walk
    """
    sm.statemachine.subtrial_limit = False
    sm.statemachine.next_comparison()

def subtrial_timelimit(sm, dt):
    """
    End walk after current comparison
    """
    sm.statemachine.subtrial_limit = True

def splitsameschedule(sm):
    """
    JND screen events and timing
    """
    Clock.schedule_once(partial(initialize_comparison, sm), 0)
    Clock.schedule_once(partial(subtrial_timelimit, sm), SUBTRIAL_MAX)


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
    walk = sm.statemachine.incrementwalk()
    sm.exoboot_remote.newwalk(walk)
    sm.exoboot_remote.set_log(mybool=False)

    btpname = "{}_walk{}".format(sm.file_prefix, walk)
    sm.vicon.start_recording(btpname)

def waitingscreenjndschedule(sm):
    """
    Waiting screen events and timing
    """
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(loggingvicon_event, sm), MIN_WAIT_JND)
    Clock.schedule_once(partial(sm.statemachine.next_screen, sm), MIN_WAIT_JND)


def finishscreenjndschedule(sm):
    """
    Finish screen event and timing
    """
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
