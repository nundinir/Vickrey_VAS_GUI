import time

from test_server import DumbBertec
from BertecMan import Bertec
from exoboot_remote_control import ExobootRemoteClient

from gui_apps import VickreyGUI, VASGUI, JNDGUI, PREFGUI, AcclimationGUI, SpeedFinderGUI
from constants import PI_IP, LOCALHOST


if __name__ == "__main__":
    # Connect to Exoboot
    exoboot_remote = ExobootRemoteClient(LOCALHOST)

    # Get subject info
    startstamp, subjectID, trial_type, trial_cond, description = exoboot_remote.get_subject_info()

    print("DETAILS: ", startstamp, subjectID, trial_type, trial_cond, description)

    # Start Bertec
    if subjectID == 'DUMMY':
        bertec = DumbBertec()
    else:
        bertec = Bertec()

    match trial_type.upper():
        case 'VICKREY':
            # TODO fix survey reporting
            VickreyGUI(exoboot_remote, bertec).run()
        case 'VAS':
            VASGUI(startstamp, exoboot_remote, bertec).run()
        case 'JND':
            JNDGUI(exoboot_remote, bertec, trial_cond).run()
        case 'PREF':
            PREFGUI(exoboot_remote, bertec, trial_cond).run()
        case 'ACCLIMATION':
            AcclimationGUI(exoboot_remote, bertec).run()
        case'SPEEDFINDER':
            # TODO finish speedfindergui or remove
            # Is a WIP
            SpeedFinderGUI(exoboot_remote, bertec).run()
        case _:
            print("INVALID CASE")
