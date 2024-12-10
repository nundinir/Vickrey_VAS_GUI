from functools import partial

from kivy.clock import Clock

from constants import *
from gui_files.shared_screens import check_batteries


def pause_exo_bertec(sm, dt):
    # Stop bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    # Pause exoboots
    sm.exoboot_remote.set_pause(mybool=True)
    # Stop exo logging
    sm.exoboot_remote.set_log(mybool=True)
    # Stop Vicon
    sm.vicon.stop_recording()

def next_presentation(sm, dt):
    # Start Vicon
    b, t, p = sm.statemachine.peak_btp()
    recording_name = "{}_B{}_T{}_P{}".format(sm.file_prefix, b, t, p)
    sm.vicon.start_recording(recording_name)

    # Start exo logging
    sm.exoboot_remote.set_log(mybool=False)

    # Go to next screen
    sm.statemachine.next_screen()

def waitingscreevasschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(next_presentation, sm), MIN_WAIT_VAS/sm.squeeze)


def vasscreenschedule(sm):
    if sm.allow_check_batteries:
        Clock.schedule_once(partial(check_batteries, sm), 0)


def finishscreenvasschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
