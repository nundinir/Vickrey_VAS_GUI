from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from constants import *
from jnd_schedules import splitsameschedule, waitingscreenjndschedule, finishscreenjndschedule
from kivy_utils import CountDownTimer


def startbtn_CB(instance):
    sm = instance.parent.parent
    # Set bertec speed
    sm.bertec.write_command(BERTEC_SPEED_RIGHT, BERTEC_SPEED_LEFT, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    # Unpause exoboots
    sm.exoboot_remote.set_pause(mybool=False)
    # Next screen
    sm.statemachine.next_screen()

def buildpushtostartscreenjnd(sm):
    screen = Screen(name="pushtostartscreenjnd")
    screen.sm = sm
    startbttn = Button(text="Touch to begin", font_size='50', color=(1, 1, 1, 1))
    startbttn.bind(on_press=startbtn_CB)
    screen.add_widget(startbttn)

    return screen


def buildwaitingscreenjnd(sm):
    screen = Screen(name="waitingscreenjnd")
    screen.sm = sm
    waitlabel = Label(text="Take a break!\nTrial resumes in 1 minute", font_size='50', color=(1, 1, 1, 1))
    screen.add_widget(waitlabel)
    
    screen.on_enter = partial(waitingscreenjndschedule, sm)

    return screen


def disable_btns(screen, mybool, dt):
    for btn in screen.children:
        btn.disabled = mybool

def report_higher(instance):
    screen = instance.parent
    disable_btns(screen, True, 0)
    Clock.schedule_once(partial(disable_btns, screen, False), 0.1)

    sm = instance.parent.parent
    sm.statemachine.report_higher(instance.signature)

def buildsplitlegscreen(sm):
    screen = Screen(name="splitlegscreen")
    screen.sm = sm

    leftbtn = Button(text="Left", font_size='70', color = (1,1,1), background_normal='', background_color= (0,1.0,0), size_hint=(1/2, 1), pos_hint={'x':0, 'y':0})
    leftbtn.signature = 0
    leftbtn.bind(on_press=report_higher)
    screen.add_widget(leftbtn)

    rightbtn = Button(text="Right", font_size='70', color = (1,1,1), background_normal='', background_color= (1.0,0,0), size_hint=(1/2, 1), pos_hint={'x':1/2, 'y':0})
    rightbtn.signature = 1
    rightbtn.bind(on_press=report_higher)
    screen.add_widget(rightbtn)

    screen.on_enter = partial(splitsameschedule,sm)

    return screen


def swap_torques(instance):
    sm = instance.parent.parent
    stma = sm.statemachine
    # Flip Flop
    stma.peak_torque_ind = 1 - stma.peak_torque_ind
    # Command peak torque
    sm.exoboot_remote.set_torques(peak_torque_left=stma.peak_torques[stma.peak_torque_ind], peak_torque_right=stma.peak_torques[stma.peak_torque_ind])

def confirm_answer(instance):
    screen = instance.parent
    disable_btns(screen, True, 0)
    Clock.schedule_once(partial(disable_btns, screen, False), 0.1)

    sm = instance.parent.parent
    sm.statemachine.report_higher()

def buildsamelegscreen(sm):
    screen = Screen(name="samelegscreen")
    screen.sm = sm

    swap_btn = Button(text="Swap Torques", font_size='70', color = (1,1,1), background_normal='', background_color= (0,1,1), size_hint=(1, 2/3), pos_hint={'x':0, 'y':1/3})
    swap_btn.bind(on_press=swap_torques)
    screen.add_widget(swap_btn)

    answer_btn = Button(text="Confirm", font_size='70', color = (1,1,1), background_normal='', background_color= (1,0,0), size_hint=(1, 1/3), pos_hint={'x':0, 'y':0})
    answer_btn.bind(on_press=confirm_answer)
    screen.add_widget(answer_btn)

    screen.on_enter = partial(splitsameschedule, sm)

    return screen


def buildfinishscreenjnd(sm):
    screen = Screen(name="finishscreenjnd")
    screen.sm = sm
    finishlabel = Label(text="Trial Finished\n Please step off the treadmill", font_size='50', color=(1, 1, 1, 1))
    screen.add_widget(finishlabel)

    screen.on_enter = partial(finishscreenjndschedule, sm)

    return screen
