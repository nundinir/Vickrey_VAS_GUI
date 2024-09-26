import time, random
import numpy as np

from constants import *
from Robobidders import *
from jnd_utils import jnd_comparitor

from constants import BTN_NUMS, MAX_TRIALS_DICT, MAX_PRESENTATIONS_DICT

# Statemachine class
class VickreyStateMachine:
    def __init__(self, screenmanager):
        self.sm = screenmanager

        # Init RoboBidders
        self.robomodel = roboModel(k_RB, b_RB, 2)
        self.auction_tally = 0 # Starts from 0th auction

        # Auction state
        self.state = False
        self.prev_state = False
        self.total_winnings = 0

        # Auction stats
        self.winning_bid = 0
        self.payout = 0

        # Screen states
        self.next_screen_dict = {"dummy": "pushtostartscreen", 
                                 "pushtostartscreen": "numpad", 
                                 "numpad": "survey",
                                 "survey": "resultscreen"
                                 }

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

        # Clamp bid
        subject_bid = max(min(subject_bid, MAX_BID), 0)

        # Get all bids from subject/robobidders
        all_bids = [subject_bid]
        all_bids.extend(self.robomodel.get_bids())

        # Get winner
        ordered_bids = sorted(all_bids)
        self.winning_bid = ordered_bids[0]
        winning_bid_idx = all_bids.index(self.winning_bid)

        # Get payout (Second price)
        self.payout = ordered_bids[1] 

        # Find if subject won
        if winning_bid_idx == 0:
            state = True
            self.total_winnings += self.payout
        else:
            state = False
            robo_walk_time = ROBOWALK_DUR * (self.auction_tally + 1)
            self.robomodel.robobidderlist[winning_bid_idx-1].walk(robo_walk_time, 0)

        # Update auction states
        self.prev_state = self.state
        self.state = state

        # Auction logging values
        t = (self.auction_tally + 1) * ROBOWALK_DUR

        # Send auction results to auctionhouse
        self.sm.exoboot_remote.call(t, subject_bid, self.state, self.payout, self.total_winnings) #, winning_bid)

        # Increment auction tally
        self.auction_tally += 1

    def close_survey(self,  *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        t = self.auction_tally * ROBOWALK_DUR
        self.sm.exoboot_remote.question(t, self.sm.enjoyment, self.sm.rpe)

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        self.sm.current = self.next_screen_dict[self.sm.current]


class VASStateMachine:
    def __init__(self, screenmanager, startstamp):
        self.sm = screenmanager
        self.startstamp = startstamp

        # Setting up Torque options
        self.num_of_tot_torque_settings = BTN_NUM_TOTAL # Total number of torque settings (Maintain 12 for practicality)
        self.torque_settings = np.linspace(TORQUE_MIN, TORQUE_MAX, self.num_of_tot_torque_settings)
        
        # Trial/Presentation States
        self.current_btn_option = 0
        self.current_trial = 0
        self.current_presentation = 0

        self.button_mappings = {}
        self.vas_btn_trial_pres = []
        self.generate_btn_trial_pres_list()
        self.generate_button_torque_mapping()

        # Screen states
        self.next_screen_dict = {"dummy": "pushtostartscreen", 
                                 "pushtostartscreen": "vasscreen",
                                 "vasscreen": "waitingscreenvas",
                                 "waitingscreenvas": "pushtostartscreen"
                                 }

        # Quit flag
        self.quit_flag = False

    def generate_btn_trial_pres_list(self):
        for btn in BTN_NUMS:
            for trial in range(1, MAX_TRIALS_DICT[btn] + 1):
                for presentation in range(1, MAX_PRESENTATIONS_DICT[btn] + 1):
                    self.vas_btn_trial_pres.append([btn, trial, presentation])

    def generate_button_torque_mapping(self):
        for btn_num in BTN_NUMS:
            trial_mappings = {}
            for trial in range(1, MAX_TRIALS_DICT[btn_num] + 1):
                np.random.seed(trial)

                pseudo_random_presentation_torques = np.random.choice(self.torque_settings, size = self.num_of_tot_torque_settings, replace=False)

                presentation_mappings = {1: pseudo_random_presentation_torques[0:btn_num],
                                         2: pseudo_random_presentation_torques[btn_num:btn_num*2],
                                         3: pseudo_random_presentation_torques[btn_num*2:self.num_of_tot_torque_settings]}

                trial_mappings[trial] = presentation_mappings

            self.button_mappings[btn_num] = trial_mappings

    def get_torque(self, ind):
        return self.button_mappings[self.current_btn_option][self.current_trial][self.current_presentation][ind]

    def next_trial_pres(self):
        [self.current_btn_option, self.current_trial, self.current_presentation] = self.vas_btn_trial_pres.pop(0)
        self.overtime_dict = {self.get_torque(i):0 for i in range(self.current_btn_option)}

        # Send overtime info
        self.sm.exoboot_remote.update_vas_info(self.current_btn_option, self.current_trial, self.current_presentation)

        # Quit after next screen if no more trial/pres left
        if len(self.vas_btn_trial_pres) < 1:
            self.quit_flag  = True
        
    def log_overtime(self, torque, mv):
        pitime = time.perf_counter() - self.startstamp
        self.overtime_dict[torque] = mv
        self.sm.exoboot_remote.slider_update(pitime, self.overtime_dict)

    def presentation_result(self, torques, values):
        self.sm.exoboot_remote.presentation_result(self.current_btn_option, self.current_trial, self.current_presentation, torques, values)

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        if self.quit_flag:
            self.sm.current = 'finishscreenvas'
        else:
            self.sm.current = self.next_screen_dict[self.sm.current]


class JNDStateMachine:
    def __init__(self, screenmanager, jnd_type='SPLITLEG'):
        self.sm = screenmanager
        self.jnd_type = jnd_type.upper()

        # JND Comparitor
        self.comparitor = jnd_comparitor(num_bins=NUM_BINS, prop_low=PROP_LOW, prop_high=PROP_HIGH, ref_low=REF_LOW, ref_high=REF_HIGH, torque_min=TORQUE_MIN, torque_max=TORQUE_MAX)

        # State tracking
        self.pres = 0
        self.prop = 0
        self.T_ref = 0
        self.T_comp = 0
        self.truth = 0

        # Time limit
        self.subtrial_limit = False

        # Quit flag
        self.quit_flag = False

        # Screen states dictionary
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
                self.next_comparison = self.next_comparison_same
                self.report_higher = self.report_higher_same

                self.peak_torques = []
                self.peak_torque_ind = 0

                self.next_screen_dict["pushtostartscreenjnd"] = "samelegscreen"
                self.next_screen_dict["samelegscreen"] = "waitingscreenjnd"

    def next_comparison_split(self):
        if self.pres >= MAX_QUERIES:
            self.quit_flag = True
            self.next_screen()
        else:
            self.prop, self.T_ref, self.T_comp, truth = self.comparitor.generate_comparison()
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
        if self.pres >= MAX_QUERIES:
            self.quit_flag = True
            self.next_screen()
        else:
            self.prop, self.T_ref, self.T_comp, truth = self.comparitor.generate_comparison()
            self.pres += 1

            self.peak_torque_ind = 0
            if random.getrandbits(1):
                self.peak_torques = [self.T_ref, self.T_comp]
                self.truth = int(truth)
            else:
                self.peak_torques = [self.T_comp, self.T_ref]
                self.truth = int(not truth)

            self.sm.exoboot_remote.set_torques(peak_torque_left=self.peak_torques[self.peak_torque_ind], peak_torque_right=self.peak_torques[self.peak_torque_ind])

    def report_higher_split(self, signature):
        self.sm.exoboot_remote.comparison_result(self.pres, self.prop, self.T_ref, self.T_comp, self.truth, signature)
        if not self.subtrial_limit:
            self.next_comparison()
        else:
            self.next_screen()

    def report_higher_same(self):
        self.sm.exoboot_remote.comparison_result(self.pres, self.prop, self.T_ref, self.T_comp, self.truth, self.peak_torque_ind)
        if not self.subtrial_limit:
            self.next_comparison()
        else:
            self.next_screen()

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        if self.quit_flag:
            self.sm.current = 'finishscreenjnd'
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
                                 "waitingscreenpref": "pushtostartscreenpref"}

        # Next screen based on pref type
        match self.pref_type:
            case 'SLIDER':
                self.next_screen_dict["pushtostartscreenpref"] = "sliderscreen"
                self.next_screen_dict["sliderscreen"] = "waitingscreenpref"
            case 'BTN':
                self.next_screen_dict["pushtostartscreenpref"] = "btnscreen"
                self.next_screen_dict["btnscreen"] = "waitingscreenpref"

    def report_pref(self, torque):
        self.sm.exoboot_remote.pref_result(self.pres, torque)
        self.pres += 1
        if self.pres > MAX_PRES_PREF - 1:
            self.quit_flag = True
        self.next_screen()

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        if self.quit_flag:
            self.sm.current = 'finishscreenpref'
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
