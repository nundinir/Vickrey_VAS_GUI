import math, random
import numpy as np
from constants import REF_LIST

class jnd_comparitor:
    def __init__(self, num_bins=21, prop_low=0.5, prop_high=1.5, ref_list=REF_LIST, torque_min = 7.0, torque_max = 40.0):
        """
        Generate random pairs of comparison from set number of proportions and set references
        """
        self.num_bins = num_bins
        self.prop_low = prop_low
        self.prop_high = prop_high
        self.ref_list = ref_list
        self.torque_min = torque_min
        self.torque_max = torque_max

        # Bins for sampling
        self.bins = np.linspace(prop_low, prop_high, num_bins)

    def generate_comparison(self):
        """
        Create random comparison pair
        Returns proportion, reference torque, comparison torque, and bool indicating if comparison torque is higher
        """
        count = 0
        while count < 100:
            T_ref = random.choice(self.ref_list)
            prop = random.choice(self.bins)

            T_comp = prop * T_ref

            # Clamp to inside max torque, min torque
            if T_comp > self.torque_min and T_comp < self.torque_max:
                break

            # Loop limit
            count += 1

        return prop, T_ref, T_comp, min(math.floor(prop), 1)


if __name__ == "__main__":
    comparitor = jnd_comparitor()

    for _ in range(20):
        print(comparitor.generate_comparison())