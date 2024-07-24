import grpc
from concurrent import futures
import auction_pb2 as pb2
import auction_pb2_grpc as pb2_grpc

class AuctionHouse(pb2_grpc.auctionServicer):
    # Logs user bids and displays win/loss for experimenter
    def __init__(self):
        self.subject_name = ""
        self.bid = 0

    def reset_bid(self):
        self.bid = 0

    def testconnection(self, request, context):
        print("Received subject: {}".format(request.subject))
        self.subject_name = request.subject

        return pb2.receipt(received=True)

    def call(self, bid, context):
        self.log(bid.amount, bid.win)

        return pb2.receipt(received=True)
    
    def log(self, *argv):
        for arg in argv:
            print(arg, end=" ")
        print()
        

def start_auction():
    auctionhouse = AuctionHouse()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_auctionServicer_to_server(auctionhouse, server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        print("Starting Auction House")
        start_auction()
    except KeyboardInterrupt:
        print("Exiting")