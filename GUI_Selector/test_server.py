import time, threading

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
        pass

class DumbGSE:
    def __init__(self):
        self.peak_torque_left = 0
        self.peak_torque_right = 0

    def set_peak_torque_left(self, T):
        self.peak_torque_left = T
    
    def set_peak_torque_right(self, T):
        self.peak_torque_right = T

class DumbWrapper:
    def __init__(self):
        self.pause_event = threading.Event()
        self.quit_event = threading.Event()
        self.pause_event.set()
        self.quit_event.set()

        self.gse_thread = DumbGSE()

        self.remote_thread = ExobootRemoteServerThread(self, pause_event=self.pause_event, quit_event=self.quit_event)
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
        dumb_wrapper = DumbWrapper()
        dumb_wrapper.run()

    except KeyboardInterrupt:
        dumb_wrapper.quit_event.clear()
        print('Goodbye')
        time.sleep(0.5)
