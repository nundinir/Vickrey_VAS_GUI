"""IP ADDRESSES"""
SERVER_IP = f"{'35.3.150.116'}:" f"{'50051'}"    # IP address of local machine
LOCALHOST = "localhost:50051"    # IP address of local machine
PI_IP = f"{'35.3.175.251'}:" f"{'50055'}"
CLIENT_IP = "[::]:50051"   # IP address of the tablet


"""SCHEDULE TIMINGS"""
# Vickrey timings in seconds
AUCTION_START = 0
AUCTION_CLOSE = 120
BIDDING_OPEN = 0
BIDDING_CLOSE = 60
INITIAL_BIDDING_CLOSE = 30
RESULT_SHOW = 100

# VAS timing in seconds
MIN_WAIT_VAS = 60

# JND timing in seconds
SUBTRIAL_MAX = 120
MIN_WAIT_JND = 60

# PREF timing in seconds
MIN_WAIT_PREF = 60

"""BERTEC SETTINGS"""
# Bertec speed
BERTEC_SPEED_STOP = 0.0

# TODO get from treadmill speed csv
BERTEC_SPEED_LEFT = 0.7
BERTEC_SPEED_RIGHT = 0.7

BERTEC_ACC_LEFT = 0.33
BERTEC_ACC_RIGHT = 0.33

"""VICKREY SPECIFIC"""
# Bid settings
MAX_BID = 100

# Robobidder constants
NUM_ROBOBIDDERS = 2
k_RB = 0.4395073979128712
b_RB = 0.05735650555767768 # regular 'b' from Leo's trials
ROBOWALK_DUR = 2 # minutes


"""VAS SPECIFIC"""
# VAS Trial/Presentation Dicts
BTN_NUMS = [4]
MAX_TRIALS_DICT = {1: 1, 4: 6}
MAX_PRESENTATIONS_DICT = {1: 1, 4: 5} # without replacement

# TODO import from csv
EPO_MV = -9.57
NPO_MV = -12.00

"""JND SPECIFIC"""
# comparitor settings
NUM_BINS = 21
PROP_LOW = 0.5
PROP_HIGH = 1.5
REF_LIST = [15, 25]
TORQUE_MIN = 7
TORQUE_MAX = 40

# Query number
MAX_QUERIES = 150

"""PREF SPECIFIC"""
# Buttons
# TODO FIX UNEVEN BUTTON SIZES
PREF_ROWS = 4
PREF_COLS = 5

# Slider
PREF_STEP = 1.0

# Max Trials
MAX_PRES_PREF = 3

"""ACCLIMATION SPECIFIC"""
ACCL_STEP = 1.0


"""SPEEDFINDER SPECIFIC"""
F_TARGET = 105.0 # spm
V_INITIAL = 1.0 # m/s
ERROR_THRESHOLD = 0.005

VMIN = 0 # m/s
VMAX = 1.75 # m/s
SLEEPTIME = 2.0 # s
