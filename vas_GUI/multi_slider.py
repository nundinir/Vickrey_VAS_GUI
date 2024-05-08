from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line, Color
from kivy.core.window import Window

# Define a new Widget class, MultiSlider
class MultiSlider(Widget):
    def __init__(self, **kwargs):
        super(MultiSlider, self).__init__(**kwargs)
        # Initialize slider positions
        self.slider_positions = [0.25, 0.5, 0.75]
        # Bind size and position changes to redraw method
        self.bind(size=self.redraw, pos=self.redraw)

    # Method to redraw the sliders
    def redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Draw the line for the slider
            Color(1, 1, 1)
            Line(points=[self.x, self.y, self.right, self.y])
            # Draw the sliders at their current positions
            for pos in self.slider_positions:
                Line(circle=[self.x + pos * self.width, self.y, 10])

    # Method to handle touch events
    def on_touch_down(self, touch):
        # Check if touch is within the widget
        if self.collide_point(*touch.pos):
            # Check if touch is near a slider
            for i, pos in enumerate(self.slider_positions):
                if abs(touch.x - (self.x + pos * self.width)) < 10:
                    # If so, capture the touch and associate it with the slider
                    touch.ud['slider'] = i
                    return True
        return super(MultiSlider, self).on_touch_down(touch)

    # Method to handle touch move events
    def on_touch_move(self, touch):
        # Check if this touch is associated with a slider
        if 'slider' in touch.ud:
            # If so, move the slider to the touch position and redraw
            self.slider_positions[touch.ud['slider']] = (touch.x - self.x) / self.width
            self.redraw()
            return True
        return super(MultiSlider, self).on_touch_move(touch)

# Define the main application class
class MyApp(App):
    def build(self):
        # Create a vertical BoxLayout
        layout = BoxLayout(orientation='vertical')
        # Create the MultiSlider
        multi_slider = MultiSlider(size_hint=(1, None), height=50)
        # Create an empty Widget to push the MultiSlider to the top
        empty_widget = Widget()

        # Add the MultiSlider and empty Widget to the layout
        layout.add_widget(multi_slider)
        layout.add_widget(empty_widget)

        # Return the layout as the root widget
        return layout

# Run the application
if __name__ == '__main__':
    MyApp().run()