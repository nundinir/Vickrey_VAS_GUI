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

import Message_pb2
import Message_pb2_grpc
import config
import grpc

# TODO: Fix the slider mapping to the correct button label (A<->E, E<->A, B<->D...)
# TODO: Add confirm button
# TODO: dynamic change order of button and slider after confirm button is pressed
# TODO: Add column in log file for confirmation button press
# TODO: GRPC server/client for real-time data transfer
# TODO: Separate script of torque and button randomization mapping (use random.seed(0) for reproducibility)
# TODO: Add trial # as user input [argparser: https://docs.python.org/3/library/argparse.html]

# Define the GUI class
class GuiVas(BoxLayout):
    """Actual Class for the GUI"""
    # set the number of torque options (create equal # of buttons and sliders)
    num_torque_options = NumericProperty(5)  # Defined as Kivy property 

    def __init__(self, **kwargs):
        """Initialize the GUI"""
        super(GuiVas, self).__init__(**kwargs)

        # Ask user for name of csv file and start the logger
        print("Filename to save as (format:Subject_VAS_pres#_inclinelvl).csv => ") 
        self.filename = '1'#input()
        self.headers = ['Time(s)', 'Current Torque Experienced', 'Torque Slider Adjusted', 'VAS Value of Torque Slider']
        self.logged_yet = False
        self.start_time = time.time()

    def csvlogger(self, value_of_slider=None, slider_index=None, btn_instance=None):
        """Log the data to a csv file"""

        try:
            with open(self.filename, 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                if self.logged_yet == False: # write headers & time stamp to csv file only once
                    csvwriter.writerow(self.headers)
                    self.logged_yet = True
    
                if slider_index != None:
                    slider_selected = {chr(65+slider_index)}
                else:
                    slider_selected = None
                
                elapsed_time = time.time() - self.start_time
                csvwriter.writerow([elapsed_time, btn_instance, slider_selected, value_of_slider])   

        except IOError:
            print("An error occurred while trying to write to the file.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def on_slider_value(self, instance_slider: Slider, value: float):
        """Slider value change event method"""
        self.vas_value = value
        print("VAS value:", self.vas_value)

        # Find the index of the slider that triggered the event
        index = self.ids.slider_layout.children.index(instance_slider.parent)

        # Print the VAS value and the index of the slider
        print(f"VAS value: {self.vas_value}, Slider: {chr(65+index)}")

        # Update the text and position of the corresponding label
        self.labels[index].text = f"${round(value, 2)}"
        self.labels[index].center_x = instance_slider.value_pos[0]  # Set the x position of the label to the x position of the slider
        self.labels[index].y = instance_slider.value_pos[1] + instance_slider.height / 3  # Set the y position of the label to the y position of the slider
        
        # Set the opacity of the label to 1
        self.labels[index].opacity = 1

        # Log the data to a csv file
        self.csvlogger(value, index)

    def press(self, instance_btn: Button):
        """Button press response method"""
        if(instance_btn.text == 'A'):
            torque = 1
        elif(instance_btn.text == 'B'):
            torque = 2
        elif(instance_btn.text == 'C'):
            torque = 3
        elif(instance_btn.text == 'D'):
            torque = 4
        elif(instance_btn.text == 'E'):
            torque = 5
    
        with grpc.insecure_channel(config.server_ip) as channel:
            stub = Message_pb2_grpc.GUIStub(channel)
            response = stub.UserButton(Message_pb2.Input(torque=torque))

        print(f"You pressed the button: {instance_btn.text}")
        
        # Log the new torque option to a csv file
        self.csvlogger(instance_btn.text)

        # TODO: insert the logic for the torque-button mapping here (also include trial #)


    def create_buttons(self):
        """Create variable number of buttons"""
        button_colors = ['#0d9c35','#00954b','#92dc7e','#64c987','#39b48e','#089f8f','#00898a','#08737f','#215d6e','#2a4858']
        button_colors = button_colors[:self.num_torque_options]  # limit the number of buttons to the number of torque options
        self.ids.button_layout.rows =  self.num_torque_options   # set the number of columns in the grid layout

        for i in range( self.num_torque_options):
            button = Button(text=f"{chr(65+i)}") # unicode point for 'A' is 65
            button.bind(on_press=self.press)
            button.background_color = button_colors[i]
            button.font_size = 64
            button.background_normal = ''
            self.ids.button_layout.add_widget(button)

    def create_sliders(self):
        """Create variable number of sliders (called only once at the beginning)"""
        print("Create sliders is called")
        slider_colors = ['#0d9c35','#00954b','#92dc7e','#64c987','#39b48e','#089f8f','#00898a','#08737f','#215d6e','#2a4858']
        slider_colors = slider_colors[:self.num_torque_options]  # limit the number of buttons to the number of torque options
        self.ids.slider_layout.rows = self.num_torque_options
        self.labels = []

        for i in range(self.num_torque_options):
            # Create a BoxLayout for each slider
            box_layout = BoxLayout(orientation='horizontal')

            # Create the slider
            slider = Slider(min=-15, max=50, value=0, cursor_size=(25, 25), cursor_image="pin_1.png")
            slider.bind(value=self.on_slider_value)

            # Create the cursor label and initially set the opacity to 0
            cursor_label = Label(text=f"${round(slider.value, 2)}", size_hint=(None, None), color=slider_colors[i],opacity=0)
            self.labels.append(cursor_label)

            # Add the labels and the slider to the BoxLayout
            box_layout.add_widget(slider)
            box_layout.add_widget(cursor_label)
            
            # Add the BoxLayout to the slider_layout
            self.ids.slider_layout.add_widget(box_layout)


class VAS_GUIApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        Builder.load_file("GUI_VAS.kv")
        return GuiVas()


if __name__ == "__main__":
    vagui = VAS_GUIApp()
    vagui.run()
