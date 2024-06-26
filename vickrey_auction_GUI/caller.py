import grpc
import auction_pb2 as pb2
import auction_pb2_grpc as pb2_grpc

class Caller(object):
    def __init__(self):
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = pb2_grpc.auctionStub(self.channel)

    def call(self, amount):
        bid = pb2.bid(amount=amount)
        response = self.stub.call(bid)
        return response
    
if __name__ == "__main__":
    client = Caller()
    test1 = client.call(10)
    print(test1.received)

    test2 = client.call(20)
    print(test1.received)
