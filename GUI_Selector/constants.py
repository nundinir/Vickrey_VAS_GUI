"""IP ADDRESSES"""
SERVER_IP = f"{'35.3.150.116'}:" f"{'50051'}"    # IP address of local machine
LOCALHOST = "localhost:50051"    # IP address of local machine
PI_IP = f"{'35.3.87.217'}:" f"{'50051'}"
CLIENT_IP = "[::]:50051"   # IP address of the tablet


"""SCHEDULE TIMINGS"""
# Speed up auction time by squeeze factor FOR TESTING
squeeze = 100

# Vickrey timings in seconds
AUCTION_START = 0/squeeze
AUCTION_CLOSE = 120/squeeze
BIDDING_OPEN = 0/squeeze
BIDDING_CLOSE = 60/squeeze
INITIAL_BIDDING_CLOSE = 30/squeeze
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
BERTEC_SPEED_LEFT = 1.16
BERTEC_SPEED_RIGHT = 1.16    

BERTEC_ACC_LEFT = 0.33
BERTEC_ACC_RIGHT = 0.33

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
BTN_NUMS = [4]
BTN_NUM_TOTAL = 20
MAX_TRIALS_DICT = {4: 6}
MAX_PRESENTATIONS_DICT = {4: 5}

# TODO import from csv
EPO_MV = -9.57
NPO_MV = -12.00

"""JND SPECIFIC"""
# comparitor settings
NUM_BINS = 21
PROP_LOW = 0.8
PROP_HIGH = 1.2
REF_LOW = 15
REF_HIGH = 35
TORQUE_MIN = 7
TORQUE_MAX = 40

# Query number
MAX_QUERIES = 10

"""ACCLIMATION SPECIFIC"""
ACCL_STEP = 1.0

"""PREF SPECIFIC"""
# Buttons
# TODO FIX UNEVEN BUTTON SIZES
PREF_ROWS = 2
PREF_COLS = 2

# Slider
PREF_STEP = 1.0

# Max Trials
MAX_PRES_PREF = 3
