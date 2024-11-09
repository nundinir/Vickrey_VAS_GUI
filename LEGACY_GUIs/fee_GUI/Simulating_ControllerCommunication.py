#Author: Varun Satyadev Shetty

import grpc
import Message_pb2
import Message_pb2_grpc

from concurrent import futures
import config


class CommunicationService(Message_pb2_grpc.CommunicationServiceServicer):
    def Input(self, request, context):
        print("Received Torque profile ", request.torque_profile)
        rise_time = request.torque_profile[0]/100
        fall_time = request.torque_profile[1]/100
        peak_torque_magnitude = request.torque_profile[2]/100
        peak_torque_timing = request.torque_profile[3]
        #print("Commanding torque profile", [rise_time, fall_time, peak_torque_magnitude, peak_torque_timing]) 
        return Message_pb2.Null()

def server_to_receive_torque_profiles_from_GUI():
    print(".... Starting the server on the controller.....")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Message_pb2_grpc.add_CommunicationServiceServicer_to_server(CommunicationService(),server)
    server.add_insecure_port(config.GUI_CONTROLLER_COMMUNICATION)
    server.start()
    server.wait_for_termination()   

if __name__ == '__main__':
    server_to_receive_torque_profiles_from_GUI()