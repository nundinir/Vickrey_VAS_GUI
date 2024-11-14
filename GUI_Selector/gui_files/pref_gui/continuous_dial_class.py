from math import atan2, pi

from kivy.properties import NumericProperty
from kivy_garden.radialslider import RadialSlider

class PrefDial(RadialSlider):
    """
    Class to handle continuous rotation of Kivy Radial dial
    """
    rotations = NumericProperty(0)  # Track full rotations in either direction
    torque_value = NumericProperty(0)   # current torque selected by the user via the dial position
    min_torque = NumericProperty(0)
    max_torque = NumericProperty(100)  # Define maximum torque value
    full_rotations_required = NumericProperty(10)  # Number of full rotations to reach max torque
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle_per_turn = 360
        self.total_rotation_value = self.full_rotations_required * self.angle_per_turn
        self.virtual_angle = 0  # Continuous rotation angle that doesn't reset
        self.last_touch_angle = None  # Track last touch angle to determine direction

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.last_touch_angle = self.get_touch_angle(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            current_touch_angle = self.get_touch_angle(touch)
            if self.last_touch_angle is not None:
                self.angle_diff = current_touch_angle - self.last_touch_angle

                # Handle wrap-around logic
                if self.angle_diff > 180:
                    self.angle_diff -= 360
                elif self.angle_diff < -180:
                    self.angle_diff += 360

                # Update the virtual angle based on the angle difference
                self.virtual_angle += self.angle_diff

                # Adjust rotations based on virtual angle to keep it in a continuous range
                self.rotations = int(self.virtual_angle / self.angle_per_turn)

                # Update the actual angle to keep thumb position in sync, modulo 360 for visual feedback
                self.angle = self.virtual_angle % 360

                # Update torque based on virtual angle
                self.update_torque_value()

            self.last_touch_angle = current_touch_angle
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.last_touch_angle = None
        return super().on_touch_up(touch)

    def get_touch_angle(self, touch):
        """Calculate the angle between touch position and the center of the widget."""
        x, y = touch.pos
        center_x, center_y = self.center
        return (180 / pi) * -atan2(y - center_y, x - center_x) % 360

    def update_torque_value(self):
        """Calculate torque based on the cumulative virtual angle."""
                
        dial_sensitivity_factor = 0.025
        self.torque_value = self.torque_value + self.angle_diff * dial_sensitivity_factor

        # clamp to min and max torque values
        if self.torque_value < self.min_torque:
            self.torque_value = self.min_torque
        elif self.torque_value > self.max_torque:
            self.torque_value = self.max_torque