"""Varun communication Cliebnt-Side test script"""
import grpc
import Message_2_pb2
import Message_2_pb2_grpc
import random
import config


def Send_client_request():

    #Creating a Dummy array, Replace this by your data passing script
    number = random.randint(0,10)
    number_array = list(range(0,number))
    with grpc.insecure_channel(config.server_ip, options=(('grpc.enable_http_proxy',0), )) as channel:
        try:
            stub = Message_2_pb2_grpc.CommunicationServiceStub(channel)
            response = stub.Input(Message_2_pb2.Request(data_array = number_array))
        except grpc.RpcError as e:
            print("Error",e)

if __name__ == '__main__':
    Send_client_request()