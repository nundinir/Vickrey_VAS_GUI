from functools import partial

from kivy.clock import Clock

import random

from constants import *
from shared_files.filing_cabinet_regex import build_filename


def pause_exo_bertec(sm, dt):
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)

    # 0 Torque/Pause exoboots
    sm.exoboot_remote.set_torques(peak_torque_left=0, peak_torque_right=0)
    sm.exoboot_remote.set_pause(mybool=True)
    sm.exoboot_remote.set_log(mybool=True)

    # Stop Vicon
    sm.vicon.stop_recording()

def trial_ready(sm, dt):
    # Start Vicon
    suffix = "walk{}".format(sm.statemachine.pres)
    recording_name = build_filename(
            FORMAT=FILENAME_FORMAT_LESS_EXT,
            PREFIX=sm.file_prefix,
            DATE=sm.current_date,
            SUFFIX=suffix,
        )

    start_recording_stamp = datetime.datetime.now(tz=DETROIT_TIMEZONE).strftime(DATETIME_FORMAT_LESS_SEC)
    file_description = f"Current date:{sm.current_date}. Start recording date:{start_recording_stamp}"
    sm.vicon.start_recording(fileNameIn=recording_name, fileDescription=file_description)

    # Start logging
    sm.exoboot_remote.set_log(mybool=False)

    sm.statemachine.next_screen()

def waitingscreenprefschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(trial_ready, sm), MIN_WAIT_PREF/sm.squeeze)


def walksreenprefschedule(sm):
    Clock.schedule_once(sm.statemachine.next_screen, WALK_TIME_PREF/sm.squeeze)


def trial_start(sm, dt):
    sm.exoboot_remote.set_pause(mybool=False)

def prefscreenschedule(sm):
    Clock.schedule_once(partial(trial_start, sm), 0)


def reset_sliderscreen(sm, screen):
    screen.confirm_btn.confirmed = False
    screen.confirm_btn.text = "Confirm"


def finishscreenprefschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
