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
    # Reset numpad bid variables on enter
    sm.previous_bid = sm.bid
    sm.bid = ''
    sm.bid_input.text = decimal_format(sm.bid)

    if sm.statemachine.auction_tally == 0:
        close_time = INITIAL_BIDDING_CLOSE
    else:
        close_time = BIDDING_CLOSE

    Clock.schedule_once(partial(cdt_start_event,sm, close_time-BIDDING_OPEN), BIDDING_OPEN)
    Clock.schedule_once(partial(bidding_close_event,sm), close_time)


def update_resultscreen(sm, dt):
    state = sm.statemachine.state
    prev_state = sm.statemachine.prev_state

    resultscreen = sm.resultscreen
    if state and prev_state:
        resultscreen.label.text="You have won! Continue Walking.\nWinning Bid: ${:.2f}.\nPayout: ${:.2f}".format(sm.statemachine.winning_bid, sm.statemachine.payout)
        resultscreen.label.color =(0, 1, 0, 1)
    elif state and not prev_state:
        resultscreen.label.text = "You have won! Step on treadmill to begin walking.\nWinning Bid: {:.2f}.\nPayout: {:.2f}".format(sm.statemachine.winning_bid, sm.statemachine.payout)
        resultscreen.label.color =(0, 1, 0, 1)
    elif not state and prev_state:
        resultscreen.label.text = "You have lost. Step off treadmill to sit out the round.\nWinning Bid: {:.2f}.\nPayout: {:.2f}".format(sm.statemachine.winning_bid, sm.statemachine.payout)
        resultscreen.label.color =(1, 0, 0, 1)
    elif not state and not prev_state:
        resultscreen.label.text = "You have lost. Continue Sitting. Winning Bid:\n{:.2f}\nPayout: {:.2f}".format(sm.statemachine.winning_bid, sm.statemachine.payout)
        resultscreen.label.color =(1, 0, 0, 1)

    # Reset startbtntext after backup load
    sm.startbtn.text = "Return to treadmill\n Touch to begin"
    

def survey_schedule(sm):
    Clock.schedule_once(partial(update_resultscreen, sm), 0)
    Clock.schedule_once(sm.statemachine.close_survey, RESULT_SHOW-BIDDING_CLOSE)
    Clock.schedule_once(sm.statemachine.next_screen, RESULT_SHOW-BIDDING_CLOSE)


def result_screens_event(sm, dt):
    state = sm.statemachine.state
    prev_state = sm.statemachine.prev_state
    if not state and prev_state:        
        # Stop Bertec and pause exoboots
        sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
        sm.exoboot_remote.set_pause(mybool=True)

    if state and not prev_state:
        # push to start if getting on treadmill
        sm.current = "pushtostartscreen"
    else:
        # continue sitting/walking/sitting out
        sm.current = "numpad"

def result_screens_schedule(sm):
    Clock.schedule_once(partial(result_screens_event,sm), AUCTION_CLOSE - RESULT_SHOW)
