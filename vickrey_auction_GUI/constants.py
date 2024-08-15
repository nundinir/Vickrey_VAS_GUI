# Bertec speed
BERTEC_SPEED_STOP = 0.0

BERTEC_SPEED_LEFT = 1.0
BERTEC_SPEED_RIGHT = 1.0    

BERTEC_ACC_LEFT = 0.5
BERTEC_ACC_RIGHT = 0.5

# Exoboot Peak torques
PEAK_TORQUE_LEFT = 0
PEAK_TORQUE_RIGHT = 0

# Bid settings
MAX_BID = 100

# Speed up auction time by squeeze factor FOR TESTING
squeeze = 20

SERVER_IP = f"{'35.3.150.116'}:" f"{'50051'}"    # IP address of local machine
# SERVER_IP = "localhost:50051"    # IP address of local machine
PI_IP = f"{'67.194.47.115'}:" f"{'50051'}"
CLIENT_IP = "[::]:50051"   # IP address of the tablet

# Auction timings in seconds
AUCTION_START = 0/squeeze
AUCTION_CLOSE = 120/squeeze
BIDDING_OPEN = 0/squeeze
BIDDING_CLOSE = 60/squeeze
RESULT_SHOW = 100/squeeze

# Robobidder constants
k_RB = 0.4395073979128712
b_RB = 0.05735650555767768 # regular 'b' from Leo's trials
ROBOWALK_DUR = 2 # minutes

# Other Functions
def decimal_format(str):
    withsigdigs = '0' * max(3 - len(str), 0) + str
    withdecimal = withsigdigs[:-2] + '.' + withsigdigs[-2:]
    return withdecimal