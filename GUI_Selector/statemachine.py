import csv, time, random
import numpy as np
import math, random
import os

from constants import *
from gui_files.vickrey_gui.Robobidders import *
from gui_files.jnd_gui.jnd_comparitors import UniformSampler
from gui_files.jnd_gui.jnd_comparitors import KaernbachAlgorithm
from shared_files.SoftRTloop import FlexibleSleeper
from shared_files.utils import Pickler

from constants import (
    BTN_NUMS, MAX_TRIALS_DICT, MAX_PRESENTATIONS_DICT, REF_LIST, TORQUE_MIN, 
    TORQUE_MAX, RIGHT_LIM, RATIO, STEP_SIZE_RIGHT_DICT, 
    RUN_LIMIT, MODES
)

# Statemachine class
class VickreyStateMachine:
    def __init__(self, screenmanager, num_robobidders=NUM_ROBOBIDDERS):
        self.sm = screenmanager

        # Check if loaded backup
        self.backupflag = False

        # Init RoboBidders
        self.num_robobidders = num_robobidders
        self.robomodel = roboModel(k_RB, b_RB, self.num_robobidders)
        self.auction_tally = 0 # Starts from 0th auction

        # Auction state
        self.state = False
        self.prev_state = False
        self.total_winnings = 0

        # Auction stats
        self.winning_bid = 0
        self.payout = 0

        # Screen states
        self.queued_screen = None
        self.next_screen_dict = {"dummy": "pushtostartscreen", 
                                 "pushtostartscreen": "numpad", 
                                 "numpad": "survey",
                                 "survey": "resultscreen"
                                 }

    def loadstate(self, states_dict: dict):
        self.auction_tally = int((states_dict["t"])/ 2) + 1
        self.state = states_dict["state"]
        self.prev_state = states_dict["prev_state"]
        self.total_winnings = states_dict["total_winnings"]
        self.robomodel.loadstate(states_dict["robostates"])
        
        self.backupflag = True

    def determine_auction(self):
        no_bid = not self.sm.bid
        no_prev_bid = not self.sm.previous_bid
        # Convert bid from string to float
        if not no_bid:
            subject_bid = float(self.sm.bid) * 0.01
            self.sm.previous_bid = self.sm.bid
        elif not no_prev_bid:
            subject_bid = float(self.sm.previous_bid) * 0.01
            self.sm.bid = self.sm.previous_bid
        else:
            subject_bid = 0

        # Clamp subject bid and round to 2 decimal places
        subject_bid = round(max(min(subject_bid, MAX_BID), 0), 2)

        # Get robobids
        robobids = self.robomodel.get_bids()
        print("BIDS: ", subject_bid, robobids)

        # Determine winning bid and all winners
        all_bids = [subject_bid] + robobids
        self.winning_bid = min(all_bids)
        winners = [bid == self.winning_bid for bid in all_bids]
        subject_win_flag = winners[0]
        print("WINNERS", winners)

        # Get payout (Second price)
        second_prices = sorted([i for i in all_bids if i != self.winning_bid])
        
        # Determine payout
        if second_prices:
            self.payout = second_prices[0]
        else:
            self.payout = self.winning_bid

        # Determine subject auction results
        if subject_win_flag:
            state = True
            self.total_winnings += self.payout
        else:
            state = False
        
        # Robowalks
        robo_walk_time = ROBOWALK_DUR * (self.auction_tally + 1)
        for ind, robo_win_state in enumerate(winners[1:]):
            if robo_win_state:
                self.robomodel.robobidderlist[ind].walk(robo_walk_time, 0)

        # Update auction states
        self.prev_state = self.state
        self.state = state

        # Auction logging values
        t = self.auction_tally * ROBOWALK_DUR

        # Send auction results to auctionhouse
        self.sm.exoboot_remote.call(t, subject_bid, self.state, self.payout, self.total_winnings)

        # Save to backup
        auctionpath = self.sm.filingcabinet.getpath("auction")
        with open(auctionpath, 'a', newline='') as f:
            auction_backup = [t, subject_bid, self.state, self.payout, self.total_winnings]
            auction_backup.extend(self.robomodel.getstate())
            csv.writer(f).writerow(auction_backup)

        # Increment auction tally
        self.auction_tally += 1

    def close_survey(self,  *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        t = self.auction_tally * ROBOWALK_DUR
        self.sm.exoboot_remote.question(t, self.sm.enjoyment, self.sm.rpe)

    def queue_screen(self, screen):
        """
        Queue screen on next next_screen
        """
        self.queued_screen = screen

    def next_screen(self, *vargs):
        """
        Move to next screen according to queued_screen, then next_screen_dict
        Ignore vargs. exists so next can be called by Clock.schedule_once
        """ 
        if self.queued_screen:
            self.sm.current = self.queued_screen
            self.queued_screen = None
        else:
            self.sm.current = self.next_screen_dict[self.sm.current]


class VASStateMachine:
    def __init__(self, screenmanager, startstamp):
        self.sm = screenmanager
        self.startstamp = startstamp
        
        # Trial/Presentation States
        self.current_btn_option = 0
        self.current_trial = 0
        self.current_presentation = 0

        self.button_mappings = {}
        self.vas_btn_trial_pres = []
        self.generate_btn_trial_pres_list()
        self.generate_button_torque_mapping()

        # Screen states
        self.queued_screen = None
        self.next_screen_dict = {"dummy": "pushtostartscreen", 
                                 "pushtostartscreen": "vasscreen",
                                 "vasscreen": "waitingscreenvas",
                                 "waitingscreenvas": "pushtostartscreen"
                                 }

        # Quit flag
        self.quit_flag = False

    @staticmethod
    def evensampler(base_list):
        """
        Create list for evenly subsampling from base list
        """
        base_ordered = base_list[::2] + base_list[1::2]
        return base_ordered

    def generate_btn_trial_pres_list(self):
        """
        Create list of button, trial, presentation combos
        """
        for btn in BTN_NUMS:
            for trial in range(1, MAX_TRIALS_DICT[btn] + 1):
                for presentation in range(1, MAX_PRESENTATIONS_DICT[btn] + 1):
                    self.vas_btn_trial_pres.append([btn, trial, presentation])

    def generate_button_torque_mapping(self):
        """
        Generate presentations (groups of buttons) for each trial
        Generates the same mapping every time (intended)
        """
        num_torques = {btn_num: btn_num * MAX_PRESENTATIONS_DICT[btn_num] for btn_num in BTN_NUMS}
        max_num = max(num_torques.values())

        torque_list = list(np.linspace(TORQUE_MIN, TORQUE_MAX, max_num).round(decimals=3))
        ordered_torques = self.evensampler(torque_list)

        for btn_num in BTN_NUMS:
            # Setting up Torque options
            num = num_torques[btn_num]
            torques = ordered_torques[:num]
            torques.sort()

            print("{}: {}".format(btn_num, torques))

            trial_mappings = {}
            for trial in range(1, MAX_TRIALS_DICT[btn_num] + 1):
                random.seed(trial)
                available_torques = torques[:]
                random.shuffle(available_torques)

                presentation_mappings = {}
                for p in range(1, MAX_PRESENTATIONS_DICT[btn_num] + 1):
                    pres_torques = []
                    for _ in range(btn_num):
                        pres_torques.append(available_torques.pop(0))
                    presentation_mappings[p] = pres_torques

                trial_mappings[trial] = presentation_mappings

            self.button_mappings[btn_num] = trial_mappings

    def peak_btp(self):
        if self.vas_btn_trial_pres:
            [b, t, p] = self.vas_btn_trial_pres[0]
            return b, t, p
        else:
            return -1, -1, -1

    def loadstate(self, btpcompleted):
        """
        Remove completed btp from vas_btn_trial_pres list
        """
        for btp in btpcompleted:
            try:
                self.vas_btn_trial_pres.remove(btp)
            except:
                pass

    def get_torque(self, ind):
        """
        Return torque (Nm) for a given btp
        """
        return self.button_mappings[self.current_btn_option][self.current_trial][self.current_presentation][ind]

    def next_trial_pres(self):
        """
        Returns next btp to query
        """
        [self.current_btn_option, self.current_trial, self.current_presentation] = self.vas_btn_trial_pres.pop(0)
        self.overtime_dict = {self.get_torque(i):0 for i in range(self.current_btn_option)}

        # Send overtime info
        self.sm.exoboot_remote.update_vas_info(self.current_btn_option, self.current_trial, self.current_presentation)

        # Quit after next screen if no more trial/pres left
        if len(self.vas_btn_trial_pres) < 1:
            self.quit_flag  = True
        
    def log_overtime(self, torque, mv):
        """
        Log slider movements when moving
        """
        pitime = time.perf_counter() - self.startstamp
        self.overtime_dict[torque] = mv
        self.sm.exoboot_remote.slider_update(pitime, self.overtime_dict)

    def presentation_result(self, torques, values):
        """
        Send presentation results to pi
        Save backup
        """
        self.sm.exoboot_remote.presentation_result(self.current_btn_option, self.current_trial, self.current_presentation, torques, values)

        # Save backup
        datalist = [self.current_btn_option, self.current_trial, self.current_presentation]
        for t, mv in zip(torques, values):
            datalist.append(t)
            datalist.append(mv)

        vasresultspath = self.sm.filingcabinet.getpath("vasresults")
        with open(vasresultspath, 'a', newline='') as f:
            csv.writer(f).writerow(datalist)

    def queue_screen(self, screen):
        """
        Queue screen on next next_screen
        """
        self.queued_screen = screen

    def next_screen(self, *vargs):
        """
        Move to next screen depending on conditions
        """
        if self.quit_flag:
            self.sm.current = 'finishscreenvas'
        elif self.queued_screen:
            self.sm.current = self.queued_screen
            self.queued_screen = None
        else:
            self.sm.current = self.next_screen_dict[self.sm.current]


class JNDStateMachine:
    def __init__(self, screenmanager, jnd_type='SPLITLEG', which_comparitor="UNIFORM"):
        self.sm = screenmanager
        self.jnd_type = jnd_type.upper()
        self.which_comparitor = which_comparitor.upper()

        # JND Comparitor
        match self.which_comparitor:
            case "UNIFORM":
                self.comparitor = UniformSampler(num_bins=NUM_BINS, prop_low=PROP_LOW, prop_high=PROP_HIGH, ref_list=REF_LIST, torque_min=TORQUE_MIN, torque_max=TORQUE_MAX)
                self.walknum = 0
                self.pres = 0
            case "STAIR":
                # instantiate a pickler object
                self.pickler = Pickler()
                
                # Create the list of tuples with reference torques and modes
                self.create_staircase_combos()  
                
                if os.path.exists(PICKLE_FILE_PATH):
                    try:
                        print("pickle file exists so loading it up")
                        self.staircases, last_walknum, self.pres = self.pickler.load_staircases_and_vars(PICKLE_FILE_PATH)  # Load the staircases from the Pickle file
                        self.walknum = last_walknum + 1
                        self.converged_staircases = len(self.staircase_combinations) - len(self.staircases)
                    except:
                        print("pickle file exists BUT FAILED to load")
                else:   
                    print("pickle file DNE so instantiating new staircases")
                    self.create_fresh_staircases()      # Initialize new staircases: Kaernbach Algorithm
                    self.walknum = 0
                    self.pres = 0
                    self.pickler.save_staircases_and_vars(self.staircases, self.walknum, self.pres, PICKLE_FILE_PATH)    # save the initialized staircases and other vars to a pickle file
                    
            case _:
                Exception("Invalid comparitor type")

        # State tracking
        self.prop = 0
        self.T_ref = 0
        self.T_comp = 0
        self.truth = 0

        # Time limit
        self.subtrial_limit = False

        # Quit flag
        self.quit_flag = False

        # Screen states dictionary
        self.queued_screen = None
        self.next_screen_dict = {"dummy": "pushtostartscreenjnd",
                                 "waitingscreenjnd": "pushtostartscreenjnd"}

        # Next screen based on jnd type
        match jnd_type:
            case 'SPLITLEG':
                # Set Split Leg Funcs
                self.next_comparison = self.next_comparison_split
                self.report_higher = self.report_higher_split

                self.peak_torque_left = 0
                self.peak_torque_right = 0

                self.next_screen_dict["pushtostartscreenjnd"] = "splitlegscreen"
                self.next_screen_dict["splitlegscreen"] = "waitingscreenjnd"
            case 'SAMELEG':
                if self.which_comparitor == "UNIFORM":
                    self.next_comparison = self.next_comparison_same
                    self.report_higher = self.report_higher_same
                elif self.which_comparitor == "STAIR":
                    self.next_comparison = self.next_comparison_same_stair
                    self.report_higher = self.report_higher_same_stair

                self.peak_torques = []
                self.peak_torque_ind = 0

                self.next_screen_dict["pushtostartscreenjnd"] = "samelegscreen"
                self.next_screen_dict["samelegscreen"] = "waitingscreenjnd"
        

    def loadstate(self, pres):
        """
        Start from previous pres number
        """
        self.pres = pres

    def next_comparison_split(self):
        """
        Assigns torque pair to randomly selected sides
        """
        if self.pres >= MAX_QUERIES:
            self.quit_flag = True
            self.next_screen()
        else:
            self.prop, self.T_ref, self.T_comp, truth = self.comparitor.generate_next_comparison()
            self.pres += 1

            if random.getrandbits(1):
                self.peak_torque_left = self.T_ref
                self.peak_torque_right = self.T_comp
                self.truth = int(truth)

            else:
                self.peak_torque_left = self.T_comp
                self.peak_torque_right = self.T_ref
                self.truth = int(not truth)

            self.sm.exoboot_remote.set_torques(peak_torque_left=self.peak_torque_left, peak_torque_right=self.peak_torque_right)

    def next_comparison_same(self):
        """
        Assigns torque pair to randomly selected swap button state
        """
        if self.pres >= MAX_QUERIES:
            self.quit_flag = True
            self.next_screen()
        else:
            self.prop, self.T_ref, self.T_comp, truth = self.comparitor.generate_next_comparison()
            self.pres += 1

            self.peak_torque_ind = 0 
            if random.getrandbits(1):
                self.peak_torques = [self.T_ref, self.T_comp]
                self.truth = int(truth)
            else:
                self.peak_torques = [self.T_comp, self.T_ref]
                self.truth = int(not truth)

            self.sm.exoboot_remote.set_torques(peak_torque_left=self.peak_torques[self.peak_torque_ind], peak_torque_right=self.peak_torques[self.peak_torque_ind])
        
    def create_staircase_combos(self):
        """Creates list of tuples with combos of reference torque, mode, and repetition. 
        Contained within staircase_combinations attribute. Sets seed for reproducibility and shuffles."""
        
        self.staircase_combinations = [(ref_torque, mode) 
                        for ref_torque in REF_LIST 
                        for mode in MODES]

        # Setting seed for reproducibility & shuffling
        seed = 2
        random.seed(seed)
        random.shuffle(self.staircase_combinations)
        print(f"Staircase combos created: {self.staircase_combinations}")

    def create_fresh_staircases(self):
        """ Instantiates the randomly interleaved staircase objects and 
        saves FOR THE FIRST TIME to a Pickle file. Sets converged_staircases and presentation to 0."""
        self.staircases = []
        for ref_torque, mode in self.staircase_combinations:
            step_size_right = STEP_SIZE_RIGHT_DICT[ref_torque]
            self.comparitor = KaernbachAlgorithm(reference_torque=ref_torque,
                                                step_size_right=step_size_right, 
                                                step_ratio=RATIO,
                                                run_limit=RUN_LIMIT, 
                                                mode=mode, 
                                                init_step_out_size=INIT_STEP_OUT_SIZE,
                                                consec_correct_lim=RIGHT_LIM, 
                                                torque_max_lim=TORQUE_MAX, 
                                                torque_min_lim=TORQUE_MIN)
            self.staircases.append((self.comparitor, ref_torque, mode))
            self.converged_staircases = 0
            self.pres = 0
            
        print(f"Staircases instantiated: {self.staircases}")
        
    def next_comparison_same_stair(self):
        """
        Assigns torque pair to randomly selected swap button state according to kaernbach algorithm
        """
        print(f"len of staircases: {len(self.staircases)}")
        if self.converged_staircases == len(self.staircase_combinations):
            self.quit_flag = True
            self.pickler.remove_pickle_file(PICKLE_FILE_PATH)
            self.next_screen()
        else:
            # Calculate the starting index of circular roll
            self.pres += 1          # increment presentation number
            start_index = self.pres % len(self.staircases)
            
            # Circularly roll through the list of tuples containing staircase objects, refs, and modes
            rolling_staircase_list = self.staircases[start_index:] + self.staircases[:start_index]
            
            # Extract the staircase object, ref_torque, and mode from the first tuple
            self.selected_staircase, ref_torque, self.mode = rolling_staircase_list[0]

            # print out components for debugging
            print(f"Selected Stair Reference Torque: {ref_torque}")
            print(f"Selected Stair Mode: {self.mode}")
            
            # if the selected_staircase hasn't converged, generate the next comparison torque
            if not self.selected_staircase.converged_flag:
                
                self.T_ref = ref_torque
                self.T_comp = self.selected_staircase.current_comparison_torque
                truth = min(math.floor(self.T_comp/self.T_ref), 1)  # indicator for which torque is higher (0: T_comp, 1: T_ref) 
                  
                # shuffle the peak torques for ref and comparison presentation
                self.peak_torque_ind = 0
                if random.getrandbits(1):
                    self.peak_torques = [self.T_ref, self.T_comp]
                    self.truth = int(truth)
                else:
                    self.peak_torques = [self.T_comp, self.T_ref]
                    self.truth = int(not truth)
                    
                print(f"Currently Presented Comparison Torque: {self.T_comp}")
                print(f"Diff is: {abs(self.T_comp - self.T_ref)}")
                
                # present current comparison vs ref
                self.sm.exoboot_remote.set_torques(peak_torque_left=self.peak_torques[self.peak_torque_ind], peak_torque_right=self.peak_torques[self.peak_torque_ind])
                
    def report_higher_split(self, signature):
        """
        Reports result of comparison
        """
        self.sm.exoboot_remote.comparison_result(self.pres, self.prop, self.T_ref, self.T_comp, self.truth, signature)

        # Log backup
        comparisonpath = self.sm.filingcabinet.getpath("comparison")
        with open(comparisonpath, 'a', newline='') as f:
            csv.writer(f).writerow([self.pres, self.prop, self.T_ref, self.T_comp, self.truth, signature])

        if not self.subtrial_limit:
            self.next_comparison()
        else:
            self.next_screen()

    def report_higher_same(self):
        """
        Reports result of comparison
        """
        self.sm.exoboot_remote.comparison_result(self.pres, self.prop, self.T_ref, self.T_comp, self.truth, self.peak_torque_ind)

        # Log backup
        comparisonpath = self.sm.filingcabinet.getpath("comparison")
        with open(comparisonpath, 'a', newline='') as f:
            csv.writer(f).writerow([self.pres, self.prop, self.T_ref, self.T_comp, self.truth, self.peak_torque_ind])

        if not self.subtrial_limit:
            self.next_comparison()
        else:
            self.next_screen()
            

    def report_higher_same_stair(self):
        """
        Reports result of comparison
        """
        self.prop = self.T_comp/self.T_ref
        self.sm.exoboot_remote.comparison_result(self.pres, self.prop, self.T_ref, self.T_comp, self.truth, self.peak_torque_ind)
        user_decided_torque = self.peak_torques[self.peak_torque_ind]
        
        # if the user_decision is the same as the truth, 
        if self.peak_torque_ind == self.truth:
            user_decision = True
        else:
            user_decision = False
            
        # print(f"User Decision: {user_decision}")
        
        # generate next comparison torque based on observer response for current comparison torque
        next_comparison_torque = self.selected_staircase.generate_next_comparison(user_decision)
        # print(f"Next Comparison Torque: {next_comparison_torque}")
        
        # set the current comparison torque to the next comparison torque for the selected_staircase evaluation
        self.selected_staircase.current_comparison_torque = next_comparison_torque
        
        # if the selected_staircase has converged, remove the particular staircase from the list
        if self.selected_staircase.converged_flag:
            print("A staircase has converged!")
            self.staircases.remove((self.selected_staircase, self.T_ref, self.mode))
            self.converged_staircases += 1
            print(f"self.staircases is now: {self.staircases}")

        # Log backup variables
        comparisonpath = self.sm.filingcabinet.getpath("comparison")
        with open(comparisonpath, 'a', newline='') as f:
            csv.writer(f).writerow([self.pres, 
                                    self.mode, 
                                    self.T_ref, 
                                    self.T_comp, 
                                    self.truth, 
                                    self.peak_torque_ind, 
                                    self.selected_staircase.converged_flag, 
                                    self.selected_staircase.consec_correct_counter,
                                    self.selected_staircase.step_size,
                                    self.selected_staircase.convergence_attempts,])
            
        # Update the saved pickle file
        self.pickler.save_staircases_and_vars(self.staircases, self.walknum, self.pres, PICKLE_FILE_PATH) 
        
        if not self.subtrial_limit:
            self.next_comparison()
        else:
            self.next_screen()

    def queue_screen(self, screen):
        """
        Queue screen on next next_screen
        """
        self.queued_screen = screen

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        if self.quit_flag:
            self.sm.current = 'finishscreenjnd'
        elif self.queued_screen:
            self.sm.current = self.queued_screen
            self.queued_screen = None
        else:
            self.sm.current = self.next_screen_dict[self.sm.current]


class PrefStateMachine:
    def __init__(self, screenmanager, pref_type='SLIDER'):
        self.sm = screenmanager
        self.pref_type = pref_type.upper()

        self.pres = 0

        # Quit flag
        self.quit_flag = False

        # Screen states dictionary
        self.next_screen_dict = {"dummy": "pushtostartscreenpref",
                                 "walkscreenpref": "waitingscreenpref",
                                 "waitingscreenpref": "pushtostartscreenpref"}

        # Next screen based on pref type
        match self.pref_type:
            case 'SLIDER':
                self.next_screen_dict["pushtostartscreenpref"] = "sliderscreen"
                self.next_screen_dict["sliderscreen"] = "walkscreenpref"
            case 'BUTTON':
                self.next_screen_dict["pushtostartscreenpref"] = "btnscreen"
                self.next_screen_dict["btnscreen"] = "walkscreenpref"
            case 'DIAL':
                self.next_screen_dict["pushtostartscreenpref"] = "dialscreen"
                self.next_screen_dict["dialscreen"] = "waitingscreenpref"
                

    def report_pref(self, torque, *vargs):
        """
        Sends preferred torque to pi
        """
        self.sm.exoboot_remote.pref_result(self.pres, torque)
        self.pres += 1
        if self.pres >= MAX_PRES_PREF:
            self.quit_flag = True
        self.next_screen()

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        if self.quit_flag:
            self.sm.current = "finishscreenpref"
        else:
            self.sm.current = self.next_screen_dict[self.sm.current]


class AcclimationStateMachine:
    def __init__(self, screenmanager):
        self.sm = screenmanager

        # Screen states dictionary
        self.next_screen_dict = {"dummy": "pushtostartscreenaccl",
                                 "pushtostartscreenaccl": "sliderscreen",
                                 "sliderscreen": "finishscreenaccl"}

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        self.sm.current = self.next_screen_dict[self.sm.current]


class SpeedFinderStateMachine:
    # TODO implement way to get steps from exoboot_remote???
    # TODO
    def __init__(self, screenmanager):
        self.sm = screenmanager

        # Screen states dictionary
        self.next_screen_dict = {"dummy": "pushtostartscreensf",
                                 "pushtostartscreensf": "speedfinderscreen",
                                 "speedfinderscreen": "finishscreensf"}

        self.IsOptimized = False

    @staticmethod
    def clamp_v(v, vmin=VMIN, vmax=VMAX):
        return min(max(v, vmin), vmax)

    def estimate_new_v(self, v1, f1, f2):
        """
        Walk Ratio invariance formula
        """
        v2 = f2**2/f1**2 * v1
        return self.clamp_v(v2)

    def runoptimizer(self, f_target=F_TARGET, v_init=V_INITIAL, sleeptime=SLEEPTIME):
        v_set = self.clamp_v(v_init)

        # while not self.IsOptimized:
        #     self.bertec.write_command(v_set, v_set, incline=None, accR=0.5, accL=0.5)

        #     # Wait for walking to occur
        #     time.sleep(sleeptime)

        #     # Get cadence/speed
        #     f = self.sm.exoboot_remote.getspm()
        #     v = self.bertec.speed # m/s

        #     # Predict new v to reach spm criteria
        #     v_set = self.estimate_new_v(v, f, f_target)

        #     # Finish if target is v_set is close to target cadence
        #     self.IsOptimized = abs((f - f_target)/f_target) < ERROR_THRESHOLD

        # # Report when done
        # self.sm.exoboot_remote.foundspeed(v_set)
        self.next_screen()

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        self.sm.current = self.next_screen_dict[self.sm.current]


if __name__ == "__main__":
    """
    Display VAS Trial/Presentation Torques
    """
    testvas = VASStateMachine(None, time.perf_counter())

    print("B T P Torques")
    for btn, trials in testvas.button_mappings.items():
        trial_torques = []
        for t, trial in trials.items():
            for p, pres in trial.items():
                print(btn, t, p, pres)
            print()
