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

    Clock.schedule_once(partial(cdt_start_event,sm, (close_time-BIDDING_OPEN)/sm.squeeze), BIDDING_OPEN/sm.squeeze)
    Clock.schedule_once(partial(bidding_close_event,sm), close_time/sm.squeeze)


def update_resultscreen(sm, dt):
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
        resultscreen.label.text = "You have lost. Step off treadmill to sit out the round.\nPayout: {:.2f}".format(sm.statemachine.payout)
        resultscreen.label.color =(1, 0, 0, 1)
    elif not state and not prev_state:
        resultscreen.label.text = "You have lost. Continue Sitting.\nPayout: {:.2f}".format(sm.statemachine.payout)
        resultscreen.label.color =(1, 0, 0, 1)

    # Reset startbtntext after backup load
    sm.startbtn.text = "STOMP then Touch to walk"
    

def survey_schedule(sm):
    Clock.schedule_once(partial(update_resultscreen, sm), 0)
    Clock.schedule_once(sm.statemachine.close_survey, (RESULT_SHOW-BIDDING_CLOSE)/sm.squeeze)
    Clock.schedule_once(sm.statemachine.next_screen, (RESULT_SHOW-BIDDING_CLOSE)/sm.squeeze)


def result_screens_event(sm, dt):
    state = sm.statemachine.state
    prev_state = sm.statemachine.prev_state
    
    if not state and prev_state:        
        # Stop Bertec and pause exoboots
        sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
        sm.exoboot_remote.set_pause(mybool=True)
        sm.exoboot_remote.set_log(mybool=True)

        # Stop Vicon
        sm.vicon.stop_recording()

    if state and not prev_state:
        # Push to start if getting on treadmill
        sm.current = "pushtostartscreen"

        # Start Vicon
        recording_name = "{}_t{}".format(sm.file_prefix, int(sm.statemachine.auction_tally * ROBOWALK_DUR))
        sm.vicon.start_recording(recording_name)

        # Start exo logging
        sm.exoboot_remote.set_log(mybool=False)
    else:
        # continue sitting/walking/sitting out
        sm.current = "numpad"

def result_screens_schedule(sm):
    Clock.schedule_once(partial(result_screens_event,sm), (AUCTION_CLOSE - RESULT_SHOW)/sm.squeeze)
