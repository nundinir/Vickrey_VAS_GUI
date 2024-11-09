import csv
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

from constants import *

from vickrey_screens import buildpushtostartscreen, buildNumPadScreen, buildsurveyscreen, buildresultscreen
from vas_screens import buildpushtostartscreenvas, buildwaitingscreenvas, buildvasscreen, buildfinishscreenvas
from jnd_screens import buildpushtostartscreenjnd, buildwaitingscreenjnd, buildsplitlegscreen, buildsamelegscreen, buildfinishscreenjnd
from pref_screens import buildpushtostartscreenpref, buildwaitingscreenpref, buildsliderscreenpref, buildbtnscreenpref, buildfinishscreenpref, builddialscreenpref
from acclimation_screens import buildpushtostartscreenaccl, buildsliderscreenaccl, buildfinishscreenaccl
from speedfinder_screens import buildpushtostartscreensf, buildspeedfinderscreen, buildfinishscreensf

from statemachine import VickreyStateMachine, VASStateMachine, JNDStateMachine, PrefStateMachine, AcclimationStateMachine, SpeedFinderStateMachine

class BaseGui(App):
    def __init__(self, name, exoboot_remote_client, filingcabinet, file_prefix, bertec, vicon):
        super().__init__()
        self.sm = ScreenManager()
        self.sm.name = name

        # Set Exoboot remote client
        self.sm.exoboot_remote = exoboot_remote_client

        # Pause Exos and set torques
        self.sm.exoboot_remote.set_pause(mybool=True)

        # Set FilingCabinet
        self.sm.filingcabinet = filingcabinet

        # Save file_prefix
        self.sm.file_prefix = file_prefix

        # Bertec over network thread
        self.sm.bertec = bertec
        self.sm.bertec.start()

        # Vicon over network thread
        self.sm.vicon = vicon

        def on_request_close(self, *args):
            """
            Stop Bertec treadmill and close Bertec
            Shutdown exoboots remotely
            """
            print("Closing Bertec")
            self.bertec.write_command(0, 0, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
            self.bertec.stop()

            print("Stopping Vicon")
            self.vicon.stop_recording()

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
    def __init__(self, exoboot_remote_client, filingcabinet, file_prefix, bertec, vicon, usebackup=False):
        super().__init__("VICKREY", exoboot_remote_client, filingcabinet, file_prefix, bertec, vicon)
        self.usebackup = usebackup

    def build(self):
        # Vickrey bids
        self.sm.previous_bid = ''
        self.sm.bid = ''

        # Survey
        self.sm.enjoyment = 0
        self.sm.rpe = 0
        
        # Statemachine
        self.sm.statemachine = VickreyStateMachine(self.sm, num_robobidders=NUM_ROBOBIDDERS)

        # Load existing or create new backup
        usebackup = self.usebackup
        try:
            if self.usebackup:
                # Get backup from filingcabinet
                auctionbackup = self.sm.filingcabinet.getpath("auction")

                # csv reader
                reader = csv.reader(open(auctionbackup), delimiter=',')
                next(reader) # Skip header

                # Load in most recent auction
                states = {"t": 0, "state": False, "prev_state": False, "total_winnings": 0, "robostates": []}
                for auction in reader:
                    print("asdf", auction)
                    states["t"] = int(auction[0])
                    states["prev_state"] = states["state"]
                    states["state"] = auction[2] in ["True"]
                    states["total_winnings"] = float(auction[4])
                    states["robostates"] = auction[5::]
                
                print("wer", states)
                self.sm.statemachine.loadstate(states)
        except:
            usebackup = False

        if not usebackup:
            # Create new file
            auctionname = "{}_{}".format(self.sm.file_prefix, "auction")
            auctionpath = self.sm.filingcabinet.newfile(auctionname, "csv", dictkey="auction")

            with open(auctionpath, 'a', newline='') as f:
                header = ['t', 'subject_bid', 'user_win_flag', 'current_payout', 'total_winnings']
                for i in range(NUM_ROBOBIDDERS):
                    header.extend(["robo{}_state_end".format(i), "robo{}_state_begin".format(i)])
                csv.writer(f).writerow(header)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreen, self.sm.startbtn = buildpushtostartscreen(self.sm)
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
    def __init__(self, startstamp, exoboot_remote_client, filingcabinet, file_prefix, bertec, vicon, usebackup=None):
        super().__init__("VAS", exoboot_remote_client, filingcabinet, file_prefix, bertec, vicon)
        self.startstamp = startstamp
        self.usebackup = usebackup

    def build(self):
        # State machine
        self.sm.statemachine = VASStateMachine(self.sm, self.startstamp)

        # Load existing or create new backup
        usebackup = self.usebackup
        try:
            if self.usebackup:
                # Load backup into filingcabinet
                vasresultsbackup = self.sm.filingcabinet.getpath("vasresults")
                
                # Load backup into statemachine
                reader = csv.reader(open(vasresultsbackup), delimiter=',')
                next(reader) # Skip header

                btpcompleted = []
                for btpline in reader:
                    btp = [int(val) for val in btpline[0:3]]
                    btpcompleted.append(btp)

                self.sm.statemachine.loadstate(btpcompleted)
        except:
            usebackup = False
            
        if not usebackup:
            # Create new file
            vasresultsname = "{}_{}".format(self.sm.file_prefix, "vasresults")
            vasresultspath = self.sm.filingcabinet.newfile(vasresultsname, "csv", dictkey="vasresults")

            with open(vasresultspath, 'a', newline='') as f:
                header = ['btn_option', 'trial', 'pres']
                for i in range(20): # TODO remove constant 20
                    header.append('torque{}'.format(i))
                    header.append('mv{}'.format(i))
                csv.writer(f).writerow(header)

        # Start Vicon Recording
        b, t, p = self.sm.statemachine.peak_btp()
        recording_name = "{}_B{}_T{}_P{}".format(self.sm.file_prefix, b, t, p)
        self.sm.vicon.start_recording(recording_name)

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
    def __init__(self, exoboot_remote_client, filingcabinet, file_prefix, bertec, vicon, jnd_type, which_comparitor, usebackup=False):
        super().__init__('JND', exoboot_remote_client, filingcabinet, file_prefix, bertec, vicon)
        self.jnd_type = jnd_type
        self.which_comparitor = which_comparitor
        self.usebackup = usebackup

    def build(self):
        # Statemachine
        self.sm.statemachine = JNDStateMachine(self.sm, jnd_type=self.jnd_type, which_comparitor=self.which_comparitor)

        # Load existing or create new backup
        usebackup = self.usebackup
        try:
            if self.usebackup:
                # Load backup into filingcabinet
                comparisonbackup = self.sm.filingcabinet.getpath("comparison")

                # Load backup into statemachine
                reader = csv.reader(open(comparisonbackup), delimiter=',')
                next(reader) # Skip Header

                pres = 0
                for comp in reader:
                    pres = int(comp[0])

                self.sm.statemachine.loadstate(pres)
        except:
            usebackup = False

        if not usebackup:
            # Create new file
            comparisonname = "{}_{}".format(self.sm.file_prefix, "comparison")
            comparisonpath = self.sm.filingcabinet.newfile(comparisonname, "csv", dictkey="comparison")

            with open(comparisonpath, 'a', newline='') as f:
                csv.writer(f).writerow(['pres', 'prop', 'T_ref', 'T_comp', 'truth', 'higher'])

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
    def __init__(self, exoboot_remote, filingcabinet, file_prefix, bertec, vicon, trial_cond):
        super().__init__('TorquePreference', exoboot_remote, filingcabinet, file_prefix, bertec, vicon)
        self.pref_type = trial_cond

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
            case "BUTTON":
                btnscreenpref = Screen(name="btnscreen")
                btnscreenpref.sm = self.sm
                buildbtnscreenpref(self.sm, btnscreenpref)
                self.sm.add_widget(btnscreenpref)
                self.sm.prefscreen = btnscreenpref
            case "DIAL":
                dialscreenpref = builddialscreenpref(self.sm)
                self.sm.add_widget(dialscreenpref)
                self.sm.dialscreenpref = dialscreenpref

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreenpref"

        return self.sm


class AcclimationGUI(BaseGui):
    def __init__(self, exoboot_remote_client, bertec):
        super().__init__(name='ACCLIMATION', exoboot_remote_client=exoboot_remote_client, bertec=bertec)

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
    
class SpeedFinderGUI(BaseGui):
    def __init__(self, exoboot_remote_client, bertec):
        super().__init__(name='SPEEDFINDER', exoboot_remote_client=exoboot_remote_client, bertec=bertec)

    def build(self):
        self.sm.statemachine = SpeedFinderStateMachine(self.sm)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreensf = buildpushtostartscreensf()
        speedfinderscreen = buildspeedfinderscreen(self.sm)
        finishscreensf = buildfinishscreensf(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreensf)
        self.sm.add_widget(speedfinderscreen)
        self.sm.add_widget(finishscreensf)

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreensf"

        return self.sm
