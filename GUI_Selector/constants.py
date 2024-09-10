"""IP ADDRESSES"""
SERVER_IP = f"{'35.3.150.116'}:" f"{'50051'}"    # IP address of local machine
# SERVER_IP = "localhost:50051"    # IP address of local machine
PI_IP = f"{'35.3.206.241'}:" f"{'50051'}"
CLIENT_IP = "[::]:50051"   # IP address of the tablet


"""SCHEDULE TIMINGS"""
# Speed up auction time by squeeze factor FOR TESTING
squeeze = 100

# Vickrey timings in seconds
AUCTION_START = 0/squeeze
AUCTION_CLOSE = 120/squeeze
BIDDING_OPEN = 0/squeeze
BIDDING_CLOSE = 60/squeeze
RESULT_SHOW = 100/squeeze

# VAS timing in seconds
MIN_WAIT_VAS = 120/squeeze

# JND timing in seconds
SUBTRIAL_MAX = 240/squeeze
MIN_WAIT_JND = 60/squeeze

# PREF timing in seconds
MIN_WAIT_PREF = 60/squeeze

"""BERTEC SETTINGS"""
# Bertec speed
BERTEC_SPEED_STOP = 0.0

# TODO get from treadmill speed csv
BERTEC_SPEED_LEFT = 1.0
BERTEC_SPEED_RIGHT = 1.0    

BERTEC_ACC_LEFT = 0.25
BERTEC_ACC_RIGHT = 0.25

"""VICKREY SPECIFIC"""
# Exoboot Peak torques
PEAK_TORQUE_LEFT = 40
PEAK_TORQUE_RIGHT = 40

# Bid settings
MAX_BID = 100

# Robobidder constants
k_RB = 0.4395073979128712
b_RB = 0.05735650555767768 # regular 'b' from Leo's trials
ROBOWALK_DUR = 2 # minutes


"""VAS SPECIFIC"""
# VAS Trial/Presentation Dicts
BTN_NUMS = [4, 12] #[3] for quick testing
MAX_TRIALS_DICT = {3: 1, 4: 3, 12: 2}
MAX_PRESENTATIONS_DICT = {3: 1, 4: 3, 12: 1}

# TODO import from csv
EPO_MV = 3.4
NPO_MV = -18.60

"""JND SPECIFIC"""
# comparitor settings
NUM_BINS = 21
PROP_LOW = 0.5
PROP_HIGH = 1.5
REF_LOW = 15
REF_HIGH = 35
TORQUE_MIN = 7
TORQUE_MAX = 40

# Query number
MAX_QUERIES = 10

"""PREF SPECIFIC"""
# Slider
PREF_STEP = 1.0

# Buttons
PREF_ROWS = 4
PREF_COLS = 5

# Max Trials
MAX_PRES_VAS = 3