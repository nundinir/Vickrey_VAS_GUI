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

from vickrey_screens import buildpushtostartscreen, buildNumPadScreen, buildsurveyscreen, buildresultscreen
from vas_screens import buildpushtostartscreenvas, buildwaitingscreenvas, buildvasscreen, buildfinishscreenvas
from jnd_screens import buildpushtostartscreenjnd, buildwaitingscreenjnd, buildsplitlegscreen, buildsamelegscreen, buildfinishscreenjnd
from pref_screens import buildpushtostartscreenpref, buildwaitingscreenpref, buildsliderscreenpref, buildbtnscreenpref, buildfinishscreenpref
from acclimation_screens import buildpushtostartscreenaccl, buildsliderscreenaccl, buildfinishscreenaccl

from vas_schedules import *
from statemachine import VickreyStateMachine, VASStateMachine, JNDStateMachine, PrefStateMachine, AcclimationStateMachine

class BaseGui(App):
    def __init__(self, name, exoboot_remote_client, bertec):
        super().__init__()
        self.sm = ScreenManager()
        self.sm.name = name

        # Set Exoboot remote client
        self.sm.exoboot_remote = exoboot_remote_client

        # Pause Exos and set torques
        self.sm.exoboot_remote.set_pause(mybool=True)

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
        super().__init__(name='VICKREY', exoboot_remote_client=exoboot_remote_client, bertec=bertec)

    def build(self):
        self.sm.statemachine = VickreyStateMachine(self.sm)

        # Vickrey bids
        self.sm.previous_bid = ''
        self.sm.bid = ''

        # Survey
        self.sm.enjoyment = 0
        self.sm.rpe = 0

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreen = buildpushtostartscreen()
        numpadscreen = buildNumPadScreen(self.sm)
        surveyscreen = buildsurveyscreen(self.sm)
        self.sm.resultscreen = buildresultscreen(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreen)
        self.sm.add_widget(numpadscreen)
        self.sm.add_widget(surveyscreen)
        self.sm.add_widget(self.sm.resultscreen)

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreen"

        return self.sm
    
class VASGUI(BaseGui):
    """
    Creates screen manager to run Vickrey Auction

    exoboot_remote  - GRPC communication with exoboot_wrapper on rpi
    bertec          - Remote control of Bertec treadmill
    """
    def __init__(self, startstamp, exoboot_remote_client, bertec):
        super().__init__(name='VAS', exoboot_remote_client=exoboot_remote_client, bertec=bertec)
        self.startstamp = startstamp

    def build(self):
        # State machine
        self.sm.statemachine = VASStateMachine(self.sm, self.startstamp)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreen = buildpushtostartscreenvas()
        waitingscreen = buildwaitingscreenvas(self.sm)
        finishscreen = buildfinishscreenvas(self.sm)

        vasscreen = Screen(name='vasscreen')
        vasscreen.sm = self.sm
        vasscreen.on_pre_enter = partial(buildvasscreen, self.sm, vasscreen, False, None)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreen)
        self.sm.add_widget(vasscreen)
        self.sm.add_widget(waitingscreen)
        self.sm.add_widget(finishscreen)

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreen"

        return self.sm

class JNDGUI(BaseGui):
    """
    Creates screen manager to run Vickrey Auction

    exoboot_remote  - GRPC communication with exoboot_wrapper on rpi
    bertec          - Remote control of Bertec treadmill
    """
    def __init__(self, exoboot_remote_client, bertec, jnd_type):
        super().__init__(name='JND', exoboot_remote_client=exoboot_remote_client, bertec=bertec)
        self.jnd_type = jnd_type

    def build(self):
        self.sm.statemachine = JNDStateMachine(self.sm, jnd_type=self.jnd_type)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreenjnd = buildpushtostartscreenjnd()
        waitingscreenjnd = buildwaitingscreenjnd(self.sm)
        finishscreenjnd = buildfinishscreenjnd(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreenjnd)
        self.sm.add_widget(waitingscreenjnd)
        self.sm.add_widget(finishscreenjnd)

        # Split or same trial cond
        match self.jnd_type:
            case "SPLITLEG":
                splitlegscreen = buildsplitlegscreen(self.sm)
                self.sm.add_widget(splitlegscreen)
            case "SAMELEG":
                samelegscreen = buildsamelegscreen(self.sm)
                self.sm.add_widget(samelegscreen)

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreenjnd"

        return self.sm


class PREFGUI(BaseGui):
    def __init__(self, exoboot_remote_client, bertec, pref_type):
        super().__init__(name='TorquePreference', exoboot_remote_client=exoboot_remote_client, bertec=bertec)
        self.pref_type = pref_type

    def build(self):
        self.sm.statemachine = PrefStateMachine(self.sm, pref_type=self.pref_type)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreenpref = buildpushtostartscreenpref(self.sm)
        waitingscreenpref = buildwaitingscreenpref(self.sm)
        finishscreenpref = buildfinishscreenpref(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreenpref)
        self.sm.add_widget(waitingscreenpref)
        self.sm.add_widget(finishscreenpref)

        # Split or same trial cond
        match self.pref_type:
            case "SLIDER":
                sliderscreenpref = buildsliderscreenpref(self.sm)
                self.sm.add_widget(sliderscreenpref)
                self.sm.prefscreen = sliderscreenpref
            case "BTN":
                btnscreenpref = Screen(name="btnscreen")
                btnscreenpref.sm = self.sm
                buildbtnscreenpref(self.sm, btnscreenpref)
                self.sm.add_widget(btnscreenpref)
                self.sm.prefscreen = btnscreenpref

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreenpref"

        return self.sm
    

class AcclimationGUI(BaseGui):
    def __init__(self, exoboot_remote_client, bertec, pref_type):
        super().__init__(name='ACCLIMATION', exoboot_remote_client=exoboot_remote_client, bertec=bertec)
        self.pref_type = pref_type

    def build(self):
        self.sm.statemachine = AcclimationStateMachine(self.sm)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreenaccl = buildpushtostartscreenaccl()
        sliderscreen = buildsliderscreenaccl(self.sm)
        self.sm.sliderscreen = sliderscreen
        finishscreenaccl = buildfinishscreenaccl(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreenaccl)
        self.sm.add_widget(sliderscreen)
        self.sm.add_widget(finishscreenaccl)

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreenaccl"

        return self.sm