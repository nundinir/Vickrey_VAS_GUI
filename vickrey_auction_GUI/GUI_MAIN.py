import numpy as np
from functools import partial

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty

import grpc
import auction_pb2 as pb2
import auction_pb2_grpc as pb2_grpc

from constants import *
from auction_schedules import *
from statemachine import VA_StateMachine
from vickrey_auction_GUI import constants

# Button Callbacks
def callback(instance):
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
    sm.statemachine.next_screen()

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
    btn0.bind(on_press=callback)
    
    btnBCKSPC = Button(text="BCKSPC", font_size='70', size_hint=(1/gn_x, 2/gn_y), pos_hint={'x':3/gn_x, 'y':2/gn_y},  background_color =(0.5, 0.5, 0.5, 1))
    btnBCKSPC.bind(on_press=BCKSPC_CB)
    
    btnCLEAR = Button(text="CLEAR", font_size='70', size_hint=(1/gn_x, 2/gn_y), pos_hint={'x':3/gn_x, 'y':0/gn_y},  background_color =(0.5, 0.5, 0.5, 1))
    btnCLEAR.bind(on_press=CLEAR_CB)

    sm.cdt = CountDownTimer(text='', font_size = '70', size_hint=(1/gn_x, 3/gn_y), pos_hint={'x':0/gn_x, 'y':4/gn_y})

    screen_.add_widget(bid_input)
    screen_.add_widget(btn0)
    screen_.add_widget(btnBCKSPC)
    screen_.add_widget(btnCLEAR)
    screen_.add_widget(sm.cdt)

    for i in range(1, 10):
        x_p = ((i-1) % 3) / gn_x
        y_p = ((i-1) // 3 + 1) / gn_y

        btn = Button(text="{}".format(i), font_size='70', size_hint=(1/gn_x, 1/gn_y), pos_hint={'x':x_p, 'y':y_p},  background_color =(0.5, 0.5, 0.5, 1))
        btn.val = '{}'.format(i)
        btn.bind(on_press=callback)

        screen_.add_widget(btn)

    screen_.on_enter = partial(numpad_schedule,sm)

    return screen_

# Timer class
class CountDownTimer(Label):
    dur = NumericProperty(0)
    def start(self, dur, *vargs):
        self.dur = dur
        Animation.cancel_all(self)
        self.anim = Animation(dur=0, duration=self.dur)
        def finish_callback(animation, CDT):
            CDT.text = "Finished"
        self.anim.bind(on_complete=finish_callback)
        self.anim.start(self)

    def on_dur(self, instance, value):
        self.text = '{:.2f}'.format(value)

# GRPC object
class CallerGRPC:
    def __init__(self):
        self.channel = grpc.insecure_channel(constants.server_ip)
        self.stub = pb2_grpc.auctionStub(self.channel)

    def testconnection(self, subject_name):
        # Send testmsg to AuctionHouse
        msg = pb2.testmsg(subject=subject_name)
        response = self.stub.testconnection(msg)
        
        # See response received
        if response:
            print("Connection Successful\n")
        else:
            raise ConnectionError("AuctionHouse connection unsuccessful.")

    def call(self, t, subject_bid, user_win_flag, current_payout, total_winnings):
        resultmsg = pb2.result(t=t,
                         subject_bid=subject_bid,
                         user_win_flag=user_win_flag,
                         current_payout=current_payout,
                         total_winnings=total_winnings
                         )
        response = self.stub.call(resultmsg)
        return response

# Combines kivy screen manager, statemachine, and GRPC into app
class CallerGUI(App):
    def build(self):
        sm = ScreenManager()
        sm.statemachine = VA_StateMachine(sm)
        sm.callergrpc = CallerGRPC()

        sm.previous_bid = ''
        sm.bid = ''

        # Create Screens
        dummyscreen = Screen(name="dummy")

        pushtostartscreen = Screen(name="pushtostartscreen")
        startbttn = Button(text="Touch to begin")
        startbttn.bind(on_press=startbttn_CB)
        pushtostartscreen.add_widget(startbttn)

        numpad = buildNumPadScreen(sm)

        waitingscreen = Screen(name="waitingscreen")
        waitingscreen.label = Label(text="", color =(1, 1, 1, 1))
        waitingscreen.add_widget(waitingscreen.label)
        waitingscreen.on_pre_enter = partial(waitingscreen_pre_enter, waitingscreen, sm)
        waitingscreen.on_enter = partial(waitingscreen_schedule, sm)

        # Result screens: 4 cases
        continuewalkingscreen = Screen(name="continuewalkingscreen")
        continuewalkingscreen.add_widget(Label(text="You have won! Continue Walking. Winning Bid. Payout.", color =(1, 1, 1, 1)))
        continuewalkingscreen.on_enter = partial(result_screens_schedule, sm)

        startwalkingscreen = Screen(name="startwalkingscreen")
        startwalkingscreen.add_widget(Label(text="You have won! Step on treadmill to begin walking. Winning Bid. Payout.", color =(1, 1, 1, 1)))
        startwalkingscreen.on_enter = partial(result_screens_schedule, sm)

        stopwalkingscreen = Screen(name="stopwalkingscreen")
        stopwalkingscreen.add_widget(Label(text="You have lost. Step off treadmill to sit out the round. Winning Bid. Payout.", color =(1, 1, 1, 1)))
        stopwalkingscreen.on_enter = partial(result_screens_schedule, sm)

        continuesittingscreen = Screen(name="continuesittingscreen")
        continuesittingscreen.add_widget(Label(text="You have lost. Continue Sitting. Winning Bid. Payout.", color =(1, 1, 1, 1)))
        continuesittingscreen.on_enter = partial(result_screens_schedule, sm)

        # Add screens to ScreenManager
        sm.add_widget(dummyscreen)
        sm.add_widget(pushtostartscreen)
        sm.add_widget(numpad)
        sm.add_widget(waitingscreen)
        sm.add_widget(continuewalkingscreen)
        sm.add_widget(startwalkingscreen)
        sm.add_widget(stopwalkingscreen)
        sm.add_widget(continuesittingscreen)

        # Switch from dummy to startscreen to run on_enter
        sm.current = "pushtostartscreen"

        return sm

if __name__ == "__main__":
    CallerGUI().run()
