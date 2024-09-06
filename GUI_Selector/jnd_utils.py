import math, random
import numpy as np

class jnd_comparitor:
    def __init__(self, num_bins=21, prop_low=0.3, prop_high=2.0, ref_low=15, ref_high=35, torque_min = 7.5, torque_max = 40):
        self.num_bins = num_bins
        self.prop_low = prop_low
        self.prop_high = prop_high
        self.ref_low = ref_low
        self.ref_high = ref_high
        self.torque_min = torque_min
        self.torque_max = torque_max

        # Bins for sampling
        self.bins = np.linspace(prop_low, prop_high, num_bins)

    def generate_comparison(self):
        count = 0
        while count < 100:
            T_ref = np.random.uniform(low=self.ref_low, high=self.ref_high)
            prop = random.choice(self.bins)

            T_comp = prop * T_ref

            # Clamp to inside max torque, min torque
            if T_comp > self.torque_min and T_comp < self.torque_max:
                break

            # Loop limit
            count += 1

        return prop, T_ref, T_comp, min(math.floor(prop), 1)
