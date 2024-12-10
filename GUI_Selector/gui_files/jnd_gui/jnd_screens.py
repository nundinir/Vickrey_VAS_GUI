from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from constants import *
from gui_files.jnd_gui.jnd_schedules import splitsameschedule, waitingscreenjndschedule, finishscreenjndschedule
from shared_files.kivy_utils import CountDownTimer


def buildpushtostartscreenjnd():
    """
    Push to start screen for jnd
    """
    def startbtn_CB(instance):
        sm = instance.parent.parent
        # Set bertec speed
        sm.bertec.write_command(sm.bertec_speed, sm.bertec_speed, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
        # Unpause exoboots
        sm.exoboot_remote.set_pause(mybool=False)
        # Next screen
        sm.statemachine.next_screen()

    # Build screen
    screen = Screen(name="pushtostartscreenjnd")
    startbttn = Button(text="STOMP then Touch to begin", font_size='50', color=(1, 1, 1, 1), size_hint=(3/4,3/4), pos_hint={'x':1/8,'y':1/8})
    startbttn.bind(on_press=startbtn_CB)
    screen.add_widget(startbttn)

    return screen


def buildwaitingscreenjnd(sm):
    """
    Enforced minimum waiting period between jnd rounds
    """
    screen = Screen(name="waitingscreenjnd")
    screen.sm = sm
    if MIN_WAIT_JND/sm.squeeze < 60:
        waittext = "Take a break!\nTrial resumes in {} seconds".format(int(MIN_WAIT_JND/sm.squeeze))
    else:
        waittext = "Take a break!\nTrial resumes in {:0.1f} minutes".format(MIN_WAIT_JND/sm.squeeze/60)
    waitlabel = Label(text=waittext, font_size='50', color=(1, 1, 1, 1))
    screen.add_widget(waitlabel)
    
    screen.on_enter = partial(waitingscreenjndschedule, screen.sm)

    return screen


def disable_btns(screen, mybool, dt):
    for btn in screen.children:
        btn.disabled = mybool


def buildsplitlegscreen(sm):
    """
    Splitleg screen for JND
    Left and Right button
    """
    def report_higher(instance):
        screen = instance.parent
        disable_btns(screen, True, 0)
        Clock.schedule_once(partial(disable_btns, screen, False), 0.1)

        sm = instance.parent.parent
        sm.statemachine.report_higher(instance.signature)

    # Build screen
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


def buildsamelegscreen(sm):
    """
    Same leg screen for JND
    Swap and confirm button
    """
    def swap_torques(instance):
        # Toggle swap button colors
        if instance.is_blue:
            instance.background_color = (0, 0, 1, 1)
        else:
            instance.background_color = (0, 1, 1, 1)

        instance.is_blue = not instance.is_blue
        
        # Toggle between torques
        sm = instance.parent.parent
        stma = sm.statemachine
        stma.peak_torque_ind = 1 - stma.peak_torque_ind # FROM STATEMACHINE

        # Command peak torque
        sm.exoboot_remote.set_torques(peak_torque_left=stma.peak_torques[stma.peak_torque_ind], peak_torque_right=stma.peak_torques[stma.peak_torque_ind])

    def confirm_answer(instance):
        screen = instance.parent
        disable_btns(screen, True, 0)
        Clock.schedule_once(partial(disable_btns, screen, False), 0.1)

        sm = instance.parent.parent
        sm.statemachine.report_higher()

    # Build screen
    screen = Screen(name="samelegscreen")
    screen.sm = sm

    swap_btn = Button(text="Swap Torques", font_size='70', color = (1,1,1), background_normal='', background_color= (0,1,1), size_hint=(1, 2/3), pos_hint={'x':0, 'y':1/3})
    
    swap_btn.bind(on_press=swap_torques)
    swap_btn.is_blue = True  # flag to keep track of the button's color state
    screen.add_widget(swap_btn)

    answer_btn = Button(text="Confirm", font_size='70', color = (1,1,1), background_normal='', background_color= (1,0,0), size_hint=(1, 1/3), pos_hint={'x':0, 'y':0})
    answer_btn.bind(on_press=confirm_answer)
    screen.add_widget(answer_btn)

    screen.on_enter = partial(splitsameschedule, sm)

    return screen


def buildfinishscreenjnd(sm):
    """
    Finish screen for JND
    """
    screen = Screen(name="finishscreenjnd")
    screen.sm = sm
    finishlabel = Label(text="Trial Finished\nPlease step off the treadmill", font_size='50', color=(1, 0, 0, 1))
    screen.add_widget(finishlabel)

    screen.on_enter = partial(finishscreenjndschedule, sm)

    return screen
