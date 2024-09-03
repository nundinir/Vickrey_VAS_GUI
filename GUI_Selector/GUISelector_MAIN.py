import time

from test_server import DumbBertec
from BertecMan import Bertec
from exoboot_remote_control import ExobootRemoteClient

from gui_apps import VickreyGUI
from constants import SERVER_IP

if __name__ == "__main__":
    print("Stuff")

    # Connect to Exoboot
    exoboot_remote = ExobootRemoteClient('localhost:50051')
    subjectID, trial_type, description = exoboot_remote.get_subject_info()

    print(subjectID, trial_type, description)
    time.sleep(1.0)

    # Start Bertec
    bertec = DumbBertec()#Bertec()

    match trial_type:
        case 'Vickrey':
            vg = VickreyGUI(exoboot_remote, bertec)
            vg.run()
        case 'VAS':
            # VASGUI(exoboot_remote, exoboot_remote, bertec).run()
            pass
