from functools import partial

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from constants import *
from vickrey_schedules import *
from kivy_utils import CountDownTimer

def startbtn_CB(instance):
    sm = instance.parent.parent

    sm.bertec.write_command(BERTEC_SPEED_RIGHT, BERTEC_SPEED_LEFT, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    sm.exoboot_remote.set_pause(mybool=False)
    sm.exoboot_remote.set_torques(peak_torque_left=0, peak_torque_right=0)
    
    sm.statemachine.next_screen()

def report_higher(instance):
    sm = instance.parent.parent

    sm.statemachine.report_higher(instance.signature)

def buildpushtostartscreenjnd(sm):
    screen_ = Screen(name="pushtostartscreenjnd")
    screen_.sm = sm
    startbttn = Button(text="Touch to begin", font_size='50', color=(1, 1, 1, 1))
    startbttn.bind(on_press=startbtn_CB)
    screen_.add_widget(startbttn)

    return screen_

def buildsplitlegscreen(sm):
    screen_ = Screen(name="splitlegscreen")
    screen_.sm = sm

    leftbtn = Button(text="Left", font_size='70', color = (1,1,1), background_normal='', background_color= (0,1.0,0), size_hint=(1/2, 1), pos_hint={'x':0, 'y':0})
    leftbtn.signature = 0
    leftbtn.bind(on_press=report_higher)
    screen_.add_widget(leftbtn)

    rightbtn = Button(text="Right", font_size='70', color = (1,1,1), background_normal='', background_color= (1.0,0,0), size_hint=(1/2, 1), pos_hint={'x':1/2, 'y':0})
    rightbtn.signature = 1
    rightbtn.bind(on_press=report_higher)
    screen_.add_widget(rightbtn)

    screen_.on_enter = partial(survey_schedule,sm)

    return screen_