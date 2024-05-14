server_ip = f"{'0.0.0.0'}:" f"{'50051'}" # IP address of the Controller (RPi)

#Initializing the torque mapping button order
button_order = ['E', 'D', 'C', 'B', 'A']
button_slider_values = {}
for i in button_order:
    button_slider_values[i] = 0

#Initila values of the log variables
bool_confirm_button_pressed: bool = False
