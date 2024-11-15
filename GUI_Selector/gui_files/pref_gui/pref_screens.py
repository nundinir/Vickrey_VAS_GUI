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
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy_garden.radialslider import RadialSlider

from constants import *
from gui_files.pref_gui.pref_schedules import waitingscreenprefschedule, prefscreenschedule, reset_sliderscreen, finishscreenprefschedule

from gui_files.pref_gui.continuous_dial_class import PrefDial

def startbtn_CB(instance):
    sm = instance.parent.parent
    # Set bertec speed
    sm.bertec.write_command(sm.bertec_speed, sm.bertec_speed, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    # Unpause exoboots
    sm.exoboot_remote.set_pause(mybool=False)
    # Next screen
    sm.statemachine.next_screen()

def buildpushtostartscreenpref(sm):
    screen = Screen(name="pushtostartscreenpref")
    screen.sm = sm
    startbttn = Button(text="STOMP then Touch to begin", font_size='50', color=(1, 1, 1, 1), size_hint=(3/4,3/4), pos_hint={'x':1/8,'y':1/8})
    startbttn.bind(on_press=startbtn_CB)
    screen.add_widget(startbttn)

    return screen


def buildwaitingscreenpref(sm):
    screen = Screen(name="waitingscreenpref")
    screen.sm = sm
    if MIN_WAIT_PREF/sm.squeeze < 60:
        waittext = "Take a break!\nTrial resumes in {} seconds".format(int(MIN_WAIT_PREF/sm.squeeze))
    else:
        waittext = "Take a break!\nTrial resumes in {:0.1f} minutes".format(MIN_WAIT_PREF/sm.squeeze/60)
    waitlabel = Label(text=waittext, font_size='50', color=(1, 1, 1, 1))
    screen.add_widget(waitlabel)

    screen.on_enter = partial(waitingscreenprefschedule, sm)

    return screen

def disable_btn(screen, mybool, dt):
    screen.confirm_btn.disabled = mybool

def onslidermotion(instance, torque):
    # Reset confirm button
    if instance.parent.confirm_btn.confirmed:
        instance.parent.confirm_btn.confirmed = False
        instance.parent.confirm_btn.background_color = (0.75,0,0)
        instance.parent.confirm_btn.text = "Confirm"

    sm = instance.parent.parent
    torque = instance.parent.tslider.value
    sm.exoboot_remote.set_torques(peak_torque_left=torque, peak_torque_right=torque)

def ondialmotion(instance, torque):
    # Reset confirm button
    if instance.parent.confirm_btn.confirmed:
        instance.parent.confirm_btn.confirmed = False
        instance.parent.confirm_btn.background_color = (0.75,0,0)
        instance.parent.confirm_btn.text = "Confirm"

    sm = instance.parent.parent
    torque = instance.parent.dial.torque_value
    # print(f'Current torque is: {torque}')
    sm.exoboot_remote.set_torques(peak_torque_left=torque, peak_torque_right=torque)

def confirm_slider_pref(instance):
    if instance.confirmed:
        sm = instance.parent.parent
        torque = instance.parent.tslider.value
        sm.statemachine.report_pref(torque)
    else:
        instance.confirmed = True
        instance.background_color = (1,0,0)
        instance.text = "ARE YOU SURE?"

        screen = instance.parent
        disable_btn(screen, True, 0)
        Clock.schedule_once(partial(disable_btn, screen, False), 0.2)
        
def confirm_dial_pref(instance):
    if instance.confirmed:
        sm = instance.parent.parent
        torque = instance.parent.dial.torque_value
        print(f'Confirmed torque is: {torque}')
        sm.statemachine.report_pref(torque)
    else:
        instance.confirmed = True
        instance.background_color = (1,0,0)
        instance.text = "ARE YOU SURE?"

        screen = instance.parent
        disable_btn(screen, True, 0)
        Clock.schedule_once(partial(disable_btn, screen, False), 0.2)

def buildsliderscreenpref(sm):
    screen = Screen(name="sliderscreen")
    screen.sm = sm

    tslider = Slider(min = TORQUE_MIN, max=TORQUE_MAX, value = 20, step = PREF_STEP, value_track=True, size_hint=(4/5, 2/3), pos_hint={'x':1/10, 'y':1/3})
    tslider.bind(value = onslidermotion)
    screen.add_widget(tslider)
    screen.tslider = tslider

    confirm_btn = Button(text="Confirm", font_size='70', color = (1,1,1), background_normal='', background_color= (0.75,0,0), size_hint=(1, 1/3), pos_hint={'x':0, 'y':0})
    confirm_btn.confirmed = False
    confirm_btn.bind(on_press=confirm_slider_pref)
    screen.add_widget(confirm_btn)
    screen.confirm_btn = confirm_btn

    screen.on_pre_enter = partial(reset_sliderscreen, sm, screen)
    screen.on_enter = partial(prefscreenschedule, sm)

    return screen


def map_btnnum_to_torque(btnnum, max_btn, t_min=TORQUE_MIN, t_max=TORQUE_MAX):
    return (t_max - t_min) / (max_btn - 1) * btnnum + t_min

def btnpress(instance):
    sm = instance.parent.parent
    screen = instance.parent

    # Current instance
    torque = instance.torque
    sm.exoboot_remote.set_torques(peak_torque_left=torque, peak_torque_right=torque)
    instance.visited = True
    instance.color = (1, 1, 1)
    instance.background_color = (0, 0, 0.9)

    # Unconfirm confirm_btn
    screen.confirm_btn.text = "Confirm"
    screen.confirm_btn.confirmed = False
    screen.confirm_btn.background_color = (0.75, 0, 0)

    # Recolor previous button
    if screen.prev_btn and instance != screen.prev_btn:
        screen.prev_btn.background_color = (0, 0.75, 0)
    screen.prev_btn = instance

    # Activate confirm button if all btns visited
    if screen.confirm_btn.disabled:
        for btn in screen.children:
            if btn.signature and not btn.visited:
                return
        screen.confirm_btn.disabled = False

def confirm_btn_pref(instance):
    sm = instance.parent.parent
    screen = instance.parent
    if instance.confirmed:
        sm.statemachine.report_pref(screen.prev_btn.torque)
    else:
        instance.confirmed = True
        instance.background_color = (1,0,0)
        instance.text = "ARE YOU SURE?"

        disable_btn(screen, True, 0)
        Clock.schedule_once(partial(disable_btn, screen, False), 0.1)

def buildbtnscreenpref(sm, screen):
    screen.clear_widgets()

    confirm_btn_height = 1/5
    confirm_btn = Button(text="Confirm", font_size='70', color = (1,1,1), background_normal='', background_color= (0.75,0,0), size_hint=(1, confirm_btn_height), pos_hint={'x':0, 'y':0})
    confirm_btn.bind(on_press=confirm_btn_pref)
    confirm_btn.confirmed = False
    confirm_btn.disabled = True
    confirm_btn.signature = 0 # Is not a preference button
    screen.add_widget(confirm_btn)
    screen.confirm_btn = confirm_btn

    btnnums = [i for i in range(PREF_ROWS * PREF_COLS)]
    random.shuffle(btnnums)

    # Build Prefence Buttons
    for row in range(PREF_ROWS):
        for col in range(PREF_COLS):
            xpos = col/PREF_COLS
            ypos = 4/5 * (PREF_ROWS - row - 1)/PREF_ROWS + 1/5

            torque = map_btnnum_to_torque(btnnums.pop(), PREF_ROWS * PREF_COLS)
            btn_temp = Button(text = chr(65 + row * PREF_COLS + col), font_size='50', color=(1,1,1), background_normal='', background_color= (0,0.5,0), size_hint=(1/PREF_COLS, (1 - confirm_btn_height) * 1/PREF_ROWS), pos_hint={'x':xpos, 'y':ypos})
            btn_temp.signature = 1 # Is a preference button
            btn_temp.torque = torque
            btn_temp.visited = False
            btn_temp.bind(on_press=btnpress)
            screen.add_widget(btn_temp)

    screen.prev_btn = 0

    screen.on_pre_enter = partial(buildbtnscreenpref, sm, screen)
    screen.on_enter = partial(prefscreenschedule, sm)

def builddialscreenpref(sm):
    screen = Screen(name="dialscreen")
    screen.sm = sm
    
    # create a preference dial
    dial = PrefDial(min_torque=TORQUE_MIN, max_torque=TORQUE_MAX, full_rotations_required=3)
    
    # set the size of the slider
    dial.size_hint = (0.65, 0.65)
    dial.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
    # dial.size = (500, 500)
    dial.thumb_diameter = 35
       
    # Bind the dial change to a callback function
    dial.bind(value=ondialmotion)
    
    # add dial to the screen
    screen.add_widget(dial)
    screen.dial = dial

    # create a confirm button
    confirm_btn = Button(text="Confirm", font_size='70', color = (1,1,1), background_normal='', background_color= (0.75,0,0), size_hint=(1, 1/6), pos_hint={'x':0, 'y':0})
    confirm_btn.confirmed = False
    confirm_btn.bind(on_press=confirm_dial_pref)
    screen.add_widget(confirm_btn)
    screen.confirm_btn = confirm_btn

    screen.pre_on_enter = partial(reset_sliderscreen, sm, screen)
    screen.on_enter = partial(prefscreenschedule, sm)

    return screen # return screen

def buildfinishscreenpref(sm):
    screen = Screen(name="finishscreenpref")
    screen.sm = sm

    finishlabel = Label(text="Experiment Finished\nPlease step off the treadmill", font_size='70', color=(1, 0, 0, 1))
    screen.add_widget(finishlabel)

    screen.on_enter = partial(finishscreenprefschedule, sm)

    return screen
