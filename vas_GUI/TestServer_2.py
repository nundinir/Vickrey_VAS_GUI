"""Communication Server-side test script"""
import grpc
import gui2controller2_pb2
import gui2controller2_pb2_grpc
from concurrent import futures
import random
import config
import csv
import os

class CommunicationService(gui2controller2_pb2_grpc.CommunicationServiceServicer):
    
    def GUI_Messenger(self, request, context):
        # Printing out the request from the client
        print("Server received data:", request.logging_data)
       
        gui_commanded_torque = request.logging_data[0]
        
        if gui_commanded_torque == 'nan':
            pass
        else: 
            print("New commanded torque is:", gui_commanded_torque)
            gui_commanded_torque = float(gui_commanded_torque)
        
        # # store a csv with the logged data
        # filename = 'Sub'+str(config.sub_num)+'_'+'T'+str(config.curr_trial_num)+'P'+str(config.current_presentation_num)+'.csv'
        # headers = ['Time(s)', 'Current Torque Experienced(Nm)', 'Adjusted Slider Btn', 
        #            'Adjusted Slider Value($)', 'Confirm Button Pressed']
        
        # # Check if file exists and is empty to decide on writing headers
        # write_headers = not os.path.exists(filename) or os.stat(filename).st_size == 0
        
        # with open(filename, 'a', newline='') as csvfile:
        #     csvwriter = csv.writer(csvfile)
            
        #     if write_headers:  # Step 3: Check if headers need to be written
        #         csvwriter.writerow(headers)
            
        #     csvwriter.writerow(request.logging_data)  # Directly write logging_data as a row

        # Sending the Null response(to close the communication loop)
        return gui2controller2_pb2.Null()
    
def starting_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gui2controller2_pb2_grpc.add_CommunicationServiceServicer_to_server(CommunicationService(),server)
    server.add_insecure_port(config.client_ip)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    starting_server()
