import os, csv, copy, threading
from typing import Type
from pathlib import Path
from collections import deque

# from rtplot import client


class LoggingNexus:
    def __init__(
        self,
        subjectID,
        file_prefix,
        filingcabinet,
        *threads,
        pause_event=Type[threading.Event]
    ):
        self.subjectID = subjectID
        self.file_prefix = file_prefix
        self.pause_event = pause_event

        self.thread_names = []
        self.thread_fields = {}
        self.thread_stashes = {}
        self.filenames = {}

        self.filingcabinet = filingcabinet

        self.setup(threads)

    def setup(self, threads):
        """
        Add each thread to LoggingNexus dicts
        Threads log to deques using their name
        """
        for thread in threads:
            thread.loggingnexus = self

            threadname = thread.name
            self.thread_names.append(threadname)
            self.thread_fields[threadname] = thread.fields
            self.thread_stashes[threadname] = deque()
            self.filenames[threadname] = "{}_{}".format(self.file_prefix, threadname)

        # Write Headers to temp name
        for thread in self.thread_names:
            filename = self.filenames[thread]
            filepath = self.filingcabinet.newfile(
                filename, "csv", behavior="new", dictkey=thread
            )
            fields = self.thread_fields[thread]

            with open(filepath, "a") as f:
                writer = csv.writer(f, lineterminator="\n", quotechar="|")
                writer.writerow(fields)

    def append(self, threadname, data_dict):
        """
        Append data dict to stashes
        Needs to be a deepcopy
        """
        data = copy.deepcopy(data_dict)
        self.thread_stashes[threadname].append(data)

        # # send client
        # if 'exothread_' in threadname:
        #     if 'left' in threadname:
        #         # pull data from dictionary
        #         self.rtplot_data_dict['pitime_left'] = data['pitime']
        #         self.rtplot_data_dict['motor_current_left'] = data['motor_current']
        #         self.rtplot_data_dict['batt_volt_left'] = data['battery_voltage']
        #         self.rtplot_data_dict['case_temp_left'] = data['temperature']

        #         plot_data_array = [self.rtplot_data_dict.values()]
        #     else:
        #         self.rtplot_data_dict['pitime_right'] = data['pitime']
        #         self.rtplot_data_dict['motor_current_right'] = data['motor_current']
        #         self.rtplot_data_dict['batt_volt_right'] = data['battery_voltage']
        #         self.rtplot_data_dict['case_temp_right'] = data['temperature']

        #         plot_data_array = [self.rtplot_data_dict.values()]

        #     client.send_array(plot_data_array)

    def get(self, threadname, field):
        try:
            data = self.thread_stashes[threadname][-1][field]
            return data
        except:
            return -1

    def log(self):
        """
        Empty data from thread_stashes and write to corresponding file
        """
        try:
            if self.pause_event.is_set():
                for thread in self.thread_names:
                    filename = self.filingcabinet.getpath(thread)
                    fields = self.thread_fields[thread]
                    stash = self.thread_stashes[thread]
                    stash_size = len(stash)

                    with open(filename, "a") as f:
                        writer = csv.DictWriter(
                            f, fieldnames=fields, lineterminator="\n", quotechar="|"
                        )
                        for _ in range(stash_size):
                            writer.writerow(stash.popleft())
        except Exception as e:
            print("LoggingNexus.log() error: ", e)


if __name__ == "__main__":
    """
    FilingCabinet Demo
    """

    # Create FilingCabinet for subject "dummy"
    pfolder = "testfolder"
    cabinet = FilingCabinet(pfolder, "dummy")

    # Create txt files in subject_data and subject subfolder to show they exist
    Path(os.path.join(pfolder, "asdf.txt")).touch()
    Path(os.path.join(cabinet.getpfolderpath(), "qwer.txt")).touch()

    # Use FilingCabinet to create new file
    # Since qwer.txt exists, follow "new" behavior (add _new to filename)
    qwer_path = cabinet.newfile(
        "qwer", "txt", behavior="new", dictkey="special_identifier"
    )
    print("qwer filepath: {}".format(qwer_path))

    # Get qwer_file path using getpath
    # Should be same as qwer_path
    iforgotpath = cabinet.getpath("special_identifier")
    print("from getpath: {}".format(iforgotpath))

    # Create testcsv in subject subfolder
    with open(iforgotpath, "a") as f:
        writer = csv.writer(f, lineterminator="\n", quotechar="|")
        writer.writerow(["foo", "bar"])

    print("Demo Finished")
