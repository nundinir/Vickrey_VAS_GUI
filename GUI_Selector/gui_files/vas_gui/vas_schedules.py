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

def update_wait_text(sm, dt):
    # Minimum wait depending on current_btn
    current_btn = sm.statemachine.current_btn_option
    min_wait = MIN_WAIT_VAS[current_btn]

    if min_wait/sm.squeeze < 60:
        waittext = "Take a break!\nTrial resumes in {} seconds".format(int(min_wait/sm.squeeze))
    else:
        waittext = "Take a break!\nTrial resumes in {:0.1f} minutes".format(min_wait/sm.squeeze/60)

    sm.waitingscreen.waitlabel.text = waittext

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
    """
    Waiting screen schedule
    Pause exos, update minimum wait time text, and change screens after minimum wait time has passed
    """
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(update_wait_text, sm), 0)
    Clock.schedule_once(partial(next_presentation, sm), MIN_WAIT_VAS[sm.statemachine.current_btn_option]/sm.squeeze)


def vasscreenschedule(sm):
    if sm.allow_check_batteries:
        Clock.schedule_once(partial(check_batteries, sm), 0)


def finishscreenvasschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
