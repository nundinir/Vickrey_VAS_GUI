from functools import partial

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from shared_files.utils import decimal_format
from constants import *
from gui_files.vickrey_gui.vickrey_schedules import *
from shared_files.kivy_utils import CountDownTimer

# push to start screen
def startbttn_CB(instance):
    sm = instance.parent.parent
    if sm.statemachine.auction_tally > 0 and sm.statemachine.state:
        # Start treadmill and unpause exoboots
        sm.bertec.write_command(sm.bertec_speed, sm.bertec_speed, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
        sm.exoboot_remote.set_pause(mybool=False)
        sm.exoboot_remote.set_torques(peak_torque_left=sm.peak_torque, peak_torque_right=sm.peak_torque)

    sm.statemachine.next_screen()

def buildpushtostartscreen(sm):
    screen = Screen(name="pushtostartscreen")

    backupflag = sm.statemachine.backupflag

    if backupflag:
        state = sm.statemachine.state
        auction_tally = sm.statemachine.auction_tally
        if auction_tally == 0:
            text = "Touch to begin"
        elif state:
            text = "STOMP then Touch to walk"
            recording_name = "{}_t{}".format(sm.file_prefix, int(sm.statemachine.auction_tally * ROBOWALK_DUR))
            sm.vicon.start_recording(recording_name)
        else:
            text = "Remain seated\nTouch to resume"
    else:
        text = "Touch to begin"

    sm.statemachine.backupflag = False

    startbttn = Button(text=text, font_size='50', color=(1, 1, 1, 1), size_hint=(3/4,3/4), pos_hint={'x':1/8,'y':1/8})
    startbttn.bind(on_press=startbttn_CB)
    screen.add_widget(startbttn)

    return screen, startbttn


# numpad screen
def numpad_cb(instance):
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


def buildNumPadScreen(sm):
    screen = Screen(name="numpad")
    screen.sm = sm

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

    screen.add_widget(bid_input)
    screen.add_widget(btn0)
    screen.add_widget(btnBCKSPC)
    screen.add_widget(btnCLEAR)
    screen.add_widget(sm.cdt)
    screen.add_widget(timerlabel)

    for i in range(1, 10):
        x_p = ((i-1) % 3) / gn_x
        y_p = ((i-1) // 3 + 1) / gn_y

        btn = Button(text="{}".format(i), font_size='70', size_hint=(1/gn_x, 1/gn_y), pos_hint={'x':x_p, 'y':y_p},  color=(1,1,1), background_color=(0.5,0.5,0.5))
        btn.val = '{}'.format(i)
        btn.bind(on_press=numpad_cb)

        screen.add_widget(btn)

    screen.on_enter = partial(numpad_schedule, sm)

    return screen

# survey screen
def enjoyment_cb(instance):
    sm = instance.parent.parent
    sm.enjoyment = instance.val

def rpe_cb(instance):
    sm = instance.parent.parent
    sm.rpe = instance.val

def buildsurveyscreen(sm):
    screen = Screen(name="survey")
    screen.sm = sm

    enjoyment_label = Label(text="Rate your enjoyment", font_size='70', size_hint=(1/3, 1/6), pos_hint={'x':1/3, 'y':8.5/10}, halign='center')
    screen.add_widget(enjoyment_label)

    enjoyment_levels = ['skull', 'frown', 'neutral', 'smile', 'sunglasses']
    for i, level in enumerate(enjoyment_levels):
        btn_ = Button(background_normal='images/{}.png'.format(level), size_hint=(1/6, 1/6), pos_hint={'x':i/5, 'y':2/3})
        btn_.val = i - 2
        btn_.bind(on_press=enjoyment_cb)
        screen.add_widget(btn_)

    rpe_label = Label(text="Rate your exertion (RPE)", font_size='70', size_hint=(1/3, 1/6), pos_hint={'x':1/3, 'y':1/3}, halign='center')
    screen.add_widget(rpe_label)

    for i in range(6, 21):
        i_ = i-6
        x_p = i_ / 15
        y_p = 0.1

        btn = Button(text="{}".format(i), font_size='70', color = (1,1,1), background_normal='', background_color= (i_/14,(1-i_/14),0,0.5), size_hint=(1/15, 1/5), pos_hint={'x':x_p, 'y':y_p})
        btn.val = i
        btn.bind(on_press=rpe_cb)
        screen.add_widget(btn)

    screen.on_enter = partial(survey_schedule,sm)

    return screen

def buildresultscreen(sm):
    screen = Screen(name="resultscreen")
    screen.label = Label(text='', font_size='50')
    screen.add_widget(screen.label)
    screen.on_enter = partial(result_screens_schedule, sm)
    return screen
