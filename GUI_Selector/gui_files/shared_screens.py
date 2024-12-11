from functools import partial

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from constants import *


def pause_exo_bertec(sm, dt):
    # Stop bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    # Pause exoboots
    sm.exoboot_remote.set_pause(mybool=True)
    # Stop exo logging
    sm.exoboot_remote.set_log(mybool=True)
    # Stop Vicon
    sm.vicon.stop_recording()


def check_batteries(sm, dt):
    """
    Check battery voltages
    If lower than BATTV_LOWER_LIM, interrupts gui for battery replacement break
    """
    battv_left = sm.exoboot_remote.getpack("exothread_left", "battery_voltage")/2
    battv_right = sm.exoboot_remote.getpack("exothread_right", "battery_voltage")/2

    print("BATTERY VOLTAGES: {}, {}".format(battv_left, battv_right))

    if battv_left == -1/2 and battv_right == -1/2:
        pass
    elif battv_left < BATTV_LOWER_LIM or battv_right < BATTV_LOWER_LIM:
        sm.batteryscreen.label.text = "BATTERY BREAK\nBATTV LEFT: {:0.2f}\nBATTV RIGHT: {:0.2f}".format(battv_left, battv_right)
        sm.statemachine.queue_screen("batteryscreen")


def buildbatteryscreen(sm):
    """
    Shows battery voltages for each exoboot
    """
    screen = Screen(name="batteryscreen")
    screen.label = Label(text='', font_size='50', color = (1,1,1))
    screen.add_widget(screen.label)
    screen.on_enter = partial(pause_exo_bertec,sm)
    return screen
