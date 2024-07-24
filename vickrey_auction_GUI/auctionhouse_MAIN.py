import csv

import grpc
from concurrent import futures
import auction_pb2 as pb2
import auction_pb2_grpc as pb2_grpc

class AuctionHouse(pb2_grpc.auctionServicer):
    # Logs user bids and displays win/loss for experimenter
    def __init__(self):
        self.subject_name = ""
        self.bid = 0

        self.filename = "testing.csv"
        self.header = ["t", "subject_bid", "user_win_flag", "current_payout", "total_winnings"]

        with open(self.filename, 'a', newline='') as f:
            csv.writer(f).writerow(self.header)

    def reset_bid(self):
        self.bid = 0

    def testconnection(self, request, context):
        print("Received subject: {}".format(request.subject))
        self.subject_name = request.subject
        return pb2.receipt(received=True)

    def call(self, resultmsg, context):
        t = resultmsg.t
        subject_bid = resultmsg.subject_bid
        user_win_flag = resultmsg.user_win_flag
        current_payout = resultmsg.current_payout
        total_winnings = resultmsg.total_winnings

        self.log(t, subject_bid, user_win_flag, current_payout, total_winnings)

        return pb2.receipt(received=True)
    
    def log(self, t, subject_bid, user_win_flag, current_payout, total_winnings):
        datalist = [t, subject_bid, user_win_flag, current_payout, total_winnings]
        print("Received results: {}, {}, {}, {}, {}".format(t, subject_bid, user_win_flag, current_payout, total_winnings))

        with open(self.filename, 'a', newline='') as f:
            csv.writer(f).writerow([t, subject_bid, user_win_flag, current_payout, total_winnings])


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