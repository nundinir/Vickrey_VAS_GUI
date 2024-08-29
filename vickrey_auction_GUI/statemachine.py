import numpy as np

from constants import *
from Robobidders import *

from constants import BTN_NUMS, MAX_TRIALS_DICT, MAX_PRESENTATIONS_DICT, BTN_ORDER

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
                                 "continuewalkingscreen": "numpad",
                                 "startwalkingscreen": "pushtostartscreen",
                                 "stopwalkingscreen": "numpad",
                                 "continuesittingscreen": "numpad"
                                 }

    def determine_auction(self):
        # Get bid as float
        # no_bid = not self.sm.bid
        # no_prev_bid = not self.sm.previous_bid
        # if not self.sm.bid:
        #     # If no bid, default to previous bid
        #     subject_bid = float(self.sm.previous_bid) * 0.01
        # else:
        #     subject_bid = float(self.sm.bid) * 0.01

        no_bid = not self.sm.bid
        no_prev_bid = not self.sm.previous_bid
        # Convert bid from string to float
        if not no_bid:
            subject_bid = float(self.sm.bid) * 0.01
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

        print("asdf", all_bids)
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
        self.sm.logging_client.call(t, subject_bid, self.state, self.payout, self.total_winnings) #, winning_bid)

        # Increment auction tally
        self.auction_tally += 1

    def close_survey(self):
        t = self.auction_tally * ROBOWALK_DUR
        print("Closing survey", t, self.sm.enjoyment, self.sm.rpe)
        self.sm.logging_client.question(t, self.sm.enjoyment, self.sm.rpe)

    def send_treadmill_msg(self, state):
        self.sm.logging_client.treadmill_state(state)

    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        self.sm.current = self.next_screen_dict[self.sm.current]


class VASStateMachine:
    def __init__(self, screenmanager):
        self.sm = screenmanager

        self.bool_confirm_button_pressed: bool = False
        self.starting_val:int = 0         # Initial value of the slider cursor

        ##################################################
        ###### MODIFY THESE VALUES FOR EACH SUBJECT ######
        ##################################################

        GUI_btn_setup:str = 'full'                              # Full 12 btn setup or 4 btn setup ('full' or '4btn')
        curr_trial_num:int = 1                                  # Current trial number (out of 4 if '4btn' setup and 3 if 'full' setup)
        current_presentation_num:int = 3                        # Only 1 presentation if 'full' setup and 3 presentations if '4btn' setup

        # TODO import from csv
        NPO_MV:float = -18.60        # Value of the slider at the extreme negative end (REMEMBER TO CHANGE IN .KV FILE)
        EPO_MV:float = 3.4           # Value of the slider at the extreme positive end (REMEMBER TO CHANGE IN .KV FILE)


        # Setting up Torque options
        self.min_torque:float = 0.0                                  # Minimum torque value
        self.max_torque:float = 40.0                                 # Maximum torque value
        self.num_of_tot_torque_settings:int = 12                     # Total number of torque settings (Maintain 12 for practicality)
        self.torque_step:float = (self.max_torque - self.min_torque)/self.num_of_tot_torque_settings  # Step size for the torque buttons (maintain 12 btns)
        self.torque_settings = np.arange(self.torque_step, self.max_torque + self.torque_step, self.torque_step)  # All Torque settings (np.arrange doesn't include stop value)
        
        # Trial/Presentation States
        self.current_btn_ind = 0
        self.current_trial = 1
        self.current_presentation = 1

        self.button_mappings = {}

        # Quit flag
        self.quit_flag = True

        # Screen states
        self.next_screen_dict = {"dummy": "pushtostartscreen", 
                                 "pushtostartscreen": "vas",
                                 "vas": "pushtostartscreen"
                                 }

    def generate_button_torque_mapping(self):
        for btn_num in BTN_NUMS:
            trial_mappings = {}
            for trial in range(1, MAX_TRIALS_DICT[btn_num] + 1):
                np.random.seed(trial)

                pseudo_random_presentation_torques = np.random.choice(self.torque_settings, size = self.num_of_tot_torque_settings, replace=False)

                presentation_mappings = {1: pseudo_random_presentation_torques[0:self.torques_per_presentation],
                                         2: pseudo_random_presentation_torques[self.torques_per_presentation:self.torques_per_presentation*2],
                                         3: pseudo_random_presentation_torques[self.torques_per_presentation*2:self.num_of_tot_torque_settings]}

                trial_mappings[trial] = presentation_mappings

            self.button_mappings[btn_num] = trial_mappings

        # torques = self.button_mappings[BTN_NUMS[self.current_btn_ind]][self.current_trial][self.current_presentation]

    def get_torque(self, ind):
        return self.button_mappings[BTN_NUMS[self.current_btn_ind]][self.current_trial][self.current_presentation][ind]

    def next_trial_pres(self):
        current_btn_num = BTN_NUMS[self.current_btn_ind]

        self.current_presentation += 1
        if self.current_presentation > MAX_PRESENTATIONS_DICT[BTN_NUMS[current_btn_num]]:
            self.current_presentation = 1
            self.current_trial += 1
            if self.current_trial > MAX_TRIALS_DICT[BTN_NUMS[current_btn_num]]:
                self.current_btn_num += 1
                if self.current_btn_num >= len(self.btn_nums):
                    # TODO add quitflag
                    self.quit_flag = True
        
        print("BTN_NUM/Trial/Presentation: {}/{}/{}".format(self.current_btn_num, self.current_trial, self.current_presentation))


    def next_screen(self, *vargs):
        # Ignore vargs. exists so next can be called by Clock.schedule_once
        if self.quit_flag:
            self.sm.current = 'finishscreen'
        else:
            self.sm.current = self.next_screen_dict[self.sm.current]