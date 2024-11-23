import os, json

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

    # Load subject dictionary
    subj_dict_file = open("subject_dictionary.json", mode="r")
    subject_dict = json.load(subj_dict_file)
    if not subjectID in subject_dict["subjects"].keys():
        print("NO SUBJECT DICTIONARY FOUND: EXITING")
        quit()
    else:
        subject_specific_info = subject_dict["subjects"][subjectID]

    # FilingCabinet for backups
    filingcabinet = FilingCabinet("trial_backups", subjectID)
    if usebackup:
        loadstatus = filingcabinet.loadbackup(file_prefix, rule="newest")
        print("Backup load status: {}".format("SUCCESS" if loadstatus else "FAILURE"))

    # Battery Check
    allow_check_batteries = trial_type in ["VAS", "JND"] or (trial_type == "VICKREY" and trial_cond == "EPO")
    print("BATTCHECK: ", allow_check_batteries)

    # DUMMY Check
    if subjectID == 'DUMMY':
        bertec = DumbBertec()
        vicon = DumbVicon()
    else:
        bertec = Bertec()
        vicon = Vicon()

    # GUI kwargs
    gui_kwargs = {"exoboot_remote": exoboot_remote,
                  "filingcabinet": filingcabinet,
                  "bertec": bertec,
                  "vicon": vicon,
                  "startstamp": startstamp,
                  "trial_cond": trial_cond,
                  "description": description,
                  "file_prefix": file_prefix,
                  "usebackup": usebackup,
                  "allow_check_batteries": allow_check_batteries,
                  "subject_dict": subject_specific_info
                  }
    
    # GUIs
    gui_dict = {"VICKREY": VickreyGUI, "VAS": VASGUI, "JND": JNDGUI, "PREF": PREFGUI, "ACCLIMATION": AcclimationGUI, "SPEEDFINDER": SpeedFinderGUI}

    # Run GUI
    gui_dict[trial_type](**gui_kwargs).run()
