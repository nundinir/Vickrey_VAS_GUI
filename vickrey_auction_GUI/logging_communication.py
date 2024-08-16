import os
import csv
import threading

import grpc
from concurrent import futures
import logging_pb2 as pb2
import logging_pb2_grpc as pb2_grpc

from constants import *

class LoggingClient:
    """
    Communication between Client and LoggingServer

    General messages for testing connection, treadmill state, and server kill

    Includes methods for all GUIs

    Includes general logging methods
    """
    def __init__(self):
        self.channel = grpc.insecure_channel(SERVER_IP)
        self.stub = pb2_grpc.logStub(self.channel)
        self.testconnection()

    def testconnection(self):
        """
        Sends test message to LoggingServer
        """
        msg = pb2.testmsg(msg="Hello from GUI")
        response = self.stub.testconnection(msg)
        
        # See response received
        if response:
            print("Connection Successful\n")
        else:
            raise ConnectionError("AuctionServer connection unsuccessful.")
    
    def chop(self):
        """
        Kill LoggingServer
        """
        msg = pb2.beaver()
        response = self.stub.chop(msg)
        return response

    def treadmill_state(self, state):
        """
        Sends treadmill state
        TODO redo message to include data from Bertec class
        """
        treadmillmsg = pb2.treadmillstate(state=state)
        response = self.stub.treadmill_state(treadmillmsg)
        return response

    def call(self, t, subject_bid, user_win_flag, current_payout, total_winnings):
        """
        Send results of Vickrey Auction
        """
        resultmsg = pb2.result(t=t,
                         subject_bid=subject_bid,
                         user_win_flag=user_win_flag,
                         current_payout=current_payout,
                         total_winnings=total_winnings
                         )
        response = self.stub.call(resultmsg)
        return response
    
    def question(self, t, enjoyment, rpe):
        """
        Send post-auction survey results
        """
        surveymsg = pb2.survey(t=t, enjoyment=enjoyment, rpe=rpe)
        response = self.stub.question(surveymsg)
        return response
    
    def slider_update(self, torque, pos):
        """
        Send updated slider info
        """
        msg = pb2.slider(torque=torque, pos = pos)
        response = self.stub.slider_update(msg)
        return response
    
    def presentation_result(self, torque, pos):
        """
        Send updated slider info
        """
        msg = pb2.presentation(torque=torque, pos = pos)
        response = self.stub.presentation_result(msg)
        return response
    
    def comparison_result(self, torques, higher):
        msg = pb2.comparison(torques=torques, higher=higher)
        response = self.stub.comparison_result(msg)
        return response
    
    def set_prefix(self, name, trialtype, description, date):
        msg = pb2.subject_prefix(name=name, trialtype=trialtype, description=description, date=date)
        response = self.stub.set_prefix(msg)
        return response

    def set_header(self, names):
        msg = pb2.header(names=names)
        response = self.stub.set_header(msg)
        return response

    def log(self, data):
        msg = pb2.datastream(data=data)
        response = self.stub.log(msg)
        return response

class LoggingServer(pb2_grpc.logServicer):
    """
    Vickrey Auction and survey results logging from GUI

    Prints internal state messages for trial oversight
    """
    def __init__(self, stop_event):
        self.auctionfilename = 'TEMP_AUCTION.csv'
        self.surveyfilename = 'TEMP_SURVEY.csv'
        self.vaspresentationfilename = 'TEMP_VASPRESENTATION.csv'
        self.jndfilename = 'TEMP_JND.csv'
        self.exodatafilename = 'TEMP_EXODATA.csv'

        self.stop_event = stop_event

    def create_filenames(self, name, trialtype, description, date, path):
        """
        TODO good description
        """
        print("Creating filenames")
        auctionfilename = "{}_{}_{}_AUCTION_{}.csv".format(name, trialtype, description, date)
        surveyfilename = "{}_{}_{}_SURVEY_{}.csv".format(name, trialtype, description, date)
        vaspresentationfilename = "{}_{}_{}_VASPRESENTATION_{}.csv".format(name, trialtype, description, date)
        jndfilename = "{}_{}_{}_JND_{}.csv".format(name, trialtype, description, date)
        exodatafilename = "{}_{}_{}_EXODATA_{}.csv".format(name, trialtype, description, date)

        self.auctionfilename = os.path.join(path, auctionfilename)
        self.surveyfilename = os.path.join(path, surveyfilename)
        self.vaspresentationfilename = os.path.join(path, vaspresentationfilename)
        self.jndfilename = os.path.join(path, jndfilename)
        self.exodatafilename = os.path.join(path, exodatafilename)

    def testconnection(self, request, context):
        print("Testing Connection: {}".format(request.msg))
        self.subject_name = request.msg
        return pb2.receipt(received=True)
    
    def treadmill_state(self, treadmillmsg, context):
        if treadmillmsg.state:
            print("Starting treadmill")
        else:
            print("Stopping treadmill")
        return pb2.receipt(received=True)
    
    def chop(self, beaver, context):
        """
        Kill Server from Client
        """
        self.stop_event.set()
        return pb2.receipt(received=True)

    def call(self, resultmsg, context):
        t = resultmsg.t
        subject_bid = resultmsg.subject_bid
        user_win_flag = resultmsg.user_win_flag
        current_payout = resultmsg.current_payout
        total_winnings = resultmsg.total_winnings

        print("Received auction results: {}, {}, {}, {}, {}".format(t, subject_bid, user_win_flag, current_payout, total_winnings))
        datalist = [t, subject_bid, user_win_flag, current_payout, total_winnings]
        with open(self.auctionfilename, 'a', newline='') as f:
            csv.writer(f).writerow(datalist)

        return pb2.receipt(received=True)
    
    def question(self, surveymsg, context):
        t = surveymsg.t
        enjoyment = surveymsg.enjoyment
        rpe = surveymsg.rpe

        print("Received survey results: {}, {}, {}".format(t, enjoyment, rpe))
        datalist = [t, enjoyment, rpe]
        with open(self.surveyfilename, 'a', newline='') as f:
            csv.writer(f).writerow(datalist)

        return pb2.receipt(received=True)
    
    def slider_update(self, slidermsg, context):
        """
        Send updated slider info
        """
        # TODO include logging for slider updates or not
        torque = slidermsg.torque
        pos = slidermsg.pos
        print("Torque: {} to {}".format(torque, pos))
        return pb2.receipt(received=True)
    
    def presentation_result(self, presmsg, context):
        """
        Send updated slider info
        """
        trial = presmsg.trial
        pres_num = presmsg.pres_num
        torques = presmsg.torques
        pos = presmsg.pos

        print("Received presentation results: {}, {}, {}, {}".format(trial, pres_num, torques, pos))
        datalist = [trial, pres_num, torques, pos]
        # TODO implement good csv format for logging presentations
        # with open(self.vaspresentationfilename, 'a', newline='') as f:
        #     csv.writer(f).writerow(datalist)
        return pb2.receipt(received=True)
    
    def comparison_result(self, compmsg):
        torques = compmsg.torques
        higher = compmsg.higher
        
        print("Received comparison results: {}, {}".format(torques, higher))
        return pb2.receipt(received=True)
    
    def set_prefix(self, prefixmsg, context):
        name = prefixmsg.name
        trialtype = prefixmsg.trialtype
        description = prefixmsg.description
        date = prefixmsg.date
        path = prefixmsg.path

        print("Received Prefix: {}, {}, {}, {}, {}".format(name, trialtype, description, date, path))
        self.create_filenames(name, trialtype, description, date, path)

        return pb2.receipt(received=True)

    def set_header(self, names):
        # TODO
        return pb2.receipt(received=True)

    def log(self, datamsg, context):
        # TODO
        return pb2.receipt(received=True)


def start_auction(client_ip):
    """
    Run auction server
    """
    try:
        stop_event = threading.Event()
        stop_event.clear()

        logging_server = LoggingServer(stop_event)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_logServicer_to_server(logging_server, server)
        server.add_insecure_port(client_ip)

        server.start()
        while not stop_event.is_set():
            pass
        server.stop(1.0)
    except KeyboardInterrupt:
        print('Goodbye')
        server.stop(1.0)
