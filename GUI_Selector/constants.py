"""IP ADDRESSES"""
SERVER_IP = f"{'35.3.150.116'}:" f"{'50051'}"    # IP address of local machine
LOCALHOST = "localhost:50051"    # IP address of local machine
PI_IP = f"{'35.3.192.197'}:" f"{'50055'}"


"""BERTEC SETTINGS"""
BERTEC_SPEED_STOP = 0.0
BERTEC_ACC_LEFT = 0.33
BERTEC_ACC_RIGHT = 0.33


"""BATTERY SETTINGS"""
BATTV_LOWER_LIM = 22000 # mV


"""VICKREY SPECIFIC"""
# Vickrey timings in seconds
AUCTION_START = 0
AUCTION_CLOSE = 120
BIDDING_OPEN = 0
BIDDING_CLOSE = 60
INITIAL_BIDDING_CLOSE = 30
RESULT_SHOW = 100

# Bid settings
MAX_BID = 100

# Robobidder constants
ROBOWALK_DUR = 2 # min
NUM_ROBOBIDDERS = 2
k_RB = 0.4395073979128712
b_RB = 0.05735650555767768 # regular 'b' from Leo's trials


"""VAS SPECIFIC"""
# MV text offsets
MV_TEXT_OFFSETS = {1:0.42, 4:0.1, 10: 0.03}
SLIDER_JUSTIFICATION = 0.15

# VAS timing in seconds
MIN_WAIT_VAS = {1: 10, 4: 60, 10: 120}
VAS_10BTN_BREAK = 60

# VAS Trial/Presentation Dicts
BTN_NUMS = [1]
MAX_TRIALS_DICT = {1:1, 4:1, 10:1}
MAX_PRESENTATIONS_DICT = {1:20, 4:5, 10:1} # without replacement

"""JND SPECIFIC"""
# JND timing in seconds
SUBTRIAL_MAX = 120
MIN_WAIT_JND = 60

TORQUE_MIN = 7
TORQUE_MAX = 40

# specific uniform sampler comparitor settings
NUM_BINS = 21
PROP_LOW = 0.5
PROP_HIGH = 1.5
MAX_QUERIES = 150

# specific staircase comparitor settings
REF_LIST = [18, 29]
RIGHT_LIM = 2   # num of consecutive right(s) after which distance from ref will decrease
RATIO = 0.947   # ratio of step_down(correct)/step_up(incorrect)
STEP_SIZE_RIGHT_DICT = {18: 1, 29: 1}  # step size when correct response given for each reference torque
RUN_LIMIT = 6                 # Number of reversals before the algorithm converges
INIT_STEP_OUT_SIZE = 11       # Initial multiplier away from reference torque for the comparison torque   
REPETITIONS = 1               # Number of ascending and descending repetitions for each reference torque value
MODES = ['ascending', 'descending'] # Staircase modes, either 'ascending' or 'descending' towards reference

PICKLE_FILE_PATH = "jnd_staircase.pkl"  # To Load/Save the staircase objects

"""PREF SPECIFIC"""
# PREF timing in seconds
MIN_WAIT_PREF = 60
WALK_TIME_PREF = 120

# Buttons
PREF_ROWS = 4
PREF_COLS = 5

# Slider
PREF_STEP = 1.0

# Dial
DIAL_SENSITIVITY_FACTOR = 0.08

# Max Trials
MAX_PRES_PREF = 10


"""ACCLIMATION SPECIFIC"""
ACCL_STEP = 1.0


"""SPEEDFINDER SPECIFIC"""
F_TARGET = 105.0 # spm
V_INITIAL = 1.0 # m/s
ERROR_THRESHOLD = 0.005

VMIN = 0 # m/s
VMAX = 1.75 # m/s
SLEEPTIME = 2.0 # s
