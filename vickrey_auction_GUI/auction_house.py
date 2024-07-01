import grpc
import time
from concurrent import futures
import auction_pb2 as pb2
import auction_pb2_grpc as pb2_grpc

class AuctionHouse(pb2_grpc.auctionServicer):
    def __init__(self):
        self.bid = 0

    def reset_bid(self):
        self.bid = 0

    def call(self, bid, context):
        self.bid = bid.amount
        return pb2.receipt(received=True)
    
    def close(self):
        result = pb2.result(win=0, amount=self.bid)
        self.reset_bid()
        return result

def start_auction():
    auctionhouse = AuctionHouse()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_auctionServicer_to_server(auctionhouse, server)
    server.add_insecure_port("[::]:50051")
    server.start()

    while True:
        auctionhouse.bid += 1
        print("Bid: {}".format(auctionhouse.bid))

        if auctionhouse.bid > 2:
            auctionhouse.reset_bid()


        time.sleep(1.0)


    

if __name__ == "__main__":
    try:
        print("Starting Auction House")
        start_auction()
    except KeyboardInterrupt:
        print("Exiting")