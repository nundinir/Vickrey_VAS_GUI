"""Communication Server-side test script"""
import grpc
import gui2controller2_pb2
import gui2controller2_pb2_grpc
from concurrent import futures
import config
import os

class CommunicationService(gui2controller2_pb2_grpc.CommunicationServiceServicer):
    
    def GUI_Messenger(self, request, context):
        # Printing out the request from the client
        print("Server received data:", request.logging_data)
       
        gui_commanded_torque = request.logging_data[0]
        
        if gui_commanded_torque == 'nan':
            print("Received a nan value. Not updating the commanded torque.")
        else: 
            config.gui_commanded_torque = float(gui_commanded_torque)
            print("New commanded torque is:", config.gui_commanded_torque)

        # Sending the Null response(to close the communication loop)
        return gui2controller2_pb2.Null()
    
def starting_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gui2controller2_pb2_grpc.add_CommunicationServiceServicer_to_server(CommunicationService(),server)
    server.add_insecure_port(config.server_port)#config.client_ip)  
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    starting_server()
