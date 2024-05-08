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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.properties import NumericProperty

import numpy as np
import time
import csv

# Define the Custom Overlayed slider class
class CustomSlider(FloatLayout):
    def __init__(self, min_val, max_val, initial_val, color, slider_num, **kwargs):
        """Initialize the Custom Slider"""
        super(CustomSlider, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        # Create the slider
        self.slider = Slider(min=min_val, max=max_val, value=initial_val, cursor_size=(25, 25), cursor_image="pin_1.png")
        self.slider.bind(value = self.slider_callback)

        # Assign the slider id to the slider
        self.slider.id = slider_num

        # Create the cursor label and initially set the opacity to 0
        self.cursor_label = Label(text=f"${round(self.slider.value, 2)}", size_hint=(None, None), color=color, opacity=0)

        # Add the slider and the label to the BoxLayout
        self.add_widget(self.slider)
        self.add_widget(self.cursor_label)

        self.labels = []
        
    def slider_callback(self, instance_slider: Slider, value: float):
        """Slider value change event method"""
        self.vas_value = value
        print("VAS value:", self.vas_value)

        # Find the index of the slider that triggered the event using slider.id
        index = instance_slider.id
        print(index)

        # Find the index of the slider that triggered the event
        #index = self.ids.slider_layout.children.index(instance_slider.parent)

        # Print the VAS value and the index of the slider
        print(f"VAS value: {self.vas_value}, Slider: {index}")

        # Update the text and position of the corresponding label
        self.update_label(instance_slider, value, index)

    def update_label(self, instance_slider: Slider, value: float, index: str):
        """Update the label text and position"""
        # Create a new label if it doesn't exist
        if len(self.labels) <= self.slider.id.count('slider_'):
            self.labels.append(Label(text=f"${round(value, 2)}", size_hint=(None, None), color=instance_slider.color, opacity=0))
            self.add_widget(self.labels[index])

        # Update the text and position of the label
        self.labels[index].text = f"${round(value, 2)}"
        self.labels[index].center_x = instance_slider.value_pos[0]  # Set the x position of the label to the x position of the slider
        self.labels[index].y = instance_slider.value_pos[1] + instance_slider.height / 3  # Set the y position of the label to the y position of the slider
        
        # Set the opacity of the label to 1
        self.labels[index].opacity = 0.5

        # Log the data to a csv file
        self.csvlogger(value, index)

# Define the main GUI class
class GuiVas(FloatLayout):
    """Actual Class for the GUI"""
    # set the number of torque options (create equal # of buttons and sliders)
    num_torque_options = NumericProperty(5)  # Defined as Kivy property
    min_MV = NumericProperty(-15)
    max_MV = NumericProperty(50)
    init_MV = NumericProperty(0)

    def __init__(self, **kwargs):
        """Initialize the GUI"""
        super(GuiVas, self).__init__(**kwargs)

        # Ask user for name of csv file and start the logger
        print("Filename to save as (format:Subject_VAS_pres#_inclinelvl).csv => ") 
        self.filename = input()
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

    def button_callback(self, instance_btn: Button):
        """Button press response method"""
        print(f"You pressed the button: {instance_btn.text}")
        
        # Log the new torque option to a csv file
        self.csvlogger(instance_btn.text)

    def create_buttons(self):
        """Create variable number of buttons"""
        button_colors = ['#0d9c35','#00954b','#92dc7e','#64c987','#39b48e','#089f8f','#00898a','#08737f','#215d6e','#2a4858']
        button_colors = button_colors[:self.num_torque_options]  # limit the number of buttons to the number of torque options
        self.ids.button_layout.cols =  self.num_torque_options   # set the number of columns in the grid layout

        for i in range( self.num_torque_options):
            button = Button(text=f"{chr(65+i)}") # unicode point for 'A' is 65
            button.bind(on_press=self.button_callback)
            button.background_color = button_colors[i]
            button.font_size = 64
            button.background_normal = ''
            self.ids.button_layout.add_widget(button)

    def create_sliders(self):
        """Create variable number of sliders (called only once at the beginning)"""
        print("Create sliders is called")
        slider_colors = ['#0d9c35','#00954b','#92dc7e','#64c987','#39b48e','#089f8f','#00898a','#08737f','#215d6e','#2a4858']
        slider_colors = slider_colors[:self.num_torque_options]  # limit the number of buttons to the number of torque options
        # self.ids.slider_layout.rows = self.num_torque_options

        for i in range(self.num_torque_options):
            # Create the sliders
            # print out the slider id assigned to each slider
            print(f"Slider ID: {chr(65+i)}")
            slider_num = f"slider_{chr(65+i)}"
            custom_slider = CustomSlider(min_val= self.min_MV, max_val= self.max_MV, initial_val= self.init_MV, color=slider_colors[i], slider_num = slider_num)
            self.add_widget(custom_slider)

class VAS_GUIApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        Builder.load_file("GUI_VAS.kv")
        return GuiVas()

if __name__ == "__main__":
    vagui = VAS_GUIApp()
    vagui.run()
