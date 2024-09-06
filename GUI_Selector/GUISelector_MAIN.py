import time

from test_server import DumbBertec
from BertecMan import Bertec
from exoboot_remote_control import ExobootRemoteClient

from gui_apps import VickreyGUI, VASGUI, JNDGUI
from constants import SERVER_IP

if __name__ == "__main__":
    print("Stuff")

    # Connect to Exoboot
    exoboot_remote = ExobootRemoteClient('localhost:50051')
    subjectID, trial_type, trial_cond, description = exoboot_remote.get_subject_info()

    print("DETAILS: ", subjectID, trial_type, trial_cond, description)

    # Start Bertec
    bertec = DumbBertec()#Bertec()

    match trial_type.upper():
        case 'VICKREY':
            print("VICKREY")
            VickreyGUI(exoboot_remote, bertec).run()
        case 'VAS':
            VASGUI(exoboot_remote, bertec).run()
        case 'JND':
            JNDGUI(exoboot_remote, bertec, trial_cond).run()
