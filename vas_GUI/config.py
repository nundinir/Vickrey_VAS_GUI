import numpy as np

server_ip = f"{'0.0.0.0'}:" f"{'50051'}"    # IP address of the Controller (RPi)

#Initializing the torque mapping button order
button_order = ['D', 'C', 'B', 'A']
button_slider_values = {}
for i in button_order:
    button_slider_values[i] = 0

#Initializing values of the log variables
bool_confirm_button_pressed: bool = False

NPO_MV = -15        # Value of the slider at the extreme negative end
EPO_MV = 50         # Value of the slider at the extreme positive end
starting_val = 0    # Initial value of the slider cursor
grpc_needed = False # set to false if just doing GUI testing without commanding exo

curr_trial_num = 1                                  # Current trial number. Out of 4 repetitions (for now)
current_presentation_num = 1                        # Current presentation number. Out of 3 presentations (for now)
torques_per_presentation = 4                        # Number of torque options per presentation
torque_settings = np.arange(7.8,28.2,1.7)           # All Torque settings (12 for now)
num_of_tot_torque_settings = len(torque_settings)   # Total number of torque settings to sample full torque space