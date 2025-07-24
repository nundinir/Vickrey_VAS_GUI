from BertecMan import Bertec
from logging_communication import LoggingClient
from exoboot_remote_control import ExobootRemoteClient

from gui_apps import VickreyGUI, VASGUI

if __name__ == "__main__":
    print("Stuff")

    # Client to LoggingServer
    logging_client = LoggingClient(guiname="GUISelector")
    subjectID, trial_type, description = logging_client.get_subject_info()

    # Connect to Exoboot
    exoboot_remote = ExobootRemoteClient()
    exoboot_remote.send_subject_info(subjectID, trial_type, description)

    # Start Bertec
    bertec = Bertec()

    match trial_type:
        case "Vickrey":
            VickreyGUI(logging_client, exoboot_remote, bertec).run()
        case "VAS":
            VASGUI(logging_client, exoboot_remote, bertec).run()
