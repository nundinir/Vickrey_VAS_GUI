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

from gui_files.vas_gui.vas_schedules import vasscreenschedule, waitingscreevasschedule, breakscreenvasschedule, finishscreenvasschedule, pause_exo_bertec_no_vicon, start_exo_bertec_only


def buildpushtostartscreenvas():
    """
    Returns start screen Screen object
    """
    def startbttnvas_CB(instance):
        sm = instance.parent.parent
        sm.bertec.write_command(sm.bertec_speed, sm.bertec_speed, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
        sm.exoboot_remote.set_pause(mybool=False) # Unpause exoboots
        sm.statemachine.next_screen()

    screen_= Screen(name="pushtostartscreen")
    startbttn = Button(text="STOMP then Touch to begin", font_size='80', color=(1, 1, 1, 1), size_hint=(3/4,3/4), pos_hint={'x':1/8,'y':1/8})
    startbttn.bind(on_press=startbttnvas_CB)
    screen_.add_widget(startbttn)
    return screen_


def buildwaitingscreenvas(sm):
    """
    Returns waiting screen Screen object
    """
    screen = Screen(name="waitingscreenvas")
    screen.sm = sm

    screen.waitlabel = Label(text="", font_size='80', color=(1, 1, 1, 1))
    screen.add_widget(screen.waitlabel)

    screen.on_pre_enter = partial(waitingscreevasschedule, sm)
    return screen


def buildvasscreen(sm, screen, confirmed=False, ranked=None, *vargs):
    """
    Returns vas screen Screen object
    """
    def onslidermotion(instance, mvalue):
        """
        Records slider position for overtime logging
        Adjusts MV label position to follow slider
        """
        sm = instance.parent.parent
        size_x, _ = instance.size_hint

        x_pos = (mvalue - instance.min) / (instance.max - instance.min) * size_x + instance.pos_hint['x']
        y_pos = instance.label.pos_hint['y']
        instance.label.pos_hint = {'x': x_pos, 'y':y_pos}
        instance.label.text = f"${round(mvalue, 2)}"

        sm.statemachine.log_overtime(instance.torque, mvalue)

    def buildsliders(sm, screen, sliders_origin={'x':0, 'y':0}, sliders_size=(0, 0), ranked=None, slider_min=0, slider_max=100):
        """
        Create sliders for new presentation or reorder for confirmation
        """
        num_sliders = sm.statemachine.current_btn_option

        for i in range(num_sliders):
            # Slider position
            origin_x = sliders_origin[0]
            origin_y = i / num_sliders * sliders_size[1] + sliders_origin[1]
            size_x = sliders_size[0]
            size_y = 1/num_sliders * sliders_size[1]

            # Load existing slider attributes from largest value to smallest
            if ranked:
                torque, mv, btntext = ranked[i]
            else:
                torque = sm.statemachine.get_torque(i)
                mv = (slider_max + slider_min) / 2
                btntext = chr(65 + num_sliders - i - 1)

            slider = Slider(min=slider_min, max=slider_max, value=float(mv), size_hint=(size_x, size_y), pos_hint={'x': origin_x, 'y':origin_y}, cursor_size=(65, 65), padding=0)
            slider.btntext = btntext
            slider.torque = float(torque)
            slider.bind(value=onslidermotion)

            # Create the cursor label and initially set the opacity to 0
            label = Label(text=f"${round(slider.value, 2)}", font_size='60', size_hint=(0.1, 0.1), pos_hint={'x': origin_x + size_x * (mv-slider_min)/(slider_max-slider_min), 'y': origin_y + size_y/3}, color=(1,1,1))
            slider.label = label

            # Add the labels and the slider to the BoxLayout
            screen.add_widget(label)
            screen.add_widget(slider)

    def disable_btns(screen, mybool, dt):
        for btn in screen.children:
            if isinstance(btn, Button) and btn.signature == 0:
                btn.disabled = mybool

    def btnpress(instance):
        """
        Disable buttons for a short period of time
        Indicate visited/current button with color change
        Enable confirm button if all buttons visited
        """
        sm = instance.parent.parent
        screen = instance.parent

        disable_btns(screen, True, 0)
        Clock.schedule_once(partial(disable_btns, screen, False), 0.1)

        sm.exoboot_remote.set_torques(peak_torque_left=instance.torque, peak_torque_right=instance.torque)
        instance.visited = True
        instance.background_color = (0,0,0.75)

        if screen.prev_btn and instance != screen.prev_btn:
            screen.prev_btn.background_color = (0, 0.75, 0)
        screen.prev_btn = instance

        if screen.confirm_btn.disabled:
            for btn in screen.children:
                if isinstance(btn, Button) and btn.signature == 0:
                    if not btn.visited:
                        return
            screen.confirm_btn.disabled = False

    def buildbtns(sm, screen, buttons_origin, buttons_size, ranked=None):
        """
        Create buttons for new presentation or reorder for confirmation
        """
        num_buttons = sm.statemachine.current_btn_option

        for i in range(num_buttons):
            # Button Position
            origin_x = buttons_origin[0]
            origin_y = i / num_buttons * buttons_size[1] + buttons_origin[1]
            size_x = buttons_size[0]
            size_y = 1/num_buttons * buttons_size[1]

            # Load existing button attributes
            if ranked:
                torque, _, btntext = ranked[i]
            else:
                torque = sm.statemachine.get_torque(i)
                btntext = chr(65 + num_buttons - i - 1)

            btn = Button(text='', font_size='120', color=(1,1,1), background_normal='', background_color= (0,0.5,0), size_hint=(size_x, size_y), pos_hint={'x': origin_x, 'y': origin_y})
            btn.text = btntext
            btn.bind(on_press=btnpress)
            btn.torque = torque
            btn.signature = 0 # Is a torque button
            btn.visited = False
            screen.add_widget(btn) 

    def confirmranking(instance):
        """
        Confirm button behavior
        Reorders presentation on first confirmation
        Finishes presentation on second confirmation
        """
        sm = instance.parent.parent
        screen = instance.parent

        # Skips confirmation for 1btn
        if instance.confirmed or sm.statemachine.current_btn_option == 1:
            # Second confirmation
            torques = []
            values = []
            for slider in screen.children:
                if isinstance(slider, Slider):
                    torques.append(slider.torque)
                    values.append(slider.value)

            sm.statemachine.presentation_result(torques, values)
            sm.statemachine.next_screen()
        else:
            # First confirmation
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

            if sm.statemachine.current_btn_option == 10:
                # Fake waiting screen for 10 btn
                pause_exo_bertec_no_vicon(sm, None)

                # Create fake waiting screen
                screen.clear_widgets()
                min_wait = VAS_10BTN_BREAK/sm.squeeze
                if min_wait/sm.squeeze < 60:
                    waittext = "Take quick break!\nTrial resumes in {} seconds".format(int(min_wait))
                else:
                    waittext = "Take quick break!\nTrial resumes in {:0.1f} minutes".format(min_wait/60)

                breaklabel = Label(text=waittext, font_size='100', color=(0, 0.2, 1, 1))
                screen.add_widget(breaklabel)

                # Resume 10 Btn presentation
                Clock.schedule_once(partial(buildvasscreen, sm, screen, True, ranked), min_wait)
                Clock.schedule_once(partial(start_exo_bertec_only, sm), min_wait)
            else:
                buildvasscreen(sm, screen, confirmed=True, ranked=ranked)


    screen.clear_widgets()
    screen.sm = sm
    if not confirmed:
        sm.statemachine.next_trial_pres()

    # Layout params
    screen.sliders_origin = (1/10, 1/10)
    screen.sliders_size = (6/10, 8.5/10)

    screen.buttons_origin = (8/10, 1/10)
    screen.buttons_size = (2/10, 8.5/10)

    confirm_btn_origin = {'x': 0, 'y': 0}
    confirm_btn_size = (1, 1/10)

    mv_label_size = (1/10, 9/10)

    # Confirm Button
    confirm_btn = Button(text='', font_size='100', color=(1,1,1), background_normal='', background_color=get_color_from_hex('#004B8D'), size_hint=confirm_btn_size, pos_hint=confirm_btn_origin)
    confirm_btn.text = "Confirm" if not confirmed else "Finish"
    confirm_btn.signature = 1
    confirm_btn.confirmed = confirmed
    confirm_btn.disabled = True
    confirm_btn.bind(on_press=confirmranking)
    screen.confirm_btn = confirm_btn

    # NPO/EPO Text
    npo_label = Label(text="${}".format(sm.NPO_MV), font_size='80', color=(1, 1, 1), size_hint=mv_label_size, pos_hint={'x': 0, 'y': 1/10})
    epo_label = Label(text="${}".format(sm.EPO_MV), font_size='80', color=(1, 1, 1), size_hint=mv_label_size, pos_hint={'x': 7/10, 'y': 1/10})

    buildsliders(sm, screen, sliders_origin=screen.sliders_origin, sliders_size=screen.sliders_size, ranked=ranked, slider_min=sm.NPO_MV, slider_max=sm.EPO_MV)

    buildbtns(sm, screen, screen.buttons_origin, screen.buttons_size, ranked=ranked)
    screen.prev_btn = 0

    screen.add_widget(confirm_btn)
    screen.add_widget(npo_label)
    screen.add_widget(epo_label)

    screen.on_enter = partial(vasscreenschedule, sm)


def buildbreakscreenvas(sm):
    """
    Finish screen
    """
    screen = Screen(name="breakscreenvas")
    screen.sm = sm

    min_wait = VAS_10BTN_BREAK/sm.squeeze
    if min_wait/sm.squeeze < 60:
        waittext = "Take quick break!\nTrial resumes in {} seconds".format(int(min_wait/sm.squeeze))
    else:
        waittext = "Take quick break!\nTrial resumes in {:0.1f} minutes".format(min_wait/sm.squeeze/60)

    breaklabel = Label(text=waittext, font_size='100', color=(0, 0.2, 1, 1))
    screen.add_widget(breaklabel)
    screen.on_enter = partial(breakscreenvasschedule, sm)
    return screen


def buildfinishscreenvas(sm):
    """
    Finish screen
    """
    screen = Screen(name="finishscreenvas")
    screen.sm = sm
    finishlabel = Label(text="Trial Finished\nPlease step off the treadmill", font_size='100', color=(1, 0, 0, 1))
    screen.add_widget(finishlabel)
    screen.on_enter = partial(finishscreenvasschedule, sm)
    return screen
