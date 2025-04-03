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
from shared_files.kivy_utils import CountDownTimer
from gui_files.pref_gui.pref_schedules import waitingscreenprefschedule, walksreenprefschedule, prefscreenschedule, reset_sliderscreen, finishscreenprefschedule


def bertecspeed_start(instance):
    screen = instance.parent
    sm = instance.parent.parent

    bertecspeed = instance.source.value
    bertec_acc = screen.bertec_acc_slider.value

    # Command Bertec
    if instance.state == "down":
        sm.bertec.write_command(bertecspeed, bertecspeed, incline=None, accR=bertec_acc, accL=bertec_acc)
    else:
        # Remove ability to toggle, force use of STOP button
        instance.state = "down"

def bertecspeed_stop(instance):
    screen = instance.parent
    sm = instance.parent.parent

    bertec_acc = screen.bertec_acc_slider.value
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=bertec_acc, accL=bertec_acc)

    instance.source.startbtn.state = "normal"

def torqueslider_start(instance):
    sm = instance.parent.parent

    peaktorque = instance.source.value

    # Command exoboots
    if instance.state == "down":
        sm.exoboot_remote.set_torques(peak_torque_left=peaktorque, peak_torque_right=peaktorque)
        sm.exoboot_remote.set_pause(mybool=False)
        sm.exoboot_remote.set_log(mybool=False)
    else:
        # Remove ability to toggle, force use of STOP button
        instance.state = "down"

def torqueslider_stop(instance):
    sm = instance.parent.parent
    sm.exoboot_remote.set_torques(peak_torque_left=0, peak_torque_right=0)
    sm.exoboot_remote.set_pause(mybool=True)
    sm.exoboot_remote.set_log(mybool=True)
    instance.source.startbtn.state = "normal"

def vicon_start(instance):
    sm = instance.parent.parent

    if instance.state == "down":
        filename = str(instance.source.text)
        sm.vicon.start_recording(filename)
    else:
        # Remove ability to toggle, force use of STOP button
        instance.state = "down"

def vicon_stop(instance):
    sm = instance.parent.parent
    sm.vicon.stop_recording()
    instance.source.startbtn.state = "normal"

def bind_link(instance):
    sm = instance.parent.parent
    if instance.state == "down":
        instance.background_color = [1, 1, 0, 1]
    else:
        instance.background_color = [0.5, 0.5, 0, 1]


def bertecslider_onmotion(instance, bertec_speed):
    instance.label.text = "Bertec SPEED: {:.2f}".format(round(bertec_speed, 2))

def bertec_acc_slider_onmotion(instance, bertec_acc):
    instance.label.text = "Bertec ACC: {:.2f}".format(round(bertec_acc, 2))

def torqueslider_onmotion(instance, peak_torque):
    instance.label.text = "EXO Peak Torque : {:.2f}".format(round(peak_torque, 2))

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

    startbtn = ToggleButton(text="START", font_size="40", color = (1,1,1), background_normal='', background_color=[0,1,0,1], size_hint=(startbtn_sizex, startbtn_sizey), pos_hint={"x":startbtn_posx, "y":startbtn_posy})
    startbtn.background_normal = 'atlas://data/images/defaulttheme/button_pressed'
    startbtn.background_down = ''
    startbtn.bind(on_press=bindstart)
    startbtn.source = source

    stopbtn = Button(text="STOP", font_size="40", color = (1,1,1), background_normal='', background_color= [1,0,0,1], size_hint=(stopbtn_sizex, stopbtn_sizey), pos_hint={"x":stopbtn_posx, "y":stopbtn_posy})
    stopbtn.bind(on_press=bindstop)
    stopbtn.source = source

    linkbtn = ToggleButton(text="LINK", font_size="40", color = (1,1,1), background_normal='', background_color= [0.5,0.5,0,1], size_hint=(linkbtn_sizex, linkbtn_sizey), pos_hint={"x":linkbtn_posx, "y":linkbtn_posy})
    linkbtn.background_down = ''
    linkbtn.bind(on_press=bind_link)
    linkbtn.source = source
    # Add buttons
    screen.add_widget(startbtn)
    screen.add_widget(stopbtn)
    screen.add_widget(linkbtn)

    # Associate with source
    source.startbtn = startbtn
    source.stopbtn = stopbtn
    source.linkbtn = linkbtn

    sm.control_sectors.append(source)


def trigger_stop(screen, dt):
    screen.stop_linked_btn.trigger_action()

def display_cdt(screen, dt):
    pass

def hide_duration_input(screen, opacity, *vargs):
    screen.duration_label.opacity = opacity
    screen.duration_status.opacity = opacity
    screen.clear_duration.opacity = opacity

    for ord_sep in screen.ord_separators:
        ord_sep.opacity = opacity

    for ord, mags in DURATION_ORDERS.items():
        for mag in mags:
            mag_label = screen.duration_inputs_dict[ord][mag]

            mag_label.opacity = opacity
            mag_label.inc_btn.opacity = opacity
            mag_label.dec_btn.opacity = opacity

def bind_start_linked(instance):
    screen = instance.parent
    sm = screen.parent
    if instance.state == "down":
        for source in sm.control_sectors:
            if source.linkbtn.state == "down":
                source.startbtn.trigger_action()

        if instance.parent.duration_status.state == "down":
            duration_in_sec = 0
            for ord, mags in screen.duration_inputs_dict.items():
                for mag, label in mags.items():
                    duration_in_sec += ORDS_TO_SEC[ord] * MAG_TO_SEC[mag] * label.value

            screen.scheduled_events.append(Clock.schedule_once(partial(display_cdt, screen), 0))
            screen.scheduled_events.append(Clock.schedule_once(partial(trigger_stop, screen), duration_in_sec))

            screen.countdowntimer.opacity = 1
            hide_duration_input(screen, opacity=0)
            screen.countdowntimer.start(duration_in_sec)
            
    else:
        # Prevent toggle, force STOP linked usage
        instance.state = "down"
        return


def bind_stop_linked(instance):
    screen = instance.parent
    sm = screen.parent
    for source in sm.control_sectors:
        if source.linkbtn.state == "down":
            source.stopbtn.trigger_action()

    try:
        for event in screen.scheduled_events:
            Clock.unschedule(event)
    except:
        pass

    screen.countdowntimer.opacity = 0
    hide_duration_input(screen, opacity=1)

    instance.parent.start_linked_btn.state = "normal"

def bind_increment_decrement(instance):
    instance.linked_value.value = (int(instance.linked_value.value) + instance.operation) % 10
    instance.linked_value.text = str(instance.linked_value.value)

def build_increment_decline_buttons(screen, size_hint, pos_hint):
    screen.value_label = Label(text="0", color=(1,1,1), font_size="60", size_hint=(size_hint[0], size_hint[1]/3), pos_hint={'x': pos_hint['x'], 'y': pos_hint['y']+size_hint[1]/3})
    screen.value_label.value = 0

    screen.value_label.inc_btn = Button(text="", background_color=(0,1,0,1), size_hint=(size_hint[0], size_hint[1]/6), pos_hint={'x': pos_hint['x'], 'y': pos_hint['y']+size_hint[1]*2/3})
    screen.value_label.inc_btn.linked_value = screen.value_label
    screen.value_label.inc_btn.operation = 1
    screen.value_label.inc_btn.bind(on_press=bind_increment_decrement)

    screen.value_label.dec_btn = Button(text="", background_color=(1,0,0,1), size_hint=(size_hint[0], size_hint[1]/6), pos_hint={'x': pos_hint['x'], 'y': pos_hint['y']+size_hint[1]/6})
    screen.value_label.dec_btn.linked_value = screen.value_label
    screen.value_label.dec_btn.operation = -1
    screen.value_label.dec_btn.bind(on_press=bind_increment_decrement)
    
    screen.add_widget(screen.value_label)
    screen.add_widget(screen.value_label.inc_btn)
    screen.add_widget(screen.value_label.dec_btn)

    return screen.value_label

def bind_duration_status(instance):
    if instance.state == "down":
        instance.background_color=(0,1,0,1)
        instance.text = "ENABLED"
    else:
        instance.background_color=(1,0,0,1)
        instance.text = "DISABLED"

def bind_clear_duration(instance):
    screen = instance.parent

    for mags in screen.duration_inputs_dict.values():
        for mag in mags.values():
            mag.value = 0
            mag.text = str(mag.value)


def build_duration_input(screen, size_hint, pos_hint):
    screen.duration_label = Label(text="Duration:", color=(1,1,1), font_size="60", size_hint=(size_hint[0]*3/10, size_hint[1]/3), pos_hint={"x":pos_hint['x']+size_hint[0]/10, "y": pos_hint['y']+size_hint[1]/3})

    screen.duration_status = ToggleButton(text="DISABLED", color=(1,1,1), background_color=(1,0,0,1), font_size="50", size_hint=(size_hint[0]*3/10, size_hint[1]/6), pos_hint={'x':pos_hint['x']+size_hint[0]/10, 'y': pos_hint['y']+size_hint[1]*2/3})
    screen.duration_status.bind(on_press=bind_duration_status)

    screen.clear_duration = Button(text="CLEAR", color=(1,1,1), font_size="70", size_hint=(size_hint[0]*3/10, size_hint[1]/6), pos_hint={"x":pos_hint['x']+size_hint[0]/10, "y": pos_hint['y']+size_hint[1]/6})
    screen.clear_duration.bind(on_press=bind_clear_duration)

    screen.add_widget(screen.duration_label)
    screen.add_widget(screen.duration_status)
    screen.add_widget(screen.clear_duration)

    num_ords = len([place for mag in DURATION_ORDERS.values() for place in mag])

    ind=0
    inc_dec_size_x = 5/10
    for ord, mags in DURATION_ORDERS.items():
        screen.duration_inputs_dict[ord] = {}
        for mag in mags:
            mag_label = build_increment_decline_buttons(screen, (size_hint[0]*inc_dec_size_x/num_ords, size_hint[1]), {'x':size_hint[0]+pos_hint['x']-size_hint[0]*inc_dec_size_x*(ind + 1)/num_ords, 'y':pos_hint['y']})
            screen.duration_inputs_dict[ord][mag] = mag_label
            ind += 1
        if not ind % 2:
            ord_separator = Label(text=":", color=(1,1,1), font_size="60", size_hint=(size_hint[0]*inc_dec_size_x/num_ords, size_hint[1]), pos_hint={'x':size_hint[0]+pos_hint['x']-size_hint[0]*inc_dec_size_x*(ind + 0.5)/num_ords, 'y':pos_hint['y']})
            screen.add_widget(ord_separator)
            screen.ord_separators.append(ord_separator)


def buildcontrolpanel(sm):
    screen = Screen(name="controlpanel")
    screen.sm = sm
    screen.scheduled_events = []

    sm.control_sectors = []
    screen.ord_separators = []

    screen.bertecslider = Slider(min=BERTEC_SPEED_MIN, max=BERTEC_SPEED_MAX, value=BERTEC_SPEED_MIN, step=BERTEC_SPEED_STEP, value_track=True, size_hint=(1/2-1/8, 1/3), pos_hint={"x":1/8, "y": 2/3})
    screen.bertecslider.bind(value=bertecslider_onmotion)
    build_sls_buttons(screen, screen.bertecslider, (1/8, 1/3), {"x":1/2, "y":2/3}, bertecspeed_start, bertecspeed_stop)
    screen.bertecslider.label = Label(text="Bertec SPEED: {:.2f}".format(round(BERTEC_SPEED_MIN, 2)), font_size="60", size_hint=(0.1,0.1), pos_hint={'x': (1/2-1/8)*1/2+3/40, 'y': 2/3+1/5})

    screen.bertec_acc_slider = Slider(orientation='vertical', min=0, max=1.0, value=0, step=0.05, value_track=True, size_hint=(1/8, 1/3-1/10), pos_hint={'x':0, 'y':2/3+1/20})
    screen.bertec_acc_slider.bind(value=bertec_acc_slider_onmotion)
    screen.bertec_acc_slider.label = Label(text="ACC: {:.2f}".format(round(0, 2)), color=(1, 1, 0, 1), font_size="40", size_hint=(1/8, 1/20), pos_hint={'x': 0, 'y': 1-1/20})

    screen.torqueslider = Slider(min=TORQUE_MIN, max=TORQUE_MAX, value=TORQUE_MIN, step=TORQUE_STEP, value_track=True, size_hint=(1/2, 1/3), pos_hint={"x":0, "y": 1/3})
    screen.torqueslider.bind(value=torqueslider_onmotion)
    build_sls_buttons(screen, screen.torqueslider, (1/8, 1/3), {"x":1/2, "y":1/3}, torqueslider_start, torqueslider_stop)
    screen.torqueslider.label = Label(text="EXO Peak Torque : {:.2f}".format(round(TORQUE_MIN, 2)), font_size="60", size_hint=(0.1,0.1), pos_hint={'x': 1/4-1/20, 'y': 1/3+1/5})
    
    screen.viconfilenameinput = TextInput(text="Vicon file name here", font_size="40", size_hint=(1/3, 1/8), pos_hint={"x":1/3*1/4, "y": 1/6-1/16})
    build_sls_buttons(screen, screen.viconfilenameinput, (1/8, 1/3), {"x":1/2, "y":0}, vicon_start, vicon_stop)
    
    screen.start_linked_btn = ToggleButton(text="Start Linked", font_size="80", color=(1,1,1), background_normal='', background_color=[0,1,0,1], size_hint=(3/8, 1/4), pos_hint={"x":5/8, "y": 3/4})
    screen.start_linked_btn.background_normal = 'atlas://data/images/defaulttheme/button_pressed'
    screen.start_linked_btn.background_down = ''
    screen.start_linked_btn.bind(on_press=bind_start_linked)
    
    screen.stop_linked_btn = Button(text="STOP Linked", font_size="80", color=(1,1,1), background_normal='', background_color=[1,0,0,1], size_hint=(3/8, 1/4), pos_hint={"x":5/8, "y": 0})
    screen.stop_linked_btn.bind(on_press=bind_stop_linked)

    screen.duration_inputs_dict = {}
    build_duration_input(screen, (3/8, 1/2), {'x': 5/8,'y': 1/4})
    screen.countdowntimer = CountDownTimer(text='asdf', font_size = '70', size_hint=(3/8, 1/2), pos_hint={'x': 5/8,'y': 1/4})
    screen.countdowntimer.opacity = 0
    
    # Add widgets
    screen.add_widget(screen.bertecslider)
    screen.add_widget(screen.bertecslider.label)
    screen.add_widget(screen.bertec_acc_slider)
    screen.add_widget(screen.bertec_acc_slider.label)
    screen.add_widget(screen.torqueslider)
    screen.add_widget(screen.torqueslider.label)
    screen.add_widget(screen.viconfilenameinput)
    screen.add_widget(screen.start_linked_btn)
    screen.add_widget(screen.stop_linked_btn)
    screen.add_widget(screen.countdowntimer)

    return screen
