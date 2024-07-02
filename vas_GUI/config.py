import numpy as np

server_ip = f"{'0.0.0.0'}:" f"{'50051'}"   # IP address of the Controller (rPi)
client_ip = f"{'0.0.0.0'}:" f"{'50051'}"   # IP address of the Tablet (GUI)

# Initializing the torque mapping button order
button_order = ['D', 'C', 'B', 'A']
button_slider_values = {}
for i in button_order:
    button_slider_values[i] = 0

# keeps track of whether all the buttons have been pressed/experienced yet
btn_pressed_yet = [0] * 4   # 0 means not pressed yet, 1 means pressed

# Initializing values of the log variables
bool_confirm_button_pressed: bool = False

NPO_MV = -15        # Value of the slider at the extreme negative end
EPO_MV = 50         # Value of the slider at the extreme positive end
starting_val = 0    # Initial value of the slider cursor
grpc_needed = True  # set to false if just doing GUI testing without commanding exo


##################################################
###### MODIFY THESE VALUES FOR EACH SUBJECT ######
##################################################

sub_num:int = 1
curr_trial_num:int = 1                                  # Current trial number. Out of 4 repetitions (for now)
current_presentation_num:int = 2                        # Current presentation number. Out of 3 presentations (for now)
torques_per_presentation:int = 4                        # Number of torque options per presentation
torque_settings = np.arange(7.8,28.2,1.7)               # All Torque settings (12 for now)
num_of_tot_torque_settings:int = len(torque_settings)   # Total number of torque settings to sample full torque space