import time, random
import numpy as np

from constants import *
from gui_files.vickrey_gui.Robobidders import *
from gui_files.jnd_gui.jnd_utils import jnd_comparitor

from constants import BTN_NUMS, MAX_TRIALS_DICT, MAX_PRESENTATIONS_DICT


class VickreyStateMachine:
    def __init__(self, screenmanager, num_robobidders=NUM_ROBOBIDDERS):
        self.sm = screenmanager

        # backupflag
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
        self.next_screen_dict = {"dummy": "pushtostartscreen", 
                                 "pushtostartscreen": "numpad", 
                                 "numpad": "survey",
                                 "survey": "resultscreen"
                                 }

    def loadstate(self, states_dict: dict):
        """
        Load state into internal variables
        """
        self.auction_tally = int((states_dict["t"])/ 2) + 1
        self.state = states_dict["state"]
        self.prev_state = states_dict["prev_state"]
        self.total_winnings = states_dict["total_winnings"]
        self.robomodel.loadstate(states_dict["robostates"])

        self.backupflag = True

    def determine_auction(self):
        """
        Determine Vickrey auction outcome
        """
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
            self.robomodel.robobidderlist[winning_bid_idx - 1].walk(robo_walk_time, 0)

        # Update auction states
        self.prev_state = self.state
        self.state = state

        # Auction logging values
        t = self.auction_tally * ROBOWALK_DUR

        # Send auction results to auctionhouse
        self.sm.exoboot_remote.call(t, subject_bid, self.state, self.payout, self.total_winnings)

        # Save backup
        auction_backup = [t, subject_bid, self.state, self.payout, self.total_winnings]
        auction_backup.extend(self.robomodel.getstate())
        self.sm.filingcabinet.writerow("auction", auction_backup)

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
        for btn_num in BTN_NUMS:
            # Setting up Torque options
            num_torques = btn_num * MAX_PRESENTATIONS_DICT[btn_num]
            torques = list(np.linspace(TORQUE_MIN, TORQUE_MAX, num_torques))

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

    def loadstate(self, btpcompleted):
        """
        Remove completed btp from vas_btn_trial_pres list
        """
        for btp in btpcompleted:
            try:
                self.vas_btn_trial_pres.remove(btp)
            except:
                pass

    def getstate(self):
        """
        Return btp
        """
        return self.current_btn_option, self.current_trial, self.current_presentation

    def get_torque(self, ind):
        """
        Return torque (Nm) for a given btp
        """
        return self.button_mappings[self.current_btn_option][self.current_trial][self.current_presentation][ind]

    def peak_btp(self):
        """
        Look at next btp no pop
        """
        [b, t, p] = self.vas_btn_trial_pres[0]
        return b, t, p

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
        resultsbackup = [self.current_btn_option, self.current_trial, self.current_presentation]
        for t, mv in zip(torques, values):
            resultsbackup.append(t)
            resultsbackup.append(mv)
        self.sm.filingcabinet.writerow("vasresults", resultsbackup)

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
        self.walk = 0
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
            case _:
                raise Exception("INVALID JND COND")

    def loadstate(self, walk, pres):
        """
        Start from previous rep, pres
        """
        self.walk = walk + 1 # Start a new walk
        self.pres = pres

    def incrementwalk(self):
        """
        Increment and return walk for logging
        """
        self.walk += 1
        return self.walk

    def next_comparison_split(self):
        """
        Assigns torque pair to randomly selected sides
        """
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
        """
        Assigns torque pair to randomly selected swap button state
        """
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
        """
        Reports result of comparison
        """
        self.sm.exoboot_remote.comparison_result(self.walk, self.pres, self.prop, self.T_ref, self.T_comp, self.truth, signature)

        # Save backup
        comparisonbackup = [self.walk, self.pres, self.prop, self.T_ref, self.T_comp, self.truth, signature]
        self.sm.filingcabinet.writerow("comparison", comparisonbackup)

        if not self.subtrial_limit:
            self.next_comparison()
        else:
            self.next_screen()

    def report_higher_same(self):
        """
        Reports result of comparison
        """
        self.sm.exoboot_remote.comparison_result(self.walk, self.pres, self.prop, self.T_ref, self.T_comp, self.truth, self.peak_torque_ind)

        # Save backup
        comparisonbackup = [self.walk, self.pres, self.prop, self.T_ref, self.T_comp, self.truth, self.peak_torque_ind]
        self.sm.filingcabinet.writerow("comparison", comparisonbackup)

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
    def __init__(self, screenmanager, pref_type='BUTTON'):
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
            case 'BUTTON':
                self.next_screen_dict["pushtostartscreenpref"] = "btnscreen"
                self.next_screen_dict["btnscreen"] = "waitingscreenpref"

    def report_pref(self, torque):
        """
        Sends preferred torque to pi
        """
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
    testvas.generate_button_torque_mapping()

    print("B T P Torques")
    for btn, trials in testvas.button_mappings.items():
        trial_torques = []
        for t, trial in trials.items():
            for p, pres in trial.items():
                print(btn, t, p, pres)
            print()
