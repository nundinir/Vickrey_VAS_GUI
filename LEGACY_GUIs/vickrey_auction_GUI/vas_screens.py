# importing widgets from kivy
from kivy.app import App
from kivy.uix.slider import Slider
from kivy.uix.label import Widget
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayoutException
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.properties import NumericProperty

import numpy as np
import time
import csv
from functools import partial
import random

import gui2controller2_pb2
import gui2controller2_pb2_grpc
import config
import grpc

from constants import BTN_ORDER, BTN_NUMS

# Define the GUI class
class GuiVas(BoxLayout):
    """Actual Class for the GUI"""
    
    if config.GUI_btn_setup == 'full':
        torques_per_presentation:int = 12                       # All 12 settings at once
        
        # Initializing the torque mapping button order
        button_order = ['L', 'K', 'J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
        button_slider_values = {}
        for i in button_order:
            button_slider_values[i] = 0
            
    elif config.GUI_btn_setup == '4btn':
        torques_per_presentation:int = 4                        # Number of torque options per presentation
        
        # Initializing the torque mapping button order
        button_order = ['D', 'C', 'B', 'A']
        button_slider_values = {}
        for i in button_order:
            button_slider_values[i] = 0
    
    # set the number of torque options (create equal # of buttons and sliders)
    num_torque_options = NumericProperty(torques_per_presentation)  # Defined as Kivy property 
    npo_mv = NumericProperty(config.NPO_MV)
    epo_mv = NumericProperty(config.EPO_MV)
    
    npo_mv_text = StringProperty(f"${config.NPO_MV}")
    epo_mv_text = StringProperty(f"${config.EPO_MV}")
    
    # npo_mv_text = StringProperty(f"Assistance\nNot Valued:\n${config.NPO_MV}")
    # epo_mv_text = StringProperty(f"Assistance\nValued:\n${config.EPO_MV}")
        
        
    def __init__(self, sm, **kwargs):
        """Initialize the GUI"""
        super(GuiVas, self).__init__(**kwargs)

        # ScreenManager
        self.sm = sm

        self.prev_btn_instance =  None
        self.last_pressed_button = None
        
        # Random colors and counter for confirm button background color changes
        self.rand_colors = ['#34308F','#590f2c']
        self.current_color_index = 0


    def on_slider_value(self,additional_variable,instance_slider: Slider, value: float):
        """Slider value change event method"""
        self.vas_value = value

        # Find the index of the slider that triggered the event
        slider_index = self.ids.slider_layout.children.index(instance_slider.parent)   # A = 0, B = 1, ...

        # Print the VAS value and the index of the slider
        # print(f"VAS value: {self.vas_value}, Slider: {chr(65+slider_index)}")

        # Update the text and position of the corresponding label
        label_index = self.num_torque_options - self.ids.slider_layout.children.index(instance_slider.parent) - 1   # label index is the opposite of the slider index
        self.labels[label_index].text = f"${round(value, 2)}"
        self.labels[label_index].center_x = instance_slider.value_pos[0]  # Set the x position of the label to the x position of the slider
        self.labels[label_index].y = instance_slider.value_pos[1] + instance_slider.height / 2  # Set the y position of the label to the y position of the slider
        
        # Set the opacity of the label to 1
        self.labels[label_index].opacity = 1

        config.bool_slider_value_changed = True
        self.button_slider_values[chr(65+slider_index)] = self.vas_value # Update the dictionary with the new slider value
        print("self.button_slider_values: ", self.button_slider_values)

        # Log the data
        self.serverlogger(slider_index=slider_index)


    def press(self, instance_btn: Button):
        """Button press response method"""
        print(f"You pressed the button: {instance_btn.text}")
        
        # on button press, disable the other buttons and then reenable them after 3 sec
        for child in self.ids.button_layout.children:
            if child != instance_btn:
                child.disabled = True
        Clock.schedule_once(self.reenable_widgets, 5)

        # TODO add sm to press args and all calls
        sm.exoboot_remote.set_torques(peak_torque_left=instance_btn.val, peak_torque_right=instance_btn.val)
        
    def reenable_widgets(self, *args):
        """Reenables button presses after 3 seconds/3 strides"""
        for child in self.ids.button_layout.children:
            child.disabled = False
                 
                 
    def confirm_button_pressed(self):
        """Confirm button press response method which re-ranks the buttons 
        based on their corresponding slider values in descending order"""

        config.bool_confirm_button_pressed = True
        print(config.bool_confirm_button_pressed)
        self.serverlogger()
        
        # sort the buttons based on the slider values
        self.button_order = sorted(self.button_order, key=lambda button: self.button_slider_values.get(button, config.NPO_MV), reverse=True)

        # Clear the old button layout
        self.ids.button_layout.clear_widgets()
        self.create_buttons()
        self.create_sliders()
        
        # Change the button color to enable the user to see the change/button press
        confirm_button = self.ids.confirm_button
        confirm_button.bind(on_release=partial(self.change_button_color, confirm_button))
        self.current_color_index += 1


    def change_button_color(self, button, *args):
        """Changes a button's background color to a set of repeating colors"""
        
        # Increment the index and wrap around if it exceeds the length of the rand_colors list
        current_color_index = self.current_color_index % len(self.rand_colors)
        
        # Set the background color to the current color in the rand_colors list
        button.background_color = self.rand_colors[current_color_index]
        button.background_normal = ''
        
        
    def create_buttons(self, sm):
        """Create variable number of buttons"""
        button_colors = ['#0d9c35','#00954b','#92dc7e','#64c987','#39b48e','#089f8f','#00898a','#08737f','#215d6e','#2a4858','#219ebc','#FFB703']
        button_colors = button_colors[:self.num_torque_options]  # limit the number of buttons to the number of torque options
        self.ids.button_layout.rows =  self.num_torque_options   # set the number of columns in the grid layout
        
        btns = BTN_ORDER[sm.statemachine.current_btn_ind]
        for count, letter in enumerate(btns):
            # Create the button
            button = Button(text=f"{letter}") # unicode point for 'A' is 65

            # TODO link to statemachine btn_num/trial/pres
            max_btns = BTN_NUMS[sm.statemachine.current_btn_ind]
            button.val = sm.statemachine.get_torque(max_btns - count - 1)

            self.last_pressed_button= letter
            button.bind(on_press=self.press)
            button.background_color = button_colors[count-1]
            button.font_size = 64
            button.background_normal = ''
            self.ids.button_layout.add_widget(button)


    def create_sliders(self):
        """Create variable number of sliders (called only once at the beginning)"""
        
        slider_colors = ['#0d9c35','#00954b','#92dc7e','#64c987','#39b48e','#089f8f','#00898a','#08737f','#215d6e','#2a4858','#219ebc','#FFB703']
        slider_colors = slider_colors[:self.num_torque_options]  # limit the number of buttons to the number of torque options
        self.ids.slider_layout.rows = self.num_torque_options
        self.labels = []

        self.ids.slider_layout.clear_widgets()
        for count,i in enumerate(self.button_order):
            #for i in range(self.num_torque_options):
            # Create a BoxLayout for each slider
            box_layout = BoxLayout(orientation='horizontal')

            # Create the slider
            slider = Slider(min=config.NPO_MV, max=config.EPO_MV, value=self.button_slider_values[i], cursor_size=(65, 65), cursor_image="pin_1.png")
            self.last_pressed_button = i
            additional_variable = i
            slider.bind(value=partial(self.on_slider_value, additional_variable))

            # Create the cursor label and initially set the opacity to 0
            cursor_label = Label(text=f"${round(slider.value, 2)}", size_hint=(None, None), color=slider_colors[count-1],opacity=1)
            self.labels.append(cursor_label)

            # Add the labels and the slider to the BoxLayout
            box_layout.add_widget(slider)
            box_layout.add_widget(cursor_label)
            
            # Add the BoxLayout to the slider_layout
            self.ids.slider_layout.add_widget(box_layout)


class VAS_GUIApp(App):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm

    def build(self):
        Builder.load_file("vasscreen.kv")
        return GuiVas(self.sm)
