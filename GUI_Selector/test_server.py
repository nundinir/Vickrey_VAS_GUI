import sys, csv, copy, time, socket, threading

from typing import Type
from random import randint
from collections import deque

from shared_files.filing_cabinet import FilingCabinet
from shared_files.filing_cabinet_regex import build_prefix
from exoboot_remote.exoboot_remote_control import ExobootRemoteServerThread

from constants import SUBJECT_DATA_PATH, DETROIT_TIMEZONE, DATETIME_FORMAT_LESS_SEC


class DumbBertec:
    """
    Very dumb Bertec
    """

    def __init__(self, viconPC_IP="141.212.77.30", viconPC_BertecPort=4000):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def __del__(self):
        pass

    def _update(self):
        pass

    def _update_odometer(self):
        pass

    def _calculate_vertical_velocity(self):
        return 7456

    def _calculate_absolute_velocity(self):
        return 9345

    @property
    def distance(self):
        return 11

    @property
    def elevation(self):
        return 123

    @property
    def speed(self):
        return 345

    def get_treadmill_incline(self):
        return 98

    def get_belt_speed(self):
        return 75

    def reset_odometer(self):
        pass

    def write_command(
        self, speedR, speedL, incline=None, accR=0.2, accL=0.2, maxVel=9001, minVel=-0
    ):
        print("BERTEC WRITE: ", speedR, speedL, "ACCELS: ", accR, accL)
        pass


class DumbVicon:
    """
    A class for managing starting and stopping Vicon recordings
    over the network.
    Just kidding this is the dumb version
    To use this class, make sure you've armed vicon and enabled network triggers.
    See this page for more info: https://docs.vicon.com/display/Nexus213/Automatically+start+and+stop+capture
    Kevin Best 10/22
    """

    # Local hostname: ROB-ROUSE-VICON.adsroot.itcs.umich.edu
    # IP address: 141.212.77.30
    def __init__(self, viconPC_IP="141.212.77.30", viconPC_port=30, viconPath="E:"):

        # self.destinationIP = viconPC_IP
        # self.destinationPort = viconPC_port
        # self.viconPath = viconPath
        # self.delayPriorToRecord_ms = 1
        # self.fileName = ''
        # self.fileDescription = ''

        # # Setup UDP
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pass

    def start_recording(
        self,
        fileNameIn: str,
        fileDescription: str = "A vicon recording",
        notes: str = "Vicon triggered from python over UDP",
    ):
        """
        Send command to vicon to start file recording.
        Requires 2 inputs:
            fileNameIn: File name to be used on the vicon PC
            fileDescription: Any notes you want to add to your file. Fills the description field on vicon
        """
        print("VICON_START: {}".format(fileNameIn))
        # msg = self._assemble_payload_start(fileNameIn, fileDescription)
        # self.sock.sendto(msg, (self.destinationIP, self.destinationPort))
        pass

    def stop_recording(self):
        print("VICON_STOP")
        # msg = self._assemble_payload_stop()
        # self.sock.sendto(msg, (self.destinationIP, self.destinationPort))
        pass

    def _assemble_payload_start(self, fileNameIn, fileDescription, notes):
        """
        Creates the proper XML string to trigger vicon.
        More documentation available here:
           https://docs.vicon.com/pages/viewpage.action?pageId=152010925
        """

        # Update self
        self.fileName = fileNameIn
        self.fileDescription = fileDescription

        # Construct the string
        self.notes = notes
        cmdHeader = (
            '\n<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<CaptureStart>\n'
        )
        nameLine = '<Name VALUE="{}"/>\n'.format(self.fileName)
        notesLine = '<Notes VALUE="{}"/>\n'.format(self.notes)
        descriptionLine = '<Description VALUE="{}"/>\n'.format(self.fileDescription)
        databasePathLine = '<DatabasePath VALUE="{}"/>\n'.format(self.viconPath)
        delayLine = '<Delay VALUE="{}"/>\n'.format(self.delayPriorToRecord_ms)
        packetIDline = '<PacketID VALUE="{}"/>\n'.format(randint(1, 2**16))
        suffixLine = "</CaptureStart>"
        fullPayloadString = (
            cmdHeader
            + nameLine
            + notesLine
            + descriptionLine
            + databasePathLine
            + delayLine
            + packetIDline
            + suffixLine
        )
        # print(fullPayloadString)

        # Convert string to utf-8 bytes string to send over network.
        return bytes(fullPayloadString, "utf-8")

    def _assemble_payload_stop(self):
        """
        Creates the proper XML string to stop vicon.
        More documentation available here:
           https://docs.vicon.com/pages/viewpage.action?pageId=152010925
        """

        cmdHeader = '\n<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<CaptureStop RESULT="SUCCESS">\n'
        nameLine = '<Name VALUE="{}"/>\n'.format(self.fileName)
        databasePathLine = '<DatabasePath VALUE="{}"/>\n'.format(self.viconPath)
        delayLine = '<Delay VALUE="{}"/>\n'.format(self.delayPriorToRecord_ms)
        packetIDline = '<PacketID VALUE="{}"/>\n'.format(randint(1, 2**16))
        suffixLine = "</CaptureStop>"
        fullPayloadString = (
            cmdHeader
            + nameLine
            + databasePathLine
            + delayLine
            + packetIDline
            + suffixLine
        )
        # print(fullPayloadString)

        # Convert string to utf-8 bytes string to send over network.
        return bytes(fullPayloadString, "utf-8")


class DumbGSE:
    """
    Dumb gait state estimator
    Report torques set over GRPC
    """

    def __init__(self):
        self.peak_torque_left = 0
        self.peak_torque_right = 0

    def set_peak_torque_left(self, T):
        print("Set Peak Torque Left: {}".format(T))
        self.peak_torque_left = T

    def set_peak_torque_right(self, T):
        print("Set Peak Torque Right: {}".format(T))
        self.peak_torque_right = T


class DumbLoggingNexus:
    """
    Dumb Logging Nexus
    Set battery voltages to test battery check routine
    """

    def __init__(self):
        pass

    def get(self, threadname, field):
        if threadname == "exothread_left":
            if field == "battery_voltage":
                return 50 * 1000
            return -3
        elif threadname == "exothread_right":
            if field == "battery_voltage":
                return 72.72 * 1000
            return 72
        else:
            return -11


class DumbWrapper:
    """
    Minimally functioning "exoboot"
    """

    def __init__(
        self, subjectID, trial_type, condition1, condition2, usebackup, current_date
    ):
        self.startstamp = time.perf_counter()
        self.quit_event = threading.Event()
        self.pause_event = threading.Event()
        self.log_event = threading.Event()
        self.quit_event.set()
        self.pause_event.clear()
        self.log_event.clear()

        self.subjectID = subjectID
        self.trial_type = trial_type.upper()
        self.condition1 = condition1.upper()
        self.condition2 = condition2.upper()
        self.usebackup = usebackup in ["true", "True", "1", "yes", "Yes"]
        self.current_date = current_date

        self.file_prefix = build_prefix(
            SUBJECT=subjectID,
            TRIALTYPE=trial_type,
            CONDITION1=self.condition1,
            CONDITION2=self.condition2,
        )

        print("Subject: {}".format(self.subjectID))
        print("Trial Type: {}".format(self.trial_type))
        print("CONDITION1: {}".format(self.condition1))
        print("CONDITION2: {}".format(self.condition2))
        print("Usebackup: {}".format(self.usebackup))

        # Filing Cabinet
        use_for_dir = [subjectID, trial_type]
        self.filingcabinet = FilingCabinet(SUBJECT_DATA_PATH, *use_for_dir)
        if self.usebackup:
            loadstatus = self.filingcabinet.loadbackup(self.file_prefix, rule="newest")
            print(
                "Backup Load Status: {}".format("SUCCESS" if loadstatus else "FAILURE")
            )

        self.gse_thread = DumbGSE()

        self.loggingnexus = DumbLoggingNexus()

        self.remote_thread = ExobootRemoteServerThread(
            self,
            self.startstamp,
            self.filingcabinet,
            usebackup=self.usebackup,
            quit_event=self.quit_event,
            pause_event=self.pause_event,
            log_event=self.log_event,
        )
        self.remote_thread.set_target_IP("[::]:50051")
        self.remote_thread.start()

    def run(self):
        while self.quit_event.is_set():
            time.sleep(0.5)


if __name__ == "__main__":
    """
    Run test server
    """

    # TODO use in FilingCabinet
    import datetime, pytz, re

    tz = pytz.timezone("America/Detroit")
    formatter = "%Z_%Y_%m_%d_%H:%M:%S"

    start = time.perf_counter()
    now = datetime.datetime.now(tz).strftime(formatter)
    end = time.perf_counter()

    filename = "SUBJECT_{}_exothread_new.csv".format(now)
    filename = filename.replace("_new", "")
    print("FILENAME: ", filename)

    pattern = re.compile(r"\d{4}(.*)_")
    result = pattern.search(filename)
    print(filename[result.span()[0] : result.span()[1] - 1])

    try:
        assert len(sys.argv) - 1 == 5
        _, subjectID, trial_type, condition1, condition2, usebackup = sys.argv
        current_date = datetime.datetime.now(tz=DETROIT_TIMEZONE).strftime(
            DATETIME_FORMAT_LESS_SEC
        )
        dumb_wrapper = DumbWrapper(
            subjectID, trial_type, condition1, condition2, usebackup, current_date
        )
        dumb_wrapper.run()

    except KeyboardInterrupt:
        dumb_wrapper.quit_event.clear()
        print("Goodbye")
