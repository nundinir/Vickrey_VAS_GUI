import random
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from constants import *
from gui_files.speedfinder_gui.speedfinder_schedules import finishscreensfschedule, speedfinderschedule

def startbtn_CB(instance):
    sm = instance.parent.parent
    # Set bertec speed
    sm.bertec.write_command(BERTEC_SPEED_RIGHT, BERTEC_SPEED_LEFT, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    # Unpause exoboots
    sm.exoboot_remote.set_pause(mybool=False)
    # Next screen
    sm.statemachine.next_screen()

def buildpushtostartscreensf():
    screen = Screen(name="pushtostartscreensf")
    startbttn = Button(text="Touch to begin", font_size='50', color=(1, 1, 1, 1), size_hint=(3/4,3/4), pos_hint={'x':1/8,'y':1/8})
    startbttn.bind(on_press=startbtn_CB)
    screen.add_widget(startbttn)

    return screen


def disable_btn(screen, mybool, dt):
    screen.finish_btn.disabled = mybool

def onslidermotion(instance, torque):
    # Reset confirm button
    if instance.parent.finish_btn.confirmed:
        instance.parent.finish_btn.confirmed = False
        instance.parent.finish_btn.background_color = (0.75,0,0)
        instance.parent.finish_btn.text = "Confirm"

    sm = instance.parent.parent
    torque = instance.parent.tslider.value
    sm.exoboot_remote.set_torques(peak_torque_left=torque, peak_torque_right=torque)

def confirm_slider_accl(instance):
    if instance.confirmed:
        sm = instance.parent.parent
        sm.statemachine.next_screen()
    else:
        instance.confirmed = True
        instance.background_color = (1,0,0)
        instance.text = "ARE YOU SURE?"

        screen = instance.parent
        disable_btn(screen, True, 0)
        Clock.schedule_once(partial(disable_btn, screen, False), 0.2)

def buildspeedfinderscreen(sm):
    screen = Screen(name="speedfinderscreen")
    screen.sm = sm

    finishlabel = Label(text="Finding speed. Treadmill speed will vary.", font_size='70', color=(1, 1, 1, 1))
    screen.add_widget(finishlabel)

    screen.on_enter = partial(speedfinderschedule, sm)

    return screen


def buildfinishscreensf(sm):
    screen = Screen(name="finishscreensf")
    screen.sm = sm

    finishlabel = Label(text="Experiment Finished\nPlease step off the treadmill", font_size='70', color=(1, 0, 0, 1))
    screen.add_widget(finishlabel)

    screen.on_enter = partial(finishscreensfschedule, sm)

    return screen
