server_ip = f"{'0.0.0.0'}:" f"{'50051'}" # IP address of the Controller (RPi)
num_torques = 5  # Number of torque options
NPO_MV = -15    # Value of the slider at the extreme negative end
EPO_MV = 50 # Value of the slider at the extreme positive end
starting_val = 0 # Initial value of the slider cursor
grpc_needed = False # set to false if just doing GUI testing without commanding exo