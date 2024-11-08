from functools import partial

from kivy.clock import Clock

from constants import *

from shared_files.utils import decimal_format


def cdt_start_event(sm, dur, dt):
    sm.cdt.start(dur)

def bidding_close_event(sm, dt):
    sm.statemachine.determine_auction()
    sm.statemachine.next_screen()

def numpad_schedule(sm): 
    """
    Numpad screen duration and event timings
    Collect bids using numpad screen during first half of auction
    """
    # Reset numpad bid variables on enter
    sm.previous_bid = sm.bid
    sm.bid = ''
    sm.bid_input.text = decimal_format(sm.bid)

    # Shorten 0th(initial) bid
    if sm.statemachine.auction_tally == 0:
        close_time = INITIAL_BIDDING_CLOSE
    else:
        close_time = BIDDING_CLOSE

    Clock.schedule_once(partial(cdt_start_event,sm, close_time-BIDDING_OPEN), BIDDING_OPEN)
    Clock.schedule_once(partial(bidding_close_event,sm), close_time)


def update_resultscreen(sm, dt):
    """
    Show results of auction
    4 conditions based on state/prev_state
    """
    state = sm.statemachine.state
    prev_state = sm.statemachine.prev_state

    resultscreen = sm.resultscreen
    if state and prev_state:
        resultscreen.label.text="You have won! Continue Walking.\nPayout: ${:.2f}".format(sm.statemachine.payout)
        resultscreen.label.color =(0, 1, 0, 1)
    elif state and not prev_state:
        resultscreen.label.text = "You have won! Step on treadmill to begin walking.\nPayout: {:.2f}".format(sm.statemachine.payout)
        resultscreen.label.color =(0, 1, 0, 1)
    elif not state and prev_state:
        resultscreen.label.text = "You have lost. Step off treadmill to sit out the round.\n\nPayout: {:.2f}".format(sm.statemachine.payout)
        resultscreen.label.color =(1, 0, 0, 1)
    elif not state and not prev_state:
        resultscreen.label.text = "You have lost. Continue Sitting.\nPayout: {:.2f}".format(sm.statemachine.payout)
        resultscreen.label.color =(1, 0, 0, 1)

    # Reset startbtntext after backup load
    sm.startbtn.text = "Return to treadmill\n Touch to begin"
    

def survey_schedule(sm):
    """
    Survey screen events and timings
    """
    Clock.schedule_once(partial(update_resultscreen, sm), 0)
    Clock.schedule_once(sm.statemachine.close_survey, RESULT_SHOW-BIDDING_CLOSE)
    Clock.schedule_once(sm.statemachine.next_screen, RESULT_SHOW-BIDDING_CLOSE)


def logging_event(sm, dt):
    """
    Start logging/Vicon early before subject is on treadmill
    """
    state = sm.statemachine.state
    prev_state = sm.statemachine.prev_state
    if state and not prev_state: # Get subject ON treadmill
        sm.exoboot_remote.newwalk(sm.statemachine.auction_tally)
        sm.exoboot_remote.set_log(mybool=False)

        auctionname = "{}_t{}".format(sm.file_prefix, 2 * sm.statemachine.auction_tally)
        sm.vicon.start_recording(auctionname)

def result_screens_event(sm, dt):
    """
    Control switching to next screen at the end of the auction
    Stop logging/Vicon if necessary
    """
    state = sm.statemachine.state
    prev_state = sm.statemachine.prev_state
    
    if not state and prev_state: # Get subject OFF treadmill
        sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
        
        # Stop logging and pause exoboots
        sm.exoboot_remote.set_pause(mybool=True)
        sm.exoboot_remote.set_log(mybool=True)

        # Stop Vicon recording
        sm.vicon.stop_recording()

        sm.current = "numpad"

    elif state and not prev_state: # Get subject ON treadmill
        sm.current = "pushtostartscreen"
    else: # Continue walking or sitting
        sm.current = "numpad"

def result_screens_schedule(sm):
    """
    Results screen events and timings
    """
    Clock.schedule_once(partial(logging_event, sm), 0)
    Clock.schedule_once(partial(result_screens_event,sm), AUCTION_CLOSE - RESULT_SHOW)
