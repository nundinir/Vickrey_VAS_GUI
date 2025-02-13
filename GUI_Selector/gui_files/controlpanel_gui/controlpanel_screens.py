import random
from functools import partial

# from kivy.app import App
# from kivy.clock import Clock
# from kivy.uix.label import Label
# from kivy.uix.slider import Slider
# from kivy.uix.button import Button
# from kivy.uix.screenmanager import Screen

from math import atan2
import random
from functools import partial

from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy_garden.radialslider import RadialSlider
from kivy.uix.relativelayout import RelativeLayout

from constants import *
from gui_files.pref_gui.pref_schedules import waitingscreenprefschedule, walksreenprefschedule, prefscreenschedule, reset_sliderscreen, finishscreenprefschedule


def startbtn_CB(instance):
    sm = instance.parent.parent
    # Set bertec speed
    sm.bertec.write_command(sm.bertec_speed, sm.bertec_speed, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    # Unpause exoboots
    sm.exoboot_remote.set_pause(mybool=False)
    # Next screen
    sm.statemachine.next_screen()

def buildpushtostartscreencontrolpanel(sm):
    screen = Screen(name="pushtostartscreencontrolpanel")
    screen.sm = sm
    startbttn = Button(text="STOMP then Touch to begin", font_size='50', color=(1, 1, 1, 1), size_hint=(3/4,3/4), pos_hint={'x':1/8,'y':1/8})
    startbttn.bind(on_press=startbtn_CB)
    screen.add_widget(startbttn)
    
    return screen


def bertecspeed_start(instance):
    sm = instance.parent.parent

    bertecspeed = instance.source.value
    bertecacc = 0.33 # TODO GET FROM ACC ADJUSTER

    # Command Bertec
    if instance.state == "normal":
        sm.bertec.write_command(bertecspeed, bertecspeed, incline=None, accR=bertecacc, accL=bertecacc)
    else:
        # Remove ability to toggle, force use of STOP button
        instance.state = "normal"

def bertecspeed_stop(instance):
    sm = instance.parent.parent

    bertecacc = 0.33 # TODO GET FROM ACC ADJUSTER

    # Command Bertec
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=bertecacc, accL=bertecacc)

    instance.startbtn.state = "down"

def torqueslider_start(instance):
    sm = instance.parent.parent

    peaktorque = instance.source.value

    # Command exoboots
    if instance.state == "normal":
        sm.exoboot_remote.set_torques(peak_torque_left=peaktorque, peak_torque_right=peaktorque)
        sm.exoboot_remote.set_pause(mybool=False)
    else:
        # Remove ability to toggle, force use of STOP button
        instance.state = "normal"

def torqueslider_stop(instance):
    sm = instance.parent.parent
    sm.exoboot_remote.set_torques(peak_torque_left=0, peak_torque_right=0)
    sm.exoboot_remote.set_pause(mybool=True)
    instance.startbtn.state = "down"


def build_sls_buttons(screen, source, size_hint, pos_hint, bindstart, bindstop):
    sm = screen.sm

    # Positions
    startbtn_sizex = size_hint[0] / 2
    startbtn_sizey = size_hint[1] / 2
    startbtn_posx = pos_hint["x"]
    startbtn_posy = pos_hint["y"] + size_hint[1] / 2

    linkbtn_sizex = size_hint[0] / 2
    linkbtn_sizey = size_hint[1] / 2
    linkbtn_posx = pos_hint["x"] + size_hint[0] / 2
    linkbtn_posy = pos_hint["y"] + size_hint[1] / 2

    stopbtn_sizex = size_hint[0]
    stopbtn_sizey = size_hint[1] / 2
    stopbtn_posx = pos_hint["x"]
    stopbtn_posy = pos_hint["y"]

    startbtn = ToggleButton(text="START", font_size="40", color = (1,1,1), background_normal='', background_color= (0,1,0), size_hint=(startbtn_sizex, startbtn_sizey), pos_hint={"x":startbtn_posx, "y":startbtn_posy})
    startbtn.source = source
    startbtn.state = "down"
    startbtn.bind(on_press=bindstart)

    linkbtn = ToggleButton(text="LINK", font_size="40", color = (1,1,1), background_normal='', background_color= (1,1,0), size_hint=(linkbtn_sizex, linkbtn_sizey), pos_hint={"x":linkbtn_posx, "y":linkbtn_posy})
    linkbtn.source = source
    linkbtn.state = "down"
    # linkbtn.bind(on_press=linkbtn)

    stopbtn = Button(text="STOP", font_size="40", color = (1,1,1), background_normal='', background_color= (1,0,0), size_hint=(stopbtn_sizex, stopbtn_sizey), pos_hint={"x":stopbtn_posx, "y":stopbtn_posy})
    stopbtn.source = source
    stopbtn.startbtn = startbtn
    stopbtn.bind(on_press=bindstop)

    # Add buttons
    screen.add_widget(startbtn)
    screen.add_widget(linkbtn)
    screen.add_widget(stopbtn)

    sm.linked_buttons.append(linkbtn)

def bertecslider_onmotion(instance, bertecspeed):
    pass

def torqueslider_onmotion(instance, peaktorque):
    pass

def buildcontrolpanel(sm):
    screen = Screen(name="controlpanel")
    screen.sm = sm

    sm.linked_buttons = []

    screen.bertecslider = Slider(min=BERTEC_SPEED_MIN, max=BERTEC_SPEED_MAX, value=BERTEC_SPEED_MIN, step=BERTEC_SPEED_STEP, value_track=True, size_hint=(1/2, 1/3), pos_hint={"x":0, "y": 2/3})
    screen.bertecslider.bind(value=bertecslider_onmotion)
    build_sls_buttons(screen, screen.bertecslider, (1/8, 1/3), {"x":1/2, "y":2/3}, bertecspeed_start, bertecspeed_stop)
    screen.add_widget(screen.bertecslider)

    screen.torqueslider = Slider(min=TORQUE_MIN, max=TORQUE_MAX, value=TORQUE_MIN, step=TORQUE_STEP, value_track=True, size_hint=(1/2, 1/3), pos_hint={"x":0, "y": 1/3})
    screen.torqueslider.bind(value=torqueslider_onmotion)
    build_sls_buttons(screen, screen.torqueslider, (1/8, 1/3), {"x":1/2, "y":1/3}, torqueslider_start, torqueslider_stop)
    screen.add_widget(screen.torqueslider)

    screen.viconfilenameinput = TextInput(text="Vicon file name here", size_hint=(1/3, 1/8), pos_hint={"x":1/3*1/4, "y": 1/6-1/16} )
    # build_sls_buttons(screen, screen.bertecslider, (1/8, 1/3), {"x":1/2, "y":0}, None, None)
    screen.add_widget(screen.viconfilenameinput)
    
    # print(sm.linked_buttons)

    return screen
