"""Varun Communication Server-side test script"""
import grpc
import Message_2_pb2
import Message_2_pb2_grpc
from concurrent import futures
import random
import config
import csv


class CommunicationService(Message_2_pb2_grpc.CommunicationServiceServicer):
    logged_yet = False
    
    def Input(self, request, context):
        # Printing out the request from the client
        print("Server received data:", request.data_array)
        
        # store a csv with the logged data
        filename = 'Sub'+str(config.sub_num)+'_'+'T'+str(config.curr_trial_num)+'P'+str(config.current_presentation_num)
        headers = ['Time(s)', 'Current Torque Experienced', 'VAS Value of Torque Slider', 'Confirm Button Pressed']

        with open(filename+'.csv', 'a') as csvwriter:
            if self.logged_yet == False: # write headers & time stamp to csv file only once
                csvwriter.write(",".join(map(str, headers)) + "\n")
                self.logged_yet = True
                
            csvwriter.write(",".join([str(i) for i in request.data_array]) + "\n")

        # Sending the Null response(to close the communication loop)
        return Message_2_pb2.Null()
    
def starting_server():
    server_1 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Message_2_pb2_grpc.add_CommunicationServiceServicer_to_server(CommunicationService(),server_1)
    server_1.add_insecure_port(config.client_ip)
    server_1.start()
    server_1.wait_for_termination()


if __name__ == '__main__':
    starting_server()