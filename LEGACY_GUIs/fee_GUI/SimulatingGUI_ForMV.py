#Author: Varun Satyadev Shetty

import grpc
import Message_pb2
import Message_pb2_grpc

import config

import argparse
import time


def SendingTorqueProfile(TP):
    '''
    input argument: Torque profile [rise time, fall time, peak torque timing, peak torque magnitude]
    function defination: It sends the torque profile to the the server running on the Dephy Exoboot Raspberry Pi, using gRPC
    conmmunication, via the ip address "config.GUI_CONTROLLER_COMMUNICATION"
    output: Null
    '''
    with grpc.insecure_channel(
            config.GUI_CONTROLLER_COMMUNICATION, options=(('grpc.enable_http_proxy',0), )) as channel:
        try:
            stub = Message_pb2_grpc.CommunicationServiceStub(channel)
            stub.Input(
                Message_pb2.Request(torque_profile=TP))
        except grpc.RpcError as e:
            print("gRPC communication error")
            print(e)

def Simulating_GUI_Response(starting_torque, ending_torque, torque_magnitude_increment, waiting_time):
    i = starting_torque
    try:
        while (i<=ending_torque):
            print("Starting")
            torque_profile =  [23.2,50.3,62.6,i]
            print("Commanding: ", torque_profile)
            i = i+torque_magnitude_increment
            SendingTorqueProfile(torque_profile)
            time.sleep(waiting_time)
    except KeyboardInterrupt:
        print("Exiting!!!! Bye.........")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--starting_torque', default ='6.3')
    parser.add_argument('--ending_torque', default ='22')
    parser.add_argument('--torque_magnitude_increment', default ='1.5')
    parser.add_argument('--waiting_time', default ='30')
    args = parser.parse_args()
    Simulating_GUI_Response(float(args.starting_torque), float(args.ending_torque), float(args.torque_magnitude_increment), float(args.waiting_time))