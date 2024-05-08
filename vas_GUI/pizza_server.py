import grpc
import Message_pb2
import Message_pb2_grpc
from concurrent import futures
import config
class GUI(Message_pb2_grpc.GUIServicer):
    def UserButton(self, request, context):
        print(f"Button pressed: {request.torque}")
        return Message_pb2.Null()

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Message_pb2_grpc.add_GUIServicer_to_server(GUI(), server)
    server.add_insecure_port(config.server_ip)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    server()