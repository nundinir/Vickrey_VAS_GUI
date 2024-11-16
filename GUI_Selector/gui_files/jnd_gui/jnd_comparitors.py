import math, random
import numpy as np
from constants import REF_LIST, TORQUE_MIN, TORQUE_MAX

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
                 run_limit: int = 8, mode: str = 'ascending', init_step_multiplier: int = 10, 
                 up: int = 1, down: int = 1) -> None:
               
        """
        Initialize the KaernbachAlgorithm class.
        
        Args:
            reference_torque (float): The reference torque value (in Nm).
            step_size_right (float): Step size for adjusting the torque when correct answer given(in Nm).
            step_ratio (float): Ratio of step_down/step_up.
            run_limit (int): Number of incorrect responses before algorithm convergence.
            mode (str): Staircase mode, either 'ascending' or 'descending'.
            init_step_multiplier (int): Initial multiplier for the step size for the first comparison.
            up (int): Number of wrong responses after which the distance from the reference will increase.
            down (int): Number of consecutive right responses after which the distance from the reference will decrease.
        """
        
        # staircasing variables
        self.step_size_ratio = step_ratio
        self.step_size_right = step_size_right
        self.step_size_wrong = step_size_right/self.step_size_ratio      # step size when incorrect response given (delta+/up)
        self.init_step_multiplier = init_step_multiplier
        self.init_step_down_multiplier = 2
        self.consec_correct_lim = down
        self.consec_incorrect_lim = up
        self.consec_correct_counter = 0
        self.consec_incorrect_counter = 0
        self.mode = mode
        
        # bounds for the comparison torque
        self.lower_torque_bound = TORQUE_MIN
        self.upper_torque_bound = TORQUE_MAX
        
        # setting inital stimuli
        self.reference_torque = reference_torque
        self.current_comparison_torque = self._initialize_comparison_torque()
        self.next_comparison_torque = self.current_comparison_torque
  
        # termination/convergence criteria
        self.run_limit = run_limit
        self.converged_flag = False
        self.convergence_attempts = 0
        
        # average-of-reversals JND estimator
        self.incorrect_runs = 0
        self.running_comp_torque_array = np.array([])
        
        self.user_decision = None

    def _initialize_comparison_torque(self) -> float:
        """Initializes the starting comparison torque based on mode. Returns clamped torque 
        between lower and upper bounds
        
        If ascending to reference, nearest value to reference_torque that is lower than it will be it's lower bound.
        If descending to reference, nearest value to reference_torque that is greater than it will be it's upper bound.
        
        """
        
        # compile and sort the list of critical torque points into ascending order
        critical_pt_list = [TORQUE_MIN] + REF_LIST + [TORQUE_MAX]
        critical_pt_list.sort()
        
        # find the idx of the reference torque in the sorted list
        idx = critical_pt_list.index(self.reference_torque)
        
        # find the closest lower and upper bounds to the reference torque from the list
        if self.mode == 'ascending':
            closest_lower_bound = critical_pt_list[idx - 1]
            closest_upper_bound = critical_pt_list[idx + 1]
        elif self.mode == 'descending':
            closest_upper_bound = critical_pt_list[idx + 1]
            closest_lower_bound = critical_pt_list[idx - 1]
        
        if self.mode == 'ascending':
            init_comp_torque = self.reference_torque - self.init_step_multiplier * self.step_size_wrong
        elif self.mode == 'descending':
            init_comp_torque = self.reference_torque + self.init_step_multiplier * self.step_size_wrong
        
        # Constrain the initial comparison torque within the closest bounds
        self.lower_torque_bound = closest_lower_bound
        self.upper_torque_bound = closest_upper_bound
        
        return max(self.lower_torque_bound, min(init_comp_torque, self.upper_torque_bound))

    def generate_next_comparison(self, observer_input: bool):
        """
        Generates the next torque comparison based on observer input.
        
        Args:
            observer_input (bool): Observer's response indicating whether they perceive the difference. 
            If they percieve the difference, assume its the correct response for the sake of simulation.
            
        Returns:
            Tuple[float, bool]: Next comparison torque and convergence flag.
        """
        # if the observer has gotten their first incorrect response, switch to the proper up-down staircase
        if self.incorrect_runs < 1:
            if observer_input:
                self.step_size = self.step_size_right*self.init_step_down_multiplier
                self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (1 if self.mode == 'ascending' else -1))
            else:
                # first incorrect response -- increment the next one by step_size_wrong
                self.incorrect_runs +=1
                self.step_size = self.step_size_wrong
                self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (-1 if self.mode == 'ascending' else 1))

        else:
            if observer_input:  # True - correct response
                # TODO: redefine step_size_right depending on comparison distance from reference
                if self.incorrect_runs >= 3:
                    self.step_size_right = 0.5
                self.step_size = self.step_size_right
                self.consec_incorrect_counter = 0  # Reset incorrect counter
                
                # Increment the consecutive correct counter
                self.consec_correct_counter += 1

                # If the consecutive correct counter reaches the limit, decrement the comparison torque
                if self.consec_correct_counter >= self.consec_correct_lim:
                    self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (1 if self.mode == 'ascending' else -1))
                    self.consec_correct_counter = 0  # Reset correct counter after decrementing torque

            else:  # False - incorrect response
                self.incorrect_runs += 1
                # redefine step_size_wrong depending on what step_size_right is
                self.step_size = self.step_size_right/self.step_ratio  
                self.consec_correct_counter = 0  # Reset correct counter
                
                # Increment the consecutive incorrect counter
                self.consec_incorrect_counter += 1
                
                # If the consecutive incorrect counter reaches the limit, increment the comparison torque
                if self.consec_incorrect_counter == self.consec_incorrect_lim:
                    self.next_comparison_torque = self.current_comparison_torque + (self.step_size * (-1 if self.mode == 'ascending' else 1))
                    self.consec_incorrect_counter = 0  # Reset incorrect counter after incrementing torque
                
                 
        if self.incorrect_runs >= 2:
            self.comparison_torque_compiler()
        
        self._apply_bounds()
        self._check_end_criteria()
        
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
        
        2) Terminate if we get close to the reference by the step size, but only 
        the 2nd time we reach this condition. This is done only once for each reference 
        ascending and descending condition.

        """
        if self.incorrect_runs >= self.run_limit:
            self.converged_flag = True
        elif abs(self.current_comparison_torque - self.reference_torque) <= self.step_size_right:
            if self.convergence_attempts == 0:
                self.current_comparison_torque += (self.step_size_wrong * (-1 if self.mode == 'ascending' else 1))
                self.convergence_attempts += 1
            else:
                self.converged_flag = True
                
        print(f'converged_flag: {self.converged_flag}')
        print(f'convergence_attempts: {self.convergence_attempts}')
        
        if self.converged_flag:
            self.find_JND_from_runs()


if __name__ == "__main__":
    comparitor = UniformSampler()

    for _ in range(20):
        print(comparitor.generate_comparison())