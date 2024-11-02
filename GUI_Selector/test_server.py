import os, sys, time, copy, socket, threading
from typing import Type
from random import randint

from constants import *
from shared_files.SoftRTloop import FlexibleSleeper
from shared_files.BaseExoThread import BaseThread
from shared_files.LoggingClass import FilingCabinet, LoggingNexus
from exoboot_remote.exoboot_remote_control import ExobootRemoteServerThread

"""LoggingNexus Fields for each thread"""
GENERAL_FIELDS = ['pitime', 'thread_freq']
GAIT_ESTIMATE_FIELDS = ['HS', 'current_time', 'stride_period', 'peak_torque', 'in_swing', 'N', 'torque_command', 'current_command']
SENSOR_FIELDS = ['state_time', 'temperature', 'winding_temp', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y' ,'gyro_z',
            'ankle_angle', 'ankle_velocity', 'motor_angle', 'motor_velocity', 'motor_current', 'motor_voltage', 'battery_voltage', 'battery_current', 'act_ank_torque', 'forceplate']
BERTEC_FIELDS = ['forceplate_left', 'forceplate_right']
RTPLOT_FIELDS = ['pitime_left', 'pitime_right', 'motor_current_left', 'motor_current_right', 'batt_volt_left', 'batt_volt_right', 'case_temp_left', 'case_temp_right']

EXOTHREAD_FIELDS = GENERAL_FIELDS + GAIT_ESTIMATE_FIELDS + SENSOR_FIELDS
GSETHREAD_FIELDS = GENERAL_FIELDS + BERTEC_FIELDS

EXOTHREAD_MAIN_FREQ = 0.5
EXOTHREAD_LOGGING_FREQ = 1

class DumbBertec:
    """
    Very dumb Bertec
    """
    def __init__(self, viconPC_IP = '141.212.77.30', viconPC_BertecPort = 4000):
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

    def write_command(self, speedR, speedL, incline = None, accR = 0.2, accL = 0.2, maxVel = 9001, minVel = -0):
        print("BERTEC WRITE: ", speedR, speedL)
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
    def __init__(self, viconPC_IP = '141.212.77.30', viconPC_port = 30,
                viconPath = 'E:'):

        # self.destinationIP = viconPC_IP
        # self.destinationPort = viconPC_port
        # self.viconPath = viconPath
        # self.delayPriorToRecord_ms = 1
        # self.fileName = ''
        # self.fileDescription = ''

        # # Setup UDP
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pass

    def start_recording(self, fileNameIn: str, fileDescription: str = 'A vicon recording'):
        """
        Send command to vicon to start file recording.
        Requires 2 inputs:
            fileNameIn: File name to be used on the vicon PC
            fileDescription: Any notes you want to add to your file. Fills the description field on vicon 
        """
        print("VICON START: {}, {}", fileNameIn, fileDescription)
        # msg = self._assemble_payload_start(fileNameIn, fileDescription)
        # self.sock.sendto(msg, (self.destinationIP, self.destinationPort))
        pass

    def stop_recording(self):
        print("VICON STOP")
        # msg = self._assemble_payload_stop()
        # self.sock.sendto(msg, (self.destinationIP, self.destinationPort))
        pass

    def _assemble_payload_start(self, fileNameIn, fileDescription):
        """
        Creates the proper XML string to trigger vicon. 
        More documentation available here: 
           https://docs.vicon.com/pages/viewpage.action?pageId=152010925
        """

        # Update self
        self.fileName = fileNameIn
        self.fileDescription = fileDescription

        # Construct the string
        notes = 'Vicon triggered from python over UDP'
        cmdHeader = '\n<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<CaptureStart>\n'
        nameLine = '<Name VALUE="{}"/>\n'.format(self.fileName)
        notesLine = '<Notes VALUE="{}"/>\n'.format(notes)
        descriptionLine = '<Description VALUE="{}"/>\n'.format(self.fileDescription)
        databasePathLine = '<DatabasePath VALUE="{}"/>\n'.format(self.viconPath)
        delayLine = '<Delay VALUE="{}"/>\n'.format(self.delayPriorToRecord_ms)
        packetIDline = '<PacketID VALUE="{}"/>\n'.format(randint(1,2**16))
        suffixLine = '</CaptureStart>'
        fullPayloadString = cmdHeader + nameLine + notesLine + descriptionLine + databasePathLine + delayLine + packetIDline + suffixLine
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
        packetIDline = '<PacketID VALUE="{}"/>\n'.format(randint(1,2**16))
        suffixLine = '</CaptureStop>'
        fullPayloadString = cmdHeader + nameLine + databasePathLine + delayLine + packetIDline + suffixLine
        # print(fullPayloadString)

        # Convert string to utf-8 bytes string to send over network. 
        return bytes(fullPayloadString, "utf-8")

class DumbDevice:
    def __init__(self):
        pass

class DumbExobootThread(BaseThread):
    """
    Testing purposes only!
    """
    def __init__(self, side, flexdevice, startstamp, name='dumbexobootthread', daemon=True, pause_event=Type[threading.Event], quit_event=Type[threading.Event], log_event=Type[threading.Event]):
        super().__init__(name=name, daemon=daemon, pause_event=pause_event, quit_event=quit_event, log_event=log_event)        
        # Logging Nexus
        self.fields = EXOTHREAD_FIELDS
        self.data_dict = dict.fromkeys(self.fields)
        self.startstamp = startstamp
        self.lastlogstamp = time.perf_counter()
        self.loggingnexus = None

    def getval(self, what):
        pass

    def spool_belt(self):
        pass
        
    def zeroProcedure(self):
        pass

    def read_sensors(self):
        for field in self.fields:
            self.data_dict[field] = -1.234

    def torque_2_current(self, torque, N) -> int:
        pass
    
    def thermal_safety_checker(self):
        pass
    
    def set_state_estimate(self, HS, stride_period, peak_torque, in_swing):
        pass

    def log_state_estimate(self):
        pass

    # Threading run() functions
    def on_pre_run(self):
        # Soft real time loop
        self.softRTloop = FlexibleSleeper(period=1/EXOTHREAD_MAIN_FREQ)
        
    def on_pre_pause(self):
        pass

    def pre_iterate(self):
        self.read_sensors()

    def iterate(self):
        pass

    def post_iterate(self):
        end_time = time.perf_counter()
        # Append data to LoggingNexus
        if self.loggingnexus and self.log_event.is_set() and end_time - self.lastlogstamp > 1/EXOTHREAD_LOGGING_FREQ:
            self.loggingnexus.append(self.name, self.data_dict)
            self.lastlogstamp = end_time

        # Soft real-time loop
        self.softRTloop.pause()

    def run(self):
        """
        Generic Run with Pausing Capabilities

        Fill out on_pre_run(), pre_iterate(), on_pre_pause(), iterate(), post_iterate(), and on_pre_exit()
        """
        self.on_pre_run()
        try:
            while self.quit_event.is_set():
                self.pre_iterate()
                if self.pause_event.is_set():
                    self.iterate()
                else:
                    self.on_pre_pause()
                if self.log_event.is_set():
                    self.post_iterate()
            self.on_pre_exit()
        except Exception as e:
            print("Exception: ", e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

class DumbGSE(BaseThread):
    def __init__(self, startstamp, device_left, device_right, thread_left, thread_right, name='GSE', daemon=True, pause_event=Type[threading.Event], quit_event=Type[threading.Event], log_event=Type[threading.Event]):
        # Threading
        super().__init__(name=name, daemon=daemon, pause_event=pause_event, quit_event=quit_event, log_event=log_event)
        self.device_left = device_left
        self.device_right = device_right
        self.device_thread_left = thread_left
        self.device_thread_right = thread_right

        # Peak torques set by GUI
        self.peak_torque_left = 0
        self.peak_torque_right = 0

        # Logging fields
        self.fields = GSETHREAD_FIELDS
        self.data_dict = dict.fromkeys(self.fields)

        # LoggingNexus
        self.startstamp = startstamp
        self.loggingnexus = None

        # Link to devices
        self.link_to_device()

    def link_to_device(self):
        self.device_left.gse = self
        self.device_right.gse = self

    def set_peak_torque_left(self, T):
        self.peak_torque_left = T
        self.device_thread_left.peak_torque = self.peak_torque_left

    def set_peak_torque_right(self, T):
        self.peak_torque_right = T
        self.device_thread_right.peak_torque = self.peak_torque_right

    def get_sensor_data(self):
        """TODO implement"""
        pass

    def get_estimate(self):
        """TODO implement"""
        pass
    
    def on_pre_run(self):
        """
        Runs once before starting main loop
        """
        # Soft real time loop
        loop_period = 1 / EXOTHREAD_MAIN_FREQ
        self.softRTloop = FlexibleSleeper(period=loop_period)

    def pre_iterate(self):
        """
        Sensor and Bertec reading
        Runs even if threads are paused
        """
        # Set starting time stamp
        self.data_dict['pitime'] = time.perf_counter() - self.startstamp

        # TODO IMU Estimation
        # self.get_sensor_data()
        # self.get_estimate()

        # Add forces to data dict
        self.data_dict['forceplate_left'] = 890
        self.data_dict['forceplate_right'] = -1320

        return True, False

    def iterate(self, new_stride_flag_left, new_stride_flag_right):
        """
        Update device estimates
        Does not run when threads paused
        """
        pass
        
    def post_iterate(self):
        """
        Loop period tracking and soft real time pause
        """
        # Update Period Tracker
        end_time = time.perf_counter()

        # Append GSE data into LoggingNexus
        self.data_dict['thread_freq'] = 842917
        if self.loggingnexus and self.log_event.is_set():
            self.loggingnexus.append(self.name, copy.deepcopy(self.data_dict))

        # soft real-time loop
        self.softRTloop.pause()

    def run(self):
        """
        Custom run to continue catching heelstrike but not update estimates
        """
        self.on_pre_run()
        while self.quit_event.is_set():
            nslf, nsfr = self.pre_iterate()
            if self.pause_event.is_set():
                self.iterate(nslf, nsfr)
            self.post_iterate()
        self.on_pre_exit()

class DumbWrapper:
    def __init__(self, subjectID, trial_type, trial_cond, description, usebackup):
        self.startstamp = time.perf_counter()
        self.pause_event = threading.Event()
        self.quit_event = threading.Event()
        self.log_event = threading.Event()
        self.pause_event.clear()
        self.quit_event.clear()
        self.log_event.clear()

        self.subjectID = subjectID
        self.trial_type = trial_type.upper()
        self.trial_cond = trial_cond.upper()
        self.description = description
        self.usebackup = usebackup in ["true", "True", "1", "yes", "Yes"]

        self.file_prefix = "{}_{}_{}_{}".format(self.subjectID, self.trial_type, self.trial_cond, self.description)
        
        print("Subject: {}".format(self.subjectID))
        print("Trial Type: {}".format(self.trial_type))
        print("Trial Cond: {}".format(self.trial_cond))
        print("Description: {}".format(self.description))
        print("Usebackup: {}".format(self.usebackup))

        # FilingCabinet
        self.filingcabinet = FilingCabinet("subject_data", self.subjectID)

        # Devices
        device_left = DumbDevice()
        device_right = DumbDevice()

        # Dumb exothreads
        self.exothread_left = DumbExobootThread("left", None, self.startstamp, "dumbexothreadleft", True, self.pause_event, self.quit_event, self.log_event)
        self.exothread_right = DumbExobootThread("right", None, self.startstamp, "dumbexothreadright", True, self.pause_event, self.quit_event, self.log_event)
        self.gse_thread = DumbGSE(self.startstamp, device_left, device_right, self.exothread_left, self.exothread_right, daemon=True, pause_event=self.pause_event, quit_event=self.quit_event, log_event=self.log_event)

        # LoggingNexus
        self.loggingnexus = LoggingNexus(self.subjectID, self.file_prefix, self.filingcabinet, self.exothread_left, self.exothread_right, self.gse_thread, log_event=self.log_event)

        # Ignore thread data when loading backups. MUST occur before initializing remote_thread
        self.filingcabinet.set_backupexceptions([self.exothread_left.name, self.exothread_right.name, self.gse_thread.name])
        self.filingcabinet.loadbackup(self.trial_type, self.file_prefix)

        # Remote Control
        self.remote_thread = ExobootRemoteServerThread(self, self.startstamp, self.filingcabinet, usebackup=self.usebackup, pause_event=self.pause_event, quit_event=self.quit_event, log_event=self.log_event)
        self.remote_thread.set_target_IP("[::]:50051")

    def run(self):
        self.quit_event.set()

        self.exothread_left.start()
        self.exothread_right.start()
        self.gse_thread.start()

        self.remote_thread.start()

        while self.quit_event.is_set():
            print("logging: ", self.log_event)
            self.loggingnexus.log()
            time.sleep(1.0)


if __name__ == "__main__":
    """
    Run test server
    """
    try:
        assert len(sys.argv) - 1 == 5
        _, subjectID, trial_type, trial_cond, description, usebackup = sys.argv
        dumb_wrapper = DumbWrapper(subjectID, trial_type, trial_cond, description, usebackup)
        dumb_wrapper.run()

    except KeyboardInterrupt:
        dumb_wrapper.quit_event.clear()
        print('Goodbye')
