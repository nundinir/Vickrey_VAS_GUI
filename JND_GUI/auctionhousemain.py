from constants import CLIENT_IP
from logging_communication import start_auction

if __name__ == "__main__":
    print("Starting Auction House")
    start_auction(CLIENT_IP)
