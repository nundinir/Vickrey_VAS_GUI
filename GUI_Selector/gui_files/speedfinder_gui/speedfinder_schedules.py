from functools import partial

from kivy.clock import Clock

from constants import BERTEC_SPEED_STOP, BERTEC_ACC_LEFT, BERTEC_ACC_RIGHT, F_TARGET, V_INITIAL, SLEEPTIME

def runoptimizer(sm, dt):
    sm.statemachine.runoptimizer(f_target=F_TARGET, v_init=V_INITIAL, sleeptime=SLEEPTIME)

def speedfinderschedule(sm):
    Clock.schedule_once(partial(runoptimizer, sm), 0)


def pause_exo_bertec(sm, dt):
    sm.bertec.write_command(BERTEC_SPEED_STOP, BERTEC_SPEED_STOP, incline=None, accR=BERTEC_ACC_RIGHT, accL=BERTEC_ACC_LEFT)
    
    # 0 Torque/Pause exoboots
    sm.exoboot_remote.set_torques(peak_torque_left=0, peak_torque_right=0)
    sm.exoboot_remote.set_pause(mybool=True)

def finishscreensfschedule(sm):
    Clock.schedule_once(partial(pause_exo_bertec, sm), 0)
