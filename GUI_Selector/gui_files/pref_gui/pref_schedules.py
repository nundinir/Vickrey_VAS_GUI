from functools import partial

from kivy.clock import Clock

from constants import BERTEC_SPEED_STOP, BERTEC_ACC_LEFT, BERTEC_ACC_RIGHT, SUBTRIAL_MAX, MIN_WAIT_PREF


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
    recording_name = "{}_walk{}".format(sm.file_prefix, sm.statemachine.pres)
    sm.vicon.start_recording(recording_name)

    # Start logging
    sm.exoboot_remote.set_log(mybool=False)

    sm.statemachine.next_screen()

def waitingscreenprefschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(trial_ready, sm), MIN_WAIT_PREF)


def trial_start(sm, dt):
    sm.exoboot_remote.set_pause(mybool=False)

def prefscreenschedule(sm):
    Clock.schedule_once(partial(trial_start, sm), 0)


def reset_sliderscreen(sm, screen):
    screen.confirm_btn.confirmed = False
    screen.confirm_btn.text = "Confirm"

def finishscreenprefschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
