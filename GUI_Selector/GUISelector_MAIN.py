import os, json

from test_server import DumbBertec, DumbVicon
from external_devices.BertecMan import Bertec
from external_devices.ViconMan import Vicon

from shared_files.filing_cabinet import FilingCabinet
from shared_files.filing_cabinet_regex import (
    build_prefix,
    group_files_by_uid,
    datetime_formatcode_to_regex,
    file_extension_regex,
)
from exoboot_remote.exoboot_remote_control import ExobootRemoteClient

from gui_apps import (
    VickreyGUI,
    VASGUI,
    JNDGUI,
    PREFGUI,
    AcclimationGUI,
    SpeedFinderGUI,
    ControlPanelGUI,
)
from constants import TABLET_DATA_PATH, PI_IP, LOCALHOST


if __name__ == "__main__":
    # Connect to Exoboot
    exoboot_remote = ExobootRemoteClient(LOCALHOST)

    # Get subject info
    _, subjectID, trial_type, condition1, condition2, usebackup, current_date = (
        exoboot_remote.get_subject_info()
    )
    print(
        "GET_SUBJECT_INFO: ",
        subjectID,
        trial_type,
        condition1,
        condition2,
        usebackup,
        current_date,
    )
    file_prefix = build_prefix(
        SUBJECT=subjectID,
        TRIALTYPE=trial_type,
        CONDITION1=condition1,
        CONDITION2=condition2,
    )
    print("DEBUG_fileprefix: ", file_prefix)

    # Load subject dictionary
    subj_dict_file = open("subject_dictionary.json", mode="r")
    subject_dict = json.load(subj_dict_file)
    if not subjectID in subject_dict["subjects"].keys():
        print("NO SUBJECT DICTIONARY FOUND: EXITING")
        quit()
    else:
        subject_specific_info = subject_dict["subjects"][subjectID]

    # FilingCabinet for backups
    use_for_dir = [subjectID, trial_type]
    filingcabinet = FilingCabinet(TABLET_DATA_PATH, *use_for_dir)
    if usebackup:
        loadstatus = filingcabinet.loadbackup(file_prefix, rule="newest")
        print("Backup load status: {}".format("SUCCESS" if loadstatus else "FAILURE"))

    # Battery Check
    allow_check_batteries = trial_type in ["VAS", "JND"] or (
        trial_type == "VICKREY" and condition1 == "EPO"
    )
    print("BATTCHECK: ", allow_check_batteries)

    # DUMMY Check
    if subjectID == "DUMMY":
        bertec = DumbBertec()
        vicon = DumbVicon()
    else:
        bertec = Bertec()
        vicon = Vicon()

    # GUI kwargs
    gui_kwargs = {
        "exoboot_remote": exoboot_remote,
        "filingcabinet": filingcabinet,
        "bertec": bertec,
        "vicon": vicon,
        "condition1": condition1,
        "condition2": condition2,
        "file_prefix": file_prefix,
        "usebackup": usebackup,
        "current_date": current_date,
        "allow_check_batteries": allow_check_batteries,
        "subject_dict": subject_specific_info,
    }

    # Run GUI
    match trial_type:
        case "VICKREY":
            VickreyGUI(**gui_kwargs).run()
        case "VAS":
            VASGUI(**gui_kwargs).run()
        case "JND":
            JNDGUI(**gui_kwargs).run()
        case "PREF":
            PREFGUI(**gui_kwargs).run()
        case "ACCLIMATION":
            AcclimationGUI(**gui_kwargs).run()
        # case "SPEEDFINDER":
        #     SpeedFinderGUI(**gui_kwargs).run()
        case "CONTROLPANEL":
            ControlPanelGUI(**gui_kwargs).run()
        case _:
            print("INVALID GUI TYPE")
            quit()
