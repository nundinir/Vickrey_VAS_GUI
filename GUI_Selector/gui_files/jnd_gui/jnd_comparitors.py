import math, random
import numpy as np
from constants import REF_LIST

class UniformSampler:
    def __init__(self, num_bins=21, prop_low=0.5, prop_high=1.5, ref_list=REF_LIST, torque_min = 7.0, torque_max = 40.0):
        """
        Generate random pairs of comparison from a set number of proportions and set references using uniform sampling
        """
        self.num_bins = num_bins
        self.prop_low = prop_low
        self.prop_high = prop_high
        self.ref_list = ref_list
        self.torque_min = torque_min
        self.torque_max = torque_max

        # Bins for sampling
        self.bins = np.linspace(prop_low, prop_high, num_bins)

    def generate_next_comparison(self):
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


class KaernbachAlgorithm:
    def __init__(self, reference_torque: float = 20, step_size_right: float = 0.5, step_ratio: float = 1, 
                 run_limit: int = 8, mode: str = 'ascending', init_step_out_size: int = 11, 
                 consec_correct_lim: int = 2, torque_max_lim: int = 40, torque_min_lim: int = 7) -> None:
               
        """
        Initialize the KaernbachAlgorithm class.
        
        Args:
            reference_torque (float): The reference torque value (in Nm).
            step_size_for_correct_resp (float): Step size for adjusting the torque when correct answer given(in Nm).
            step_ratio (float): Ratio of step_down(correct)/step_up(incorrect).
            run_limit (int): Number of incorrect responses before algorithm convergence.
            mode (str): Staircase mode, either 'ascending' or 'descending'.
            init_step_out_size (int): Initial step size for the first comparison.
            consec_correct_lim (int): Number of consecutive right responses after which the distance from the reference will decrease.
        """
        
        # staircasing variables
        self.step_size_for_correct_resp = step_size_right  # step size when correct response given (delta-/down)     
        self.step_size_ratio = step_ratio                  # ratio of step_down(correct)/step_up(incorrect)
        self.init_step_out_size = init_step_out_size
        
        self.consec_correct_lim = consec_correct_lim
        self.consec_correct_counter = 0
        self.mode = mode
        
        # bounds for the comparison torque
        self.lower_torque_bound = torque_min_lim
        self.upper_torque_bound = torque_max_lim
        
        # setting inital stimuli
        self.reference_torque = reference_torque
        self.current_comparison_torque = self.reference_torque + self.init_step_out_size * (-1 if self.mode == 'ascending' else 1)
        self.next_comparison_torque = self.current_comparison_torque
  
        # termination/convergence criteria
        self.run_limit = run_limit
        self.converged_flag = False
        self.convergence_attempts = 0
        
        # average-of-reversals JND estimator
        self.incorrect_runs = 0
        self.running_comp_torque_array = np.array([])
        
    def compute_step_size(self):
        """Computes step size based on the difference between the reference and comparison torques."""
        stim_diff = abs(self.reference_torque - self.current_comparison_torque)
        
        if stim_diff > 6:
            self.step_size = 2 * self.step_size_for_correct_resp 
        elif (3 <= stim_diff <= 6):
            self.step_size = self.step_size_for_correct_resp 
        elif(1 <= stim_diff < 3):
            self.step_size = self.step_size_for_correct_resp / 2
        else:
            self.step_size = self.step_size_for_correct_resp / 4
    
    def generate_next_comparison(self, observer_input: bool):
        """
        Generates the next torque comparison based on observer input.
        
        Args:
            observer_input (bool): Observer's response indicating whether they perceive the difference.
            
        Returns:
            Tuple[float, bool]: Next comparison torque and convergence flag.
        """
        self.compute_step_size()
        
        if self.incorrect_runs < 1:
            if observer_input:
                self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (1 if self.mode == 'ascending' else -1))
            else:
                # first incorrect response -- increment the next one by step_size_wrong
                self.incorrect_runs +=1
                self.step_size = np.round(self.step_size/self.step_size_ratio,3)
                self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (-1 if self.mode == 'ascending' else 1))

        else:
                
            if observer_input:  # True - correct response
                # Increment the consecutive correct counter
                self.consec_correct_counter += 1

                # If the consecutive correct counter reaches the limit, decrement the comparison torque
                if self.consec_correct_counter >= self.consec_correct_lim:
                    self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (1 if self.mode == 'ascending' else -1))
                    self.consec_correct_counter = 0  # Reset correct counter after decrementing torque

            else:  # False - incorrect response
                self.incorrect_runs += 1
                self.step_size = np.round(self.step_size/self.step_size_ratio,3)  
                self.consec_correct_counter = 0  # Reset correct counter

                self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (-1 if self.mode == 'ascending' else 1))
        
        if self.incorrect_runs >= 2:
            self.comparison_torque_compiler()
        
        self._check_end_criteria()
        self._apply_bounds()
        
        self.next_comparison_torque = np.round(self.next_comparison_torque, 3)
        
        return self.next_comparison_torque
    
    def comparison_torque_compiler(self):
        """Compiles all the comparison torques from the last 6 runs."""
        self.running_comp_torque_array = np.append(self.running_comp_torque_array, self.next_comparison_torque)
        
    def find_JND_from_runs(self):
        """Finds the average torque from the last 6 runs to get the JND estimate."""
        avg_JND = np.mean(self.running_comp_torque_array)
        self.normd_JND = abs(avg_JND - self.reference_torque)
        print(f'Normd JND estimate for {self.reference_torque} Nm reference in the {self.mode} mode is: {self.normd_JND}')

    def _apply_bounds(self) -> None:
        """Ensures the comparison torque stays within defined bounds."""
        if self.next_comparison_torque < self.lower_torque_bound:
            self.next_comparison_torque = self.lower_torque_bound
        elif self.next_comparison_torque > self.upper_torque_bound:
            self.next_comparison_torque = self.upper_torque_bound

    def _check_end_criteria(self) -> None:
        """
        Check for Termination conditions:
        
        1) Terminate if the number of incorrect responses == run limit (8) OR
        
        2) Terminate if we correctly get close to the reference by the step size, but only 
        the 2nd time we reach this condition. This is done only once for each reference 
        ascending and descending condition.

        """
        if self.incorrect_runs >= self.run_limit:
            self.converged_flag = True
        elif (abs(self.current_comparison_torque - self.reference_torque) <= self.step_size_for_correct_resp/2):
            self.convergence_attempts += 1
            
            if self.convergence_attempts == 1:
                self.step_size = np.round(self.step_size/self.step_size_ratio,3)
                self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (-1 if self.mode == 'ascending' else 1))
                # self.convergence_attempts += 1
                self.converged_flag = False
            elif self.convergence_attempts >= 2:
                self.converged_flag = True
            else:
                self.converged_flag = True
        else:
            self.converged_flag = False
        
        if self.converged_flag:
            self.find_JND_from_runs()


if __name__ == "__main__":
    comparitor = UniformSampler()

    for _ in range(20):
        print(comparitor.generate_comparison())