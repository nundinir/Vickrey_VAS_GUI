import numpy as np

# server_ip = f"{'0.0.0.0'}:" f"{'50051'}"   # IP address when just testing on same machine
# client_ip = f"{'0.0.0.0'}:" f"{'50051'}"   # IP address when just testing on same machine

server_ip = f"{'67.194.45.127'}:" f"{'50051'}"   # IP address of the Controller (rPi)
client_ip = f"{'0.0.0.0'}:" f"{'50051'}"         # IP address of my laptop running the GUI

# keeps track of whether all the buttons have been pressed/experienced yet
btn_pressed_yet = [0] * 4   # 0 means not pressed yet, 1 means pressed

# Initializing values of the log variables
bool_confirm_button_pressed: bool = False

NPO_MV:float = -18.60        # Value of the slider at the extreme negative end (REMEMBER TO CHANGE IN .KV FILE)
EPO_MV:float = 19.80         # Value of the slider at the extreme positive end (REMEMBER TO CHANGE IN .KV FILE)
starting_val:int = 0         # Initial value of the slider cursor
grpc_needed:bool = False     # SET TO FALSE IF DOING GUI TESTING W/O COMMANDING EXO

# Set Torque settings
min_torque:float = 0.0                                  # Minimum torque value
max_torque:float = 30.0                                 # Maximum torque value
num_of_tot_torque_settings:int = 12                     # Total number of torque settings (Maintain 12 for practicality)
torque_step:float = (max_torque - min_torque)/num_of_tot_torque_settings  # Step size for the torque buttons (maintain 12 btns)
torque_settings = np.arange(torque_step,max_torque+torque_step,torque_step)  # All Torque settings (np.arrange doesn't include stop value)

##################################################
###### MODIFY THESE VALUES FOR EACH SUBJECT ######
##################################################

# UNCOMMENT WHEN TESTING FULL 12btn GUI AT ONCE
# GUI_btn_setup:str = 'full'                             # Full 12 btn setup
# sub_num:int = 1
# curr_trial_num:int = 1                                  # Current trial number (out of 3)
# current_presentation_num:int = 1                        # Only 1 presentation
# torques_per_presentation:int = 12                       # All 12 settings at once

# # Initializing the torque mapping button order
# button_order = ['L', 'K', 'J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
# button_slider_values = {}
# for i in button_order:
#     button_slider_values[i] = 0

# UNCOMMENT WHEN TESTING 4btn GUI
GUI_btn_setup:str = '4btn'                             # Full 12 btn setup
sub_num:int = 1
curr_trial_num:int = 5                                  # Current trial number (Out of 4)
current_presentation_num:int = 1                        # Current presentation number (Out of 3)
torques_per_presentation:int = 4                        # Number of torque options per presentation

# INITIALIZING the torque mapping button order
button_order = ['D', 'C', 'B', 'A']
button_slider_values = {}
for i in button_order:
    button_slider_values[i] = 0
