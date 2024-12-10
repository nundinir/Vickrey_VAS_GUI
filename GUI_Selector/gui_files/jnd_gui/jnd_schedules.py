from functools import partial

from kivy.clock import Clock

from constants import BERTEC_SPEED_STOP, BERTEC_ACC_LEFT, BERTEC_ACC_RIGHT, SUBTRIAL_MAX, MIN_WAIT_JND

from gui_files.shared_screens import check_batteries


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
    recording_name = "{}_walk{}".format(sm.file_prefix, sm.statemachine.walknum)
    sm.vicon.start_recording(recording_name)

    # Start exo logging
    sm.exoboot_remote.set_log(mybool=False)

    sm.statemachine.next_screen()

def waitingscreenjndschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)

    # Increment walknum
    sm.statemachine.walknum += 1

    Clock.schedule_once(partial(trial_ready, sm), MIN_WAIT_JND/sm.squeeze)


def finishscreenjndschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
