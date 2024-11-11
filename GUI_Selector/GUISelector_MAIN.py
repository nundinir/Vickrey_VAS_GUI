import os

from test_server import DumbBertec, DumbVicon
from external_devices.BertecMan import Bertec
from external_devices.ViconMan import Vicon

from shared_files.LoggingClass import FilingCabinet
from exoboot_remote.exoboot_remote_control import ExobootRemoteClient

from gui_apps import VickreyGUI, VASGUI, JNDGUI, PREFGUI, AcclimationGUI, SpeedFinderGUI
from constants import PI_IP, LOCALHOST


if __name__ == "__main__":
    # Connect to Exoboot
    exoboot_remote = ExobootRemoteClient(LOCALHOST)

    # Get subject info
    startstamp, subjectID, trial_type, trial_cond, description, usebackup = exoboot_remote.get_subject_info()
    file_prefix = "{}_{}_{}_{}".format(subjectID, trial_type, trial_cond, description)
    print("DETAILS: ", startstamp, subjectID, trial_type, trial_cond, description)

    # FilingCabinet for backups
    filingcabinet = FilingCabinet("trial_backups", subjectID)

    if usebackup:
        loadstatus = filingcabinet.loadbackup(file_prefix, rule="newest")
        print("Backup load status: {}".format("SUCCESS" if loadstatus else "FAILURE"))

    # DUMMY Check
    if subjectID == 'DUMMY':
        bertec = DumbBertec()
        vicon = DumbVicon()
    else:
        bertec = Bertec()
        vicon = Vicon()

    match trial_type.upper():
        case 'VICKREY':
            VickreyGUI(exoboot_remote, filingcabinet, file_prefix, bertec, vicon, usebackup=usebackup).run()
        case 'VAS':
            VASGUI(startstamp, exoboot_remote, filingcabinet, file_prefix, bertec, vicon, usebackup=usebackup).run()
        case 'JND':
            JNDGUI(exoboot_remote, filingcabinet, file_prefix, bertec, vicon, trial_cond, description, usebackup=usebackup).run()
        case 'PREF':
            PREFGUI(exoboot_remote, filingcabinet, file_prefix, bertec, vicon, trial_cond).run()
        case 'ACCLIMATION':
            AcclimationGUI(exoboot_remote, filingcabinet, file_prefix, bertec, vicon).run()
        case'SPEEDFINDER':
            # TODO finish speedfindergui or remove
            # Is a WIP
            SpeedFinderGUI(exoboot_remote, bertec).run()
        case _:
            print("INVALID CASE")

