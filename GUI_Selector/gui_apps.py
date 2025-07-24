import re, csv
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

from shared_files.filing_cabinet_regex import build_filename
from constants import *

from gui_files.shared_screens import buildbatteryscreen
from gui_files.vickrey_gui.vickrey_screens import (
    buildpushtostartscreen,
    buildNumPadScreen,
    buildsurveyscreen,
    buildresultscreen,
)
from gui_files.vas_gui.vas_screens import (
    buildpushtostartscreenvas,
    buildwaitingscreenvas,
    buildvasscreen,
    buildbreakscreenvas,
    buildfinishscreenvas,
)
from gui_files.jnd_gui.jnd_screens import (
    buildpushtostartscreenjnd,
    buildwaitingscreenjnd,
    buildsplitlegscreen,
    buildsamelegscreen,
    buildfinishscreenjnd,
)
from gui_files.pref_gui.pref_screens import (
    buildpushtostartscreenpref,
    buildwaitingscreenpref,
    buildwalkscreenpref,
    buildsliderscreenpref,
    buildbtnscreenpref,
    buildfinishscreenpref,
    builddialscreenpref,
)
from gui_files.acclimation_gui.acclimation_screens import (
    buildpushtostartscreenaccl,
    buildsliderscreenaccl,
    buildfinishscreenaccl,
)
from gui_files.controlpanel_gui.controlpanel_screens import buildcontrolpanel
from gui_files.speedfinder_gui.speedfinder_screens import (
    buildpushtostartscreensf,
    buildspeedfinderscreen,
    buildfinishscreensf,
)

from statemachine import (
    VickreyStateMachine,
    VASStateMachine,
    JNDStateMachine,
    PrefStateMachine,
    AcclimationStateMachine,
    ControlPanelStateMachine,
    SpeedFinderStateMachine,
)


class BaseGui(App):
    def __init__(
        self,
        name,
        exoboot_remote,
        filingcabinet,
        file_prefix,
        current_date,
        bertec,
        vicon,
    ):
        super().__init__()
        self.sm = ScreenManager()
        self.sm.name = name

        # Set Exoboot remote client
        self.sm.exoboot_remote = exoboot_remote

        # Pause Exos and set torques
        self.sm.exoboot_remote.set_pause(mybool=True)

        # Set FilingCabinet
        self.sm.filingcabinet = filingcabinet

        # Save file_prefix
        self.sm.file_prefix = file_prefix
        self.sm.current_date = current_date

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
            self.bertec.write_command(
                0, 0, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT
            )
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

    def __init__(
        self,
        exoboot_remote=None,
        filingcabinet=None,
        file_prefix=None,
        current_date=None,
        bertec=None,
        vicon=None,
        condition1=None,
        usebackup=False,
        allow_check_batteries=True,
        subject_dict=None,
        **kwargs,
    ):
        super().__init__(
            "VICKREY",
            exoboot_remote,
            filingcabinet,
            file_prefix,
            current_date,
            bertec,
            vicon,
        )
        self.trial_cond = condition1
        self.usebackup = usebackup
        self.sm.allow_check_batteries = allow_check_batteries
        self.subject_dict = subject_dict

        # Get info from subject_dict
        self.sm.peak_torque = (
            0 if self.trial_cond in ["WNE", "NPO"] else self.subject_dict["pref_torque"]
        )
        self.sm.bertec_speed = subject_dict["bertec_speed"]
        self.sm.squeeze = subject_dict["squeeze"]

    def build(self):
        # Vickrey bids
        self.sm.previous_bid = ""
        self.sm.bid = ""

        # Survey
        self.sm.enjoyment = 0
        self.sm.rpe = 0

        # Statemachine
        self.sm.statemachine = VickreyStateMachine(
            self.sm, num_robobidders=NUM_ROBOBIDDERS
        )

        # Load existing or create new backup
        usebackup = self.usebackup
        try:
            if self.usebackup:
                # Get backup from filingcabinet
                auctionbackup = self.sm.filingcabinet.getpath("auction")

                # csv reader
                reader = csv.reader(open(auctionbackup), delimiter=",")
                next(reader)  # Skip header

                # Load in most recent auction
                states = {
                    "t": 0,
                    "state": False,
                    "prev_state": False,
                    "total_winnings": 0,
                    "robostates": [],
                }
                for auction in reader:
                    states["t"] = int(auction[0])
                    states["prev_state"] = states["state"]
                    states["state"] = auction[2] in ["True"]
                    states["total_winnings"] = float(auction[4])
                    states["robostates"] = auction[5::]

                self.sm.statemachine.loadstate(states)

                if self.sm.statemachine.state:
                    # Start Vicon
                    recording_name = "{}_t{}".format(
                        self.file_prefix,
                        int(self.sm.statemachine.auction_tally * ROBOWALK_DUR),
                    )
                    # get timestamp of vicon recording
                    start_recording_stamp = datetime.datetime.now(
                        tz=DETROIT_TIMEZONE
                    ).strftime(DATETIME_FORMAT_LESS_SEC)
                    file_description = f"Current date:{self.sm.current_date}. Start recording date:{start_recording_stamp}"
                    self.sm.vicon.start_recording(
                        fileNameIn=recording_name, fileDescription=file_description
                    )

                    # Start exo logging
                    self.sm.exoboot_remote.set_log(mybool=False)
        except:
            usebackup = False

        if not usebackup:
            # Create new file
            auctionname = auctionname = build_filename(
                format=FILENAME_FORMAT,
                PREFIX=self.sm.file_prefix,
                DATE=self.sm.current_date,
                SUFFIX="auction",
                EXT="csv",
            )
            auctionpath = self.sm.filingcabinet.newfile(auctionname, uid="auction")

            with open(auctionpath, "a", newline="") as f:
                header = [
                    "t",
                    "subject_bid",
                    "user_win_flag",
                    "current_payout",
                    "total_winnings",
                ]
                for i in range(NUM_ROBOBIDDERS):
                    header.extend(
                        ["robo{}_state_end".format(i), "robo{}_state_begin".format(i)]
                    )
                csv.writer(f).writerow(header)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreen, self.sm.startbtn = buildpushtostartscreen(self.sm)
        numpadscreen = buildNumPadScreen(self.sm)
        surveyscreen = buildsurveyscreen(self.sm)
        self.sm.resultscreen = buildresultscreen(self.sm)
        self.sm.batteryscreen = buildbatteryscreen(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreen)
        self.sm.add_widget(numpadscreen)
        self.sm.add_widget(surveyscreen)
        self.sm.add_widget(self.sm.resultscreen)
        self.sm.add_widget(self.sm.batteryscreen)

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreen"

        return self.sm


class VASGUI(BaseGui):
    """
    Creates screen manager to run Vickrey Auction

    exoboot_remote  - GRPC communication with exoboot_wrapper on rpi
    bertec          - Remote control of Bertec treadmill
    """

    def __init__(
        self,
        exoboot_remote=None,
        filingcabinet=None,
        file_prefix=None,
        current_date=None,
        bertec=None,
        vicon=None,
        usebackup=None,
        allow_check_batteries=True,
        subject_dict=None,
        **kwargs,
    ):
        super().__init__(
            "VAS",
            exoboot_remote,
            filingcabinet,
            file_prefix,
            current_date,
            bertec,
            vicon,
        )
        self.usebackup = usebackup
        self.sm.allow_check_batteries = allow_check_batteries
        self.subject_dict = subject_dict

        # Parse trial condition and description
        self.sm.desc_num = int("".join(re.findall(r"\d+", kwargs["condition2"])))

        # Get info from subject_dict
        self.sm.bertec_speed = subject_dict["bertec_speed"]
        self.sm.squeeze = subject_dict["squeeze"]
        self.sm.EPO_MV = subject_dict["EPO_MV"]
        self.sm.NPO_MV = subject_dict["NPO_MV"]
        self.sm.vas_seed = subject_dict["vas_seed"]

    def build(self):
        # State machine
        self.sm.statemachine = VASStateMachine(self.sm, self.subject_dict)

        # Load existing or create new backup
        usebackup = self.usebackup
        try:
            if self.usebackup:
                # Load backup into filingcabinet
                vasresultsbackup = self.sm.filingcabinet.getpath("vasresults")

                # Load backup into statemachine
                reader = csv.reader(open(vasresultsbackup), delimiter=",")
                next(reader)  # Skip header

                btpcompleted = []
                for btpline in reader:
                    btp = [int(val) for val in btpline[0:3]]
                    btpcompleted.append(btp)

                self.sm.statemachine.loadstate(btpcompleted)
        except:
            usebackup = False

        if not usebackup:
            # Create new file
            vasresultsname = build_filename(
                format=FILENAME_FORMAT,
                PREFIX=self.sm.file_prefix,
                DATE=self.sm.current_date,
                SUFFIX="vasresults",
                EXT="csv",
            )
            vasresultspath = self.sm.filingcabinet.newfile(
                vasresultsname, uid="vasresults"
            )

            with open(vasresultspath, "a", newline="") as f:
                header = ["btn_option", "trial", "pres"]
                for i in range(20):  # TODO remove constant 20
                    header.append("torque{}".format(i))
                    header.append("mv{}".format(i))
                csv.writer(f).writerow(header)

        # Start Vicon Recording
        b, t, p = self.sm.statemachine.peak_btp()
        suffix = "B{}_T{}_P{}".format(b, t, p)
        recording_name = build_filename(
            format=FILENAME_FORMAT_LESS_EXT,
            PREFIX=self.sm.file_prefix,
            DATE=self.sm.current_date,
            SUFFIX=suffix,
        )

        start_recording_stamp = datetime.datetime.now(tz=DETROIT_TIMEZONE).strftime(
            DATETIME_FORMAT_LESS_SEC
        )
        file_description = f"Current date:{self.sm.current_date}. Start recording date:{start_recording_stamp}"
        self.sm.vicon.start_recording(
            fileNameIn=recording_name, fileDescription=file_description
        )

        self.sm.exoboot_remote.set_log(mybool=False)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreen = buildpushtostartscreenvas()
        self.sm.waitingscreen = buildwaitingscreenvas(self.sm)
        finishscreen = buildfinishscreenvas(self.sm)
        breakscreen = buildbreakscreenvas(self.sm)
        self.sm.batteryscreen = buildbatteryscreen(self.sm)

        vasscreen = Screen(name="vasscreen")
        vasscreen.sm = self.sm
        vasscreen.on_pre_enter = partial(
            buildvasscreen, self.sm, vasscreen, False, None
        )

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreen)
        self.sm.add_widget(vasscreen)
        self.sm.add_widget(self.sm.waitingscreen)
        self.sm.add_widget(breakscreen)
        self.sm.add_widget(finishscreen)
        self.sm.add_widget(self.sm.batteryscreen)

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreen"

        return self.sm


class JNDGUI(BaseGui):
    """
    Creates screen manager to run Vickrey Auction

    exoboot_remote  - GRPC communication with exoboot_wrapper on rpi
    bertec          - Remote control of Bertec treadmill
    """

    def __init__(
        self,
        exoboot_remote=None,
        filingcabinet=None,
        file_prefix=None,
        current_date=None,
        bertec=None,
        vicon=None,
        condition1=None,
        condition2=None,
        usebackup=False,
        allow_check_batteries=True,
        subject_dict=None,
        **kwargs,
    ):
        super().__init__(
            "JND",
            exoboot_remote,
            filingcabinet,
            file_prefix,
            current_date,
            bertec,
            vicon,
        )
        self.jnd_type = condition1
        self.which_comparitor = condition2.upper()
        self.usebackup = usebackup
        self.sm.allow_check_batteries = allow_check_batteries
        self.subject_dict = subject_dict

        # Get info from subject_dict
        self.sm.bertec_speed = subject_dict["bertec_speed"]
        self.sm.squeeze = subject_dict["squeeze"]

    def build(self):
        # Statemachine
        self.sm.statemachine = JNDStateMachine(
            self.sm, jnd_type=self.jnd_type, which_comparitor=self.which_comparitor
        )

        # Load existing or create new backup
        usebackup = self.usebackup
        try:
            if self.usebackup:
                if self.which_comparitor == "UNIFORM":
                    # Load backup into filingcabinet
                    comparisonbackup = self.sm.filingcabinet.getpath("comparison")

                    # Load backup into statemachine
                    reader = csv.reader(open(comparisonbackup), delimiter=",")
                    next(reader)  # Skip Header

                    pres = 0
                    for comp in reader:
                        pres = int(comp[0])

                    self.sm.statemachine.loadstate(pres)

                elif self.which_comparitor == "STAIR":
                    # Create new file for JND back-up logging with full details (DO THIS NO MATTER WHAT)
                    comparisonname = build_filename(
                        format=FILENAME_FORMAT,
                        PREFIX=self.sm.file_prefix,
                        DATE=self.sm.current_date,
                        SUFFIX="comparison",
                        EXT="csv",
                    )
                    comparisonpath = self.sm.filingcabinet.newfile(
                        comparisonname, uid="comparison"
                    )
                    with open(comparisonpath, "a", newline="") as f:
                        csv.writer(f).writerow(
                            [
                                "pres",
                                "mode",
                                "T_ref",
                                "T_comp",
                                "truth",
                                "peak_torque_ind",
                                "converged_flag",
                                "consec_correct_counter",
                                "step_size",
                                "convergence_attempts",
                            ]
                        )
        except:
            usebackup = False

        if not usebackup:
            # Create new file
            comparisonname = build_filename(
                format=FILENAME_FORMAT,
                PREFIX=self.sm.file_prefix,
                DATE=self.sm.current_date,
                SUFFIX="comparison",
                EXT="csv",
            )
            comparisonpath = self.sm.filingcabinet.newfile(
                comparisonname, uid="comparison"
            )

            if self.which_comparitor == "STAIR":
                with open(comparisonpath, "a", newline="") as f:
                    csv.writer(f).writerow(
                        [
                            "pres",
                            "mode",
                            "T_ref",
                            "T_comp",
                            "truth",
                            "peak_torque_ind",
                            "converged_flag",
                            "consec_correct_counter",
                            "step_size",
                            "convergence_attempts",
                        ]
                    )

            elif self.which_comparitor == "UNIFORM":
                with open(comparisonpath, "a", newline="") as f:
                    csv.writer(f).writerow(
                        ["pres", "prop", "T_ref", "T_comp", "truth", "higher"]
                    )

        # Start Vicon
        suffix = "walk{}".format(self.sm.statemachine.walknum)
        recording_name = build_filename(
            format=FILENAME_FORMAT_LESS_EXT,
            PREFIX=self.sm.file_prefix,
            DATE=self.sm.current_date,
            SUFFIX=suffix,
        )

        start_recording_stamp = datetime.datetime.now(tz=DETROIT_TIMEZONE).strftime(
            DATETIME_FORMAT_LESS_SEC
        )
        file_description = f"Current date:{self.sm.current_date}. Start recording date:{start_recording_stamp}"
        self.sm.vicon.start_recording(
            fileNameIn=recording_name, fileDescription=file_description
        )

        # Start exo logging
        self.sm.exoboot_remote.set_log(mybool=False)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreenjnd = buildpushtostartscreenjnd()
        waitingscreenjnd = buildwaitingscreenjnd(self.sm)
        finishscreenjnd = buildfinishscreenjnd(self.sm)
        self.sm.batteryscreen = buildbatteryscreen(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreenjnd)
        self.sm.add_widget(waitingscreenjnd)
        self.sm.add_widget(finishscreenjnd)
        self.sm.add_widget(self.sm.batteryscreen)

        # Split or same trial cond
        if self.jnd_type == "SPLITLEG":
            splitlegscreen = buildsplitlegscreen(self.sm)
            self.sm.add_widget(splitlegscreen)
        elif self.jnd_type == "SAMELEG":
            samelegscreen = buildsamelegscreen(self.sm)
            self.sm.add_widget(samelegscreen)
        else:
            print("invalid JND trial type selected")
            quit()

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreenjnd"

        return self.sm


class PREFGUI(BaseGui):
    def __init__(
        self,
        exoboot_remote=None,
        filingcabinet=None,
        file_prefix=None,
        current_date=None,
        bertec=None,
        vicon=None,
        condition1=None,
        subject_dict=None,
        **kwargs,
    ):
        super().__init__(
            "PREFERENCE",
            exoboot_remote,
            filingcabinet,
            file_prefix,
            current_date,
            bertec,
            vicon,
        )
        self.pref_type = condition1
        self.subject_dict = subject_dict

        # Get info from subject_dict
        self.sm.bertec_speed = subject_dict["bertec_speed"]
        self.sm.squeeze = subject_dict["squeeze"]

    def build(self):
        self.sm.statemachine = PrefStateMachine(self.sm, pref_type=self.pref_type)

        # Start Vicon
        suffix = "walk{}".format(self.sm.statemachine.pres)
        recording_name = build_filename(
            format=FILENAME_FORMAT_LESS_EXT,
            PREFIX=self.sm.file_prefix,
            DATE=self.sm.current_date,
            SUFFIX=suffix,
        )

        start_recording_stamp = datetime.datetime.now(tz=DETROIT_TIMEZONE).strftime(
            DATETIME_FORMAT_LESS_SEC
        )
        file_description = f"Current date:{self.sm.current_date}. Start recording date:{start_recording_stamp}"
        self.sm.vicon.start_recording(
            fileNameIn=recording_name, fileDescription=file_description
        )

        # Start logging
        self.sm.exoboot_remote.set_log(mybool=False)

        # Create Screens
        dummyscreen = Screen(name="dummy")
        pushtostartscreenpref = buildpushtostartscreenpref(self.sm)
        walkscreenpref = buildwalkscreenpref(self.sm)
        waitingscreenpref = buildwaitingscreenpref(self.sm)
        finishscreenpref = buildfinishscreenpref(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(pushtostartscreenpref)
        self.sm.add_widget(walkscreenpref)
        self.sm.add_widget(waitingscreenpref)
        self.sm.add_widget(finishscreenpref)

        # Split or same trial cond
        if self.pref_type == "SLIDER":
            sliderscreenpref = buildsliderscreenpref(self.sm)
            self.sm.add_widget(sliderscreenpref)
            self.sm.prefscreen = sliderscreenpref
        elif self.pref_type == "BUTTON":
            btnscreenpref = Screen(name="btnscreen")
            btnscreenpref.sm = self.sm
            buildbtnscreenpref(self.sm, btnscreenpref)
            self.sm.add_widget(btnscreenpref)
            self.sm.prefscreen = btnscreenpref
        elif self.pref_type == "DIAL":
            dialscreenpref = builddialscreenpref(self.sm)
            self.sm.add_widget(dialscreenpref)
            self.sm.dialscreenpref = dialscreenpref
        else:
            print("invalid pref trial type selected")
            quit()

        # Switch from dummy to startscreen to run on_enter
        self.sm.current = "pushtostartscreenpref"

        return self.sm


class AcclimationGUI(BaseGui):
    def __init__(
        self,
        exoboot_remote=None,
        filingcabinet=None,
        file_prefix=None,
        current_date=None,
        bertec=None,
        vicon=None,
        subject_dict=None,
        **kwargs,
    ):
        super().__init__(
            "ACCLIMATION",
            exoboot_remote,
            filingcabinet,
            file_prefix,
            current_date,
            bertec,
            vicon,
        )
        self.sm.subject_dict = subject_dict

        # Get info from subject_dict
        self.sm.bertec_speed = subject_dict["bertec_speed"]
        self.sm.squeeze = subject_dict["squeeze"]

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


class ControlPanelGUI(BaseGui):
    def __init__(
        self,
        exoboot_remote=None,
        filingcabinet=None,
        file_prefix=None,
        current_date=None,
        bertec=None,
        vicon=None,
        subject_dict=None,
        **kwargs,
    ):
        super().__init__(
            "CONTROLPANEL",
            exoboot_remote,
            filingcabinet,
            file_prefix,
            current_date,
            bertec,
            vicon,
        )
        self.sm.subject_dict = subject_dict

        self.sm.bertec_speed = subject_dict["bertec_speed"]
        self.sm.squeeze = subject_dict["squeeze"]

    def build(self):
        self.sm.statemachine = ControlPanelStateMachine(self.sm)

        # Create screens
        dummyscreen = Screen(name="dummy")
        self.sm.controlpanel = buildcontrolpanel(self.sm)

        # Add screens to ScreenManager
        self.sm.add_widget(dummyscreen)
        self.sm.add_widget(self.sm.controlpanel)

        self.sm.current = "controlpanel"

        return self.sm


class SpeedFinderGUI(BaseGui):
    pass
    # def __init__(self, exoboot_remote, bertec):
    #     super().__init__(name='SPEEDFINDER', exoboot_remote=exoboot_remote, bertec=bertec)

    # def build(self):
    #     self.sm.statemachine = SpeedFinderStateMachine(self.sm)

    #     # Create Screens
    #     dummyscreen = Screen(name="dummy")
    #     pushtostartscreensf = buildpushtostartscreensf()
    #     speedfinderscreen = buildspeedfinderscreen(self.sm)
    #     finishscreensf = buildfinishscreensf(self.sm)

    #     # Add screens to ScreenManager
    #     self.sm.add_widget(dummyscreen)
    #     self.sm.add_widget(pushtostartscreensf)
    #     self.sm.add_widget(speedfinderscreen)
    #     self.sm.add_widget(finishscreensf)

    #     # Switch from dummy to startscreen to run on_enter
    #     self.sm.current = "pushtostartscreensf"

    #     return self.sm
