from functools import partial

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from constants import *
from vickrey_schedules import *
from kivy_utils import CountDownTimer

# Button Callbacks
def numpad_cb(instance):
    print("{} button was pushed".format(instance.val))
    sm = instance.parent.parent
    sm.bid += instance.val
    sm.bid_input.text = decimal_format(sm.bid)

def BCKSPC_CB(instance):
    sm = instance.parent.parent
    sm.bid = sm.bid[:-1]
    sm.bid_input.text = decimal_format(sm.bid)

def CLEAR_CB(instance):
    sm = instance.parent.parent
    sm.bid = ''
    sm.bid_input.text = decimal_format(sm.bid)

def startbttn_CB(instance):
    sm = instance.parent.parent
    if sm.statemachine.auction_tally > 0:
        sm.statemachine.send_treadmill_msg(sm.statemachine.state)
        
        # Start treadmill and unpause exoboots
        sm.bertec.write_command(BERTEC_SPEED_RIGHT, BERTEC_SPEED_LEFT, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
        sm.exoboot_remote.set_pause(mybool=False)
        sm.exoboot_remote.set_torques(peak_torque_left=PEAK_TORQUE_LEFT, peak_torque_right=PEAK_TORQUE_RIGHT)

    sm.statemachine.next_screen()

def enjoyment_cb(instance):
    sm = instance.parent.parent
    sm.enjoyment = instance.val
    print("Enjoyment level: {}".format(sm.enjoyment))

def rpe_cb(instance):
    sm = instance.parent.parent
    sm.rpe = instance.val
    print("RPE: {}".format(sm.rpe))

# Numpad screen builder
def buildNumPadScreen(sm):
    screen_ = Screen(name="numpad")
    screen_.sm = sm

    # Grid num
    gn_x = 4
    gn_y = 6

    bid_input = Label(text=decimal_format(sm.bid), font_size='100', size_hint=(4/gn_x, 1/gn_y), pos_hint={'x':0/gn_x, 'y':4/gn_y},  color =(0.5, 0.5, 0.5, 1))
    sm.bid_input = bid_input

    btn0 = Button(text="0", font_size='70', size_hint=(3/gn_x, 1/gn_y), pos_hint={'x':0/gn_x, 'y':0/gn_y},  background_color =(0.5, 0.5, 0.5, 1))
    btn0.val = '0'
    btn0.bind(on_press=numpad_cb)
    
    btnBCKSPC = Button(text="BCKSPC", font_size='70', size_hint=(1/gn_x, 2/gn_y), pos_hint={'x':3/gn_x, 'y':2/gn_y},  background_color =(0.5, 0.5, 0.5, 1))
    btnBCKSPC.bind(on_press=BCKSPC_CB)
    
    btnCLEAR = Button(text="CLEAR", font_size='70', size_hint=(1/gn_x, 2/gn_y), pos_hint={'x':3/gn_x, 'y':0/gn_y},  background_color =(0.5, 0.5, 0.5, 1))
    btnCLEAR.bind(on_press=CLEAR_CB)

    sm.cdt = CountDownTimer(text='', font_size = '70', size_hint=(1/gn_x, 3/gn_y), pos_hint={'x':3/gn_x, 'y':4/gn_y})
    
    timerlabel = Label(text='Close in: ', font_size = '50',size_hint=(1/gn_x, 3/gn_y), pos_hint={'x':2/gn_x, 'y':4/gn_y})

    screen_.add_widget(bid_input)
    screen_.add_widget(btn0)
    screen_.add_widget(btnBCKSPC)
    screen_.add_widget(btnCLEAR)
    screen_.add_widget(sm.cdt)
    screen_.add_widget(timerlabel)

    for i in range(1, 10):
        x_p = ((i-1) % 3) / gn_x
        y_p = ((i-1) // 3 + 1) / gn_y

        btn = Button(text="{}".format(i), font_size='70', size_hint=(1/gn_x, 1/gn_y), pos_hint={'x':x_p, 'y':y_p},  color=(1,1,1), background_color=(0.5,0.5,0.5))
        btn.val = '{}'.format(i)
        btn.bind(on_press=numpad_cb)

        screen_.add_widget(btn)

    screen_.on_enter = partial(numpad_schedule,sm)

    return screen_

def buildsurveyscreen(sm):
    screen_ = Screen(name="survey")
    screen_.sm = sm

    enjoyment_label = Label(text="Rate your enjoyment", font_size='30', size_hint=(1/3, 1/6), pos_hint={'x':1/3, 'y':8.5/10}, halign='center')
    screen_.add_widget(enjoyment_label)

    enjoyment_levels = ['skull', 'frown', 'neutral', 'smile', 'sunglasses']
    for i, level in enumerate(enjoyment_levels):
        btn_ = Button(background_normal='images/{}.png'.format(level), size_hint=(1/6, 1/6), pos_hint={'x':i/5, 'y':2/3})
        btn_.val = i - 2
        btn_.bind(on_press=enjoyment_cb)
        screen_.add_widget(btn_)

    rpe_label = Label(text="Rate your exertion (RPE)", font_size='30', size_hint=(1/3, 1/6), pos_hint={'x':1/3, 'y':1/3}, halign='center')
    screen_.add_widget(rpe_label)

    for i in range(6, 21):
        i_ = i-6
        x_p = i_ / 15
        y_p = 0.1

        btn = Button(text="{}".format(i), font_size='70', color = (1,1,1), background_normal='', background_color= (i_/14,(1-i_/14),0,0.5), size_hint=(1/15, 1/5), pos_hint={'x':x_p, 'y':y_p})
        btn.val = i
        btn.bind(on_press=rpe_cb)
        screen_.add_widget(btn)

    screen_.on_enter = partial(survey_schedule,sm)

    return screen_

def buildpushtostartscreen(sm, fontsize):
    screen_= Screen(name="pushtostartscreen")
    startbttn = Button(text="Touch to begin", font_size=fontsize, color=(1, 1, 1, 1))
    startbttn.bind(on_press=startbttn_CB)
    screen_.add_widget(startbttn)

    return screen_