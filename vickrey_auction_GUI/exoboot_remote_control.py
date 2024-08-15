import threading
import grpc
from concurrent import futures
import exoboot_remote_pb2 as pb2
import exoboot_remote_pb2_grpc as pb2_grpc

from typing import Type
import time

from vickrey_auction_GUI.utils import MovingAverageFilter
from constants import PI_IP

from vickrey_auction_GUI.BaseExoThread import BaseThread

class ExobootCommServicer(pb2_grpc.exoboot_over_networkServicer):
    """
    Communication between anything and pi
    """
    def __init__(self, mainwrapper):
        super().__init__()
        self.mainwrapper = mainwrapper

    def set_pause(self, pause_msg, context):
        pause = pause_msg.pause

        if pause:
            self.mainwrapper.pause_event.clear()
        else:
            self.mainwrapper.pause_event.set()

        return pb2.receipt(received=True)

    def set_quit(self, quit_msg, context):
        quit = quit_msg.quit

        if quit:
            self.mainwrapper.quit_event.clear()
        else:
            self.mainwrapper.quit_event.set()

        return pb2.receipt(received=True)

    def command_exoboots(self, torque_msg, context):
        # Printing out the request from the client        
        peak_torque_left  = torque_msg.peak_torque_left
        peak_torque_right = torque_msg.peak_torque_right

        # Set torques in GSE
        self.mainwrapper.gse_thread.set_peak_torque_left(peak_torque_left)
        self.mainwrapper.gse_thread.set_peak_torque_right(peak_torque_right)

        return pb2.receipt(received=True)


class RemoteThread(BaseThread):
    """
    Thread class for receiving remote commands

    Runs until quit_event is cleared
     
    Does not pause
    """
    def __init__(self, mainwrapper, name='GUICommunication', daemon=True, pause_event=Type[threading.Event], quit_event=Type[threading.Event]):
        super().__init__(name=name, daemon=daemon, pause_event=pause_event, quit_event=quit_event)
        self.mainwrapper = mainwrapper
        self.exoboot_remote_grpc = ExobootCommServicer(self, self.mainwrapper)
    
    def starting_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
        pb2_grpc.add_exoboot_over_networkServicer_to_server(self.exoboot_remote_grpc, server)
        server.add_insecure_port(PI_IP)
        server.start()
        server.wait_for_termination()        

    def run(self):
        while self.quit_event.is_set():
            self.starting_server()


class ExobootRemoteClient:
    """
    Client running on network
    """
    def __init__(self):
        self.channel = grpc.insecure_channel(PI_IP)
        self.stub = pb2_grpc.exoboot_over_networkStub(self.channel)

    def set_pause(self, pause=False):
        pause_msg = pb2.pause(pause=pause)
        receipt = self.stub.set_pause(pause_msg)
        return receipt
    
    def set_quit(self, quit=False):
        quit_msg = pb2.quit(quit=quit)
        receipt = self.stub.set_quit(quit_msg)
        return receipt

    def set_torques(self, peak_torque_left=0, peak_torque_right=0):
        torque_msg = pb2.torques(peak_torque_left=peak_torque_left, peak_torque_right=peak_torque_right)
        receipt = self.stub.command_exoboots(torque_msg)
        return receipt
