import datetime

from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.properties import NumericProperty

# Timer class
class CountDownTimer(Label):
    dur = NumericProperty(0)
    def start(self, dur, *vargs):
        self.dur = dur
        Animation.cancel_all(self)
        self.anim = Animation(dur=0, duration=self.dur)
        def finish_callback(animation, CDT):
            # CDT.text = "Finished"
            CDT.text = ""
        self.anim.bind(on_complete=finish_callback)
        self.anim.start(self)

    def on_dur(self, instance, value):
        self.text = str(datetime.timedelta(seconds=value))[:-3]
