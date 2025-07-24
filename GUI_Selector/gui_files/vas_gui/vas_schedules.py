from functools import partial

from kivy.clock import Clock

from constants import *
from gui_files.shared_screens import check_batteries
from shared_files.filing_cabinet_regex import build_filename


def pause_exo_bertec_no_vicon(sm, dt):
    # Stop bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)

    # Zero and pause exoboots
    sm.exoboot_remote.set_torques(peak_torque_left=0, peak_torque_right=0)
    sm.exoboot_remote.set_pause(mybool=True)

    # Stop exo logging
    # sm.exoboot_remote.set_log(mybool=True)

def start_exo_bertec_only(sm, dt):
    sm.bertec.write_command(sm.bertec_speed, sm.bertec_speed, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    sm.exoboot_remote.set_pause(mybool=False)
    # sm.exoboot_remote.set_log(mybool=False)

def pause_exo_bertec(sm, dt):
    # Stop bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)

    # Zero and pause exoboots
    sm.exoboot_remote.set_torques(peak_torque_left=0, peak_torque_right=0)
    sm.exoboot_remote.set_pause(mybool=True)

    # Stop exo logging
    sm.exoboot_remote.set_log(mybool=True)

    # Stop Vicon
    sm.vicon.stop_recording()

def update_wait_text(sm, duration, dt):
    if duration/sm.squeeze < 60:
        waittext = "Take a break!\nTrial resumes in {} seconds".format(int(duration))
    else:
        waittext = "Take a break!\nTrial resumes in {:0.1f} minutes".format(duration/60)

    sm.waitingscreen.waitlabel.text = waittext

def next_presentation(sm, b, t, p, dt):
    # Start Vicon
    suffix = "B{}_T{}_P{}".format(b, t, p)
    recording_name = build_filename(
            FORMAT=FILENAME_FORMAT_LESS_EXT,
            PREFIX=sm.file_prefix,
            DATE=sm.current_date,
            SUFFIX=suffix,
        )

    start_recording_stamp = datetime.datetime.now(tz=DETROIT_TIMEZONE).strftime(DATETIME_FORMAT_LESS_SEC)
    file_description = f"Current date:{sm.current_date}. Start recording date:{start_recording_stamp}"
    sm.vicon.start_recording(fileNameIn=recording_name, fileDescription=file_description)

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

    next_b, next_t, next_p = sm.statemachine.peak_btp()
    if next_b == sm.statemachine.current_btn_option:
        next_pres_wait = MIN_WAIT_VAS[sm.statemachine.current_btn_option]/sm.squeeze
    else:
        next_pres_wait = WAIT_BETWEEN_BTNS/sm.squeeze

    Clock.schedule_once(partial(update_wait_text, sm, next_pres_wait), 0)
    Clock.schedule_once(partial(next_presentation, sm, next_b, next_t, next_p), next_pres_wait)


def vasscreenschedule(sm):
    if sm.allow_check_batteries:
        Clock.schedule_once(partial(check_batteries, sm), 0)


def breakscreenvasschedule(sm):
    def resume_vas(sm, dt):
        sm.current = "vasscreen"

    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(resume_vas, sm), VAS_10BTN_BREAK/sm.squeeze)


def finishscreenvasschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
