import datetime
from functools import partial

from kivy.clock import Clock

from constants import BERTEC_SPEED_STOP, BERTEC_ACC_LEFT, BERTEC_ACC_RIGHT, SUBTRIAL_MAX, MIN_WAIT_JND, FILENAME_FORMAT_LESS_EXT, DETROIT_TIMEZONE, DATETIME_FORMAT_LESS_SEC

from gui_files.shared_screens import check_batteries
from shared_files.filing_cabinet_regex import build_filename


def initialize_comparison(sm, dt):
    sm.statemachine.subtrial_limit = False
    sm.statemachine.next_comparison()

def subtrial_timelimit(sm, dt):
    sm.statemachine.subtrial_limit = True

def splitsameschedule(sm):
    Clock.schedule_once(partial(initialize_comparison, sm), 0)
    Clock.schedule_once(partial(subtrial_timelimit, sm), SUBTRIAL_MAX/sm.squeeze)
    if sm.allow_check_batteries:
        Clock.schedule_once(partial(check_batteries, sm), SUBTRIAL_MAX/sm.squeeze)


def pause_exo_bertec(sm, dt):
    # Stop bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)

    # Pause exoboots
    sm.exoboot_remote.set_pause(mybool=True)

    # Stop exo logging
    sm.exoboot_remote.set_log(mybool=True)

    # Stop Vicon
    sm.vicon.stop_recording()

def trial_ready(sm, dt):
    # Start Vicon
    suffix = "walk{}".format(sm.statemachine.walknum)
    recording_name = build_filename(
            format=FILENAME_FORMAT_LESS_EXT,
            PREFIX=sm.file_prefix,
            DATE=sm.current_date,
            SUFFIX=suffix,
        )

    start_recording_stamp = datetime.datetime.now(tz=DETROIT_TIMEZONE).strftime(DATETIME_FORMAT_LESS_SEC)
    notes = f"Current date: {sm.current_date}. Start recording date: {start_recording_stamp}"
    sm.vicon.start_recording(fileNameIn=recording_name, notes=notes)

    # Start exo logging
    sm.exoboot_remote.set_log(mybool=False)

    sm.statemachine.next_screen()

def waitingscreenjndschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(trial_ready, sm), MIN_WAIT_JND/sm.squeeze)


def finishscreenjndschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
