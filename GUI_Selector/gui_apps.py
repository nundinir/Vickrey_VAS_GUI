import numpy as np
from functools import partial

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.image import Image, AsyncImage
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.core.window import Window

from BertecMan import Bertec

from constants import *
from vickrey_schedules import *
from vickrey_screens import buildpushtostartscreen, buildNumPadScreen, buildsurveyscreen
# from vas_screens import VAS_GUIApp
from statemachine import VickreyStateMachine, VASStateMachine

class BaseGui(App):
    def __init__(self, name, exoboot_remote_client, bertec):
        super().__init__()
        self.sm = ScreenManager()
        self.sm.name = name

        # Set Exoboot remote client
        self.sm.exoboot_remote = exoboot_remote_client

        # Pause Exos and set torques
        self.sm.exoboot_remote.set_pause(mybool=True)
        self.sm.exoboot_remote.set_torques(peak_torque_left=PEAK_TORQUE_LEFT, peak_torque_right=PEAK_TORQUE_RIGHT)

        # Bertec over network thread
        self.sm.bertec = bertec
        self.sm.bertec.start()

        def on_request_close(self, *args):
            """
            Stop Bertec treadmill and close Bertec
            Shutdown exoboots remotely
            """
            print("Closing Bertec")
            self.bertec.write_command(0, 0, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
            self.bertec.stop()

            print("Exiting Logging Server")
            self.exoboot_remote.chop()

            print("Shutting down exoboots")
            self.exoboot_remote.set_quit(mybool=True)
            print("Goodbye")

        Window.bind(on_request_close=partial(on_request_close, self.sm))


class VickreyGUI(BaseGui):
    """
    Creates screen manager to run Vickrey Auction

    exoboot_remote  - GRPC communication with exoboot_wrapper on rpi
    bertec          - Remote control of Bertec treadmill
    """
    def __init__(self, exoboot_remote_client, bertec):
        super().__init__(name='Vickrey', exoboot_remote_client=exoboot_remote_client, bertec=bertec)

    def build(self):
        self.sm.statemachine = VickreyStateMachine(self.sm)

        # Vickrey bids
        self.sm.previous_bid = ''
        self.sm.bid = ''

        # Survey
        self.sm.enjoyment = 0
        self.sm.rpe = 0

        label_fontsize = '50'

        # Create Screens
        dummyscreen = Screen(name="dummy")

        pushtostartscreen = buildpushtostartscreen(self.sm, label_fontsize)

        numpad = buildNumPadScreen(self.sm)

        survey = buildsurveyscreen(self.sm)

        # Result screens: 4 cases
        self.sm.continuewalkingscreen = Screen(name="continuewalkingscreen")
        self.sm.continuewalkingscreen.label = Label(text='', font_size=label_fontsize)
        self.sm.continuewalkingscreen.add_widget(self.sm.continuewalkingscreen.label)
        self.sm.continuewalkingscreen.on_enter = partial(result_screens_schedule, self.sm)

        self.sm.startwalkingscreen = Screen(name="startwalkingscreen")
        self.sm.startwalkingscreen.label = Label(text='', font_size=label_fontsize)
        self.sm.startwalkingscreen.add_widget(self.sm.startwalkingscreen.label)
        self.sm.startwalkingscreen.on_enter = partial(result_screens_schedule, self.sm)

        self.sm.stopwalkingscreen = Screen(name="stopwalkingscreen")
        self.sm.stopwalkingscreen.label = Label(text='', font_size=label_fontsize)
        self.sm.stopwalkingscreen.add_widget(self.sm.stopwalkingscreen.label)
        self.sm.stopwalkingscreen.on_enter = partial(result_screens_schedule, self.sm)

        self.sm.continuesittingscreen = Screen(name="continuesittingscreen")
        self.sm.continuesittingscreen.label = Label(text='', font_size=label_fontsize)
        self.sm.continuesittingscreen.add_widget(self.sm.continuesittingscreen.label)
        self.sm.continuesittingscreen.on_enter = partial(result_screens_schedule, self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreen)
        self.sm.add_widget(numpad)
        self.sm.add_widget(survey)
        self.sm.add_widget(self.sm.continuewalkingscreen)
        self.sm.add_widget(self.sm.startwalkingscreen)
        self.sm.add_widget(self.sm.stopwalkingscreen)
        self.sm.add_widget(self.sm.continuesittingscreen)

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreen"

        return self.sm
    
# class VASGUI(BaseGui):
#     """
#     Creates screen manager to run Vickrey Auction

#     exoboot_remote  - GRPC communication with exoboot_wrapper on rpi
#     bertec          - Remote control of Bertec treadmill
#     """
#     def __init__(self):
#         super().__init__(self, 'VAS')

#     def build(self):
#         # State machine
#         self.sm.statemachine = VASStateMachine(self.sm)

#         label_fontsize = '50'

#         # Create Screens
#         dummyscreen = Screen(name="dummy")

#         # TODO VAS pushtostartscreen
#         pushtostartscreen = buildpushtostartscreen(self.sm, label_fontsize)

#         vasscreen = VAS_GUIApp(self.sm).build()

#         finishscreen = Screen(name='finishscreen')
#         # TODO add kill method

#         # Add screens to ScreenManager
#         self.sm.add_widget(dummyscreen)
#         self.sm.add_widget(pushtostartscreen)
#         self.sm.add_widget(vasscreen)
#         self.sm.add_widget(finishscreen)

#         # Switch from dummy to startscreen to run on_enter
#         self.sm.current = "pushtostartscreen"

#         return self.sm
