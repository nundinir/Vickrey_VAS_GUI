import random
from functools import partial
from kivy.clock import Clock

from constants import *


def pause_exo_bertec(sm, dt):
    """
    Stop Bertec, pause exoboot actuation and logging, stop Vicon recording
    """
    # Bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    
    # Exoboots
    sm.exoboot_remote.set_torques(peak_torque_left=0, peak_torque_right=0)
    sm.exoboot_remote.set_pause(mybool=True)
    sm.exoboot_remote.set_log(mybool=True)

    # Vicon
    sm.vicon.stop_recording()


def waitingscreenprefschedule(sm):
    """
    What happens during waiting screen
    Enforces a minimum wait time before subject can start the next round
    """
    # Functions
    def trial_ready(sm, dt):
        # Start Vicon/Exoboot logging
        recording_name = "{}_walk{}".format(sm.file_prefix, sm.statemachine.pres)
        sm.vicon.start_recording(recording_name)
        sm.exoboot_remote.set_log(mybool=False)
        sm.statemachine.next_screen()

    # Kivy Clock Scheduling
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
    Clock.schedule_once(partial(trial_ready, sm), MIN_WAIT_PREF/sm.squeeze)


def walksreenprefschedule(sm):
    """
    Have subject walk after choosing preferred torque, then report the torque
    Only for SLIDER and BUTTON
    """
    pref_type = sm.statemachine.pref_type
    if pref_type == "SLIDER":
        torque = sm.prefscreen.tslider.value
    elif pref_type == "BUTTON":
        torque = sm.prefscreen.prev_btn.torque
    else:
        print("NOT A VALID in walkscreenprefschedule")

    Clock.schedule_once(partial(sm.statemachine.report_pref, torque), MANDATORY_WALK_PREF/sm.squeeze)


def prefmandatorywalk(sm):
    """
    Start mandatory walk period after subject has chosen their preferred torque for the round
    """
    def setmandatorywalktext(sm ,dt):
        if MANDATORY_WALK_PREF/sm.squeeze < 60:
            walktext = "Continue walking for {} seconds".format(int(MANDATORY_WALK_PREF/sm.squeeze))
        else:
            walktext = "Continue walking for {:0.1f} minutes".format(MANDATORY_WALK_PREF/sm.squeeze/60)
        sm.prefscreen.confirm_btn.text = walktext
        sm.prefscreen.confirm_btn.background_color = (0, 1, 1)

    def reportprefandcleanup(sm, dt):
        # Report preferred torque
        torque = sm.prefscreen.dial.torque_value
        print(f'Confirmed torque is: {torque}')
        sm.statemachine.report_pref(torque)

        # Randomize the starting torque value of the preference dial during the disable period
        rand_start_torque = random.uniform(TORQUE_MIN, TORQUE_MAX/2)
        sm.prefscreen.dial.torque_value = rand_start_torque
        print("Randomizing dial start torque: {}".format(rand_start_torque))

    # Kivy Clock Scheduling
    Clock.schedule_once(partial(setmandatorywalktext, sm), 0) 
    Clock.schedule_once(partial(reportprefandcleanup, sm), MANDATORY_WALK_PREF/sm.squeeze)


def prefscreenschedule(sm):
    """
    What happens during preference screen
    Unpauses exoboots to begin
    """
    def reset_prefscreen(sm, dt):
        sm.prefscreen.confirm_btn.confirmed = False
        if sm.statemachine.pref_type == "DIAL":
            sm.prefscreen.confirm_btn.lock = False
        sm.prefscreen.confirm_btn.text = "Confirm"
        sm.prefscreen.confirm_btn.background_color = (0.75, 0, 0)

    def trial_start(sm, dt):
        sm.exoboot_remote.set_pause(mybool=False)
    
    # Kivy Clock Scheduling
    Clock.schedule_once(partial(reset_prefscreen, sm), 0)
    Clock.schedule_once(partial(trial_start, sm), 0)


def finishscreenprefschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
