# importing widgets from kivy
from kivy.app import App
from kivy.uix.slider import Slider
from kivy.uix.label import Widget
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayoutException
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex

import numpy as np
import time
import csv
from functools import partial
from typing import Type
import random

from constants import *

from vas_schedules import waitingscreevasschedule, finishscreenvasschedule

def startbttnvas_CB(instance):
    sm = instance.parent.parent
    # Set bertec speed
    sm.bertec.write_command(BERTEC_SPEED_RIGHT, BERTEC_SPEED_LEFT, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    # Unpause exoboots
    sm.exoboot_remote.set_pause(mybool=False)
    # Next screen
    sm.statemachine.next_screen()

def buildpushtostartscreenvas():
    screen_= Screen(name="pushtostartscreen")
    startbttn = Button(text="Touch to begin", font_size='50', color=(1, 1, 1, 1), size_hint=(3/4,3/4), pos_hint={'x':1/8,'y':1/8})
    startbttn.bind(on_press=startbttnvas_CB)
    screen_.add_widget(startbttn)

    return screen_


def buildwaitingscreenvas(sm):
    screen = Screen(name="waitingscreenvas")
    screen.sm = sm
    waitlabel = Label(text="Take a break!\nTrial resumes in 2 minute", font_size='50', color=(1, 1, 1, 1))
    screen.add_widget(waitlabel)

    screen.on_enter = partial(waitingscreevasschedule, sm)

    return screen


def onslidermotion(instance, mvalue):
    sm = instance.parent.parent

    min = instance.min
    max = instance.max

    size_x, _ = instance.size_hint

    x_pos = (mvalue - min) / (max - min) * size_x + instance.pos_hint['x']
    y_pos = instance.label.pos_hint['y']
    instance.label.pos_hint = {'x': x_pos, 'y':y_pos}
    instance.label.text = f"${round(mvalue, 2)}"

    sm.statemachine.log_overtime(instance.torque, mvalue)

def buildsliders(sm, screen, sliders_origin={'x':0, 'y':0}, sliders_size=(0, 0), ranked=None, slider_min=NPO_MV, slider_max=EPO_MV):
    num_sliders = sm.statemachine.current_btn_option

    if ranked:
        ranked_ = ranked.copy()

    for i in range(num_sliders):
        # Slider position
        origin_x = sliders_origin[0]
        origin_y = i / num_sliders * sliders_size[1] + sliders_origin[1]
        size_x = sliders_size[0]
        size_y = 1/num_sliders * sliders_size[1]

        # Load existing slider attributes
        if ranked:
            torque, mv, btntext = ranked_.pop()
        else:
            torque = sm.statemachine.get_torque(i)
            mv = 0
            btntext = chr(65 + num_sliders - i - 1)

        slider = Slider(min=slider_min, max=slider_max, value=float(mv), size_hint=(size_x, size_y), pos_hint={'x': origin_x, 'y':origin_y}, cursor_size=(65, 65), padding=0)
        slider.btntext = btntext
        slider.torque = float(torque)
        slider.bind(value=onslidermotion)

        # Create the cursor label and initially set the opacity to 0
        label = Label(text=f"${round(slider.value, 2)}", size_hint=(0.1, 0.1), pos_hint={'x': origin_x, 'y':origin_y}, color=(1.0,0,0))
        slider.label = label

        # Add the labels and the slider to the BoxLayout
        screen.add_widget(label)
        screen.add_widget(slider)

def disable_btns(screen, mybool, dt):
    for btn in screen.children:
        if isinstance(btn, Button) and btn.signature == 0:
            btn.disabled = mybool

def btnpress(instance):
    sm = instance.parent.parent
    screen = instance.parent

    disable_btns(screen, True, 0)
    Clock.schedule_once(partial(disable_btns, screen, False), 0.1)

    sm.exoboot_remote.set_torques(peak_torque_left=instance.torque, peak_torque_right=instance.torque)
    instance.visited = True
    instance.background_color = (0,0,0.75)

    if screen.prev_btn:
        screen.prev_btn.background_color = (0, 0.75, 0)
    screen.prev_btn = instance

    if screen.confirm_btn.disabled:
        for btn in screen.children:
            if isinstance(btn, Button) and btn.signature == 0:
                if not btn.visited:
                    return
        screen.confirm_btn.disabled = False

def buildbtns(sm, screen, buttons_origin, buttons_size, ranked=None):
    num_buttons = sm.statemachine.current_btn_option

    if ranked:
        ranked_ = ranked.copy()

    for i in range(num_buttons):
        # Button Position
        origin_x = buttons_origin[0]
        origin_y = i / num_buttons * buttons_size[1] + buttons_origin[1]
        size_x = buttons_size[0]
        size_y = 1/num_buttons * buttons_size[1]

        # Load existing button attributes
        if ranked:
            torque, _, btntext = ranked_.pop()
        else:
            torque = sm.statemachine.get_torque(i)
            btntext = chr(65 + num_buttons - i - 1)

        btn = Button(text='', font_size='50', color=(1,1,1), background_normal='', background_color= (0,0.5,0), size_hint=(size_x, size_y), pos_hint={'x': origin_x, 'y': origin_y})
        btn.text = btntext
        btn.bind(on_press=btnpress)
        btn.torque = torque
        btn.signature = 0 # Is a torque button
        btn.visited = False
        screen.add_widget(btn) 

def confirmranking(instance):
    sm = instance.parent.parent
    screen = instance.parent

    if instance.confirmed:
        torques = []
        values = []
        for slider in screen.children:
            if isinstance(slider, Slider):
                torques.append(slider.torque)
                values.append(slider.value)

        sm.statemachine.presentation_result(torques, values)
        sm.statemachine.next_screen()
    else:
        instance.confirmed = True

        unranked_torques = []
        unranked_mvs = []
        unranked_text = []
        for slider in screen.children:
            if isinstance(slider, Slider):
                unranked_torques.append(slider.torque)
                unranked_mvs.append(slider.value)
                unranked_text.append(slider.btntext)

        ranked = [[t, mv, txt] for mv, t, txt in sorted(zip(unranked_mvs, unranked_torques, unranked_text))]
        ranked = ranked[::-1]

        buildvasscreen(sm, screen, confirmed=True, ranked=ranked)


def buildvasscreen(sm, screen, confirmed=False, ranked=None):
    screen.clear_widgets()
    screen.sm = sm
    if not confirmed:
        sm.statemachine.next_trial_pres()

    # Layout params
    screen.sliders_origin = (1/10, 1/10)
    screen.sliders_size = (6/10, 9/10)

    screen.buttons_origin = (8/10, 1/10)
    screen.buttons_size = (2/10, 9/10)

    confirm_btn_origin = {'x': 0, 'y': 0}
    confirm_btn_size = (1, 1/10)

    mv_label_size = (1/10, 9/10)

    # Confirm Button
    confirm_btn = Button(text='', font_size='50', color=(1,1,1), background_normal='', background_color=get_color_from_hex('#004B8D'), size_hint=confirm_btn_size, pos_hint=confirm_btn_origin)
    confirm_btn.text = "Confirm" if not confirmed else "Finish"
    confirm_btn.signature = 1
    confirm_btn.confirmed = confirmed
    confirm_btn.disabled = True
    confirm_btn.bind(on_press=confirmranking)
    screen.confirm_btn = confirm_btn

    # NPO/EPO Text
    # Label(text=f"${round(slider.value, 2)}", size_hint=(0.1, 0.1), pos_hint={'x': origin_x, 'y':origin_y}, color=(1.0,0,0))
    npo_label = Label(text="${}".format(NPO_MV), font_size='30', color=(1, 1, 1), size_hint=mv_label_size, pos_hint={'x': 0, 'y': 1/10})
    epo_label = Label(text="${}".format(EPO_MV), font_size='30', color=(1, 1, 1), size_hint=mv_label_size, pos_hint={'x': 7/10, 'y': 1/10})

    buildsliders(sm, screen, sliders_origin=screen.sliders_origin, sliders_size=screen.sliders_size, ranked=ranked, slider_min=NPO_MV, slider_max=EPO_MV)

    buildbtns(sm, screen, screen.buttons_origin, screen.buttons_size, ranked=ranked)
    screen.prev_btn = 0

    screen.add_widget(confirm_btn)
    screen.add_widget(npo_label)
    screen.add_widget(epo_label)


def buildfinishscreenvas(sm):
    screen = Screen(name="finishscreenvas")
    screen.sm = sm

    finishlabel = Label(text="Trial Finished\nPlease step off the treadmill", font_size='50', color=(1, 0, 0, 1))
    screen.add_widget(finishlabel)

    screen.on_enter = partial(finishscreenvasschedule, sm)

    return screen
