import sys, time, threading

from exoboot_remote_control import ExobootRemoteServerThread

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

class DumbGSE:
    def __init__(self):
        self.peak_torque_left = 0
        self.peak_torque_right = 0

    def set_peak_torque_left(self, T):
        print("Set Peak Torque Left: {}".format(T))
        self.peak_torque_left = T
    
    def set_peak_torque_right(self, T):
        print("Set Peak Torque Right: {}".format(T))
        self.peak_torque_right = T

class DumbWrapper:
    def __init__(self, subjectID, trial_type, trial_cond, description):
        self.startstamp = time.perf_counter()
        self.pause_event = threading.Event()
        self.quit_event = threading.Event()
        self.pause_event.set()
        self.quit_event.set()

        self.subjectID = subjectID
        self.trial_type = trial_type.upper()
        self.trial_cond = trial_cond.upper()
        self.description = description

        self.file_prefix = "{}_{}_{}_{}".format(self.subjectID, self.trial_type, self.trial_cond, self.description)
        
        print("Subject: {}".format(self.subjectID))
        print("Trial Type: {}".format(self.trial_type))
        print("Trial Cond: {}".format(self.trial_cond))
        print("Description: {}".format(self.description))

        self.gse_thread = DumbGSE()

        self.remote_thread = ExobootRemoteServerThread(self, self.startstamp, pause_event=self.pause_event, quit_event=self.quit_event)
        self.remote_thread.set_target_IP("[::]:50051")
        self.remote_thread.start()

    def run(self):
        while self.quit_event.is_set():
            time.sleep(0.1)

if __name__ == "__main__":
    """
    Run auction server
    """
    try:
        subjectID = sys.argv[1]
        trial_type = sys.argv[2]
        trial_cond = sys.argv[3]
        description = sys.argv[4]
        dumb_wrapper = DumbWrapper(subjectID, trial_type, trial_cond, description)
        dumb_wrapper.run()

    except KeyboardInterrupt:
        dumb_wrapper.quit_event.clear()
        print('Goodbye')
