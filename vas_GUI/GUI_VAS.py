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

# import Message_2_pb2
# import Message_2_pb2_grpc
import gui2pi_messenger_pb2
import gui2pi_messenger_pb2_grpc
import config
import grpc

# Define the GUI class
class GuiVas(BoxLayout):
    """Actual Class for the GUI"""
    # set the number of torque options (create equal # of buttons and sliders)
    num_torque_options = NumericProperty(config.torques_per_presentation)  # Defined as Kivy property 
    
    def __init__(self, **kwargs):
        """Initialize the GUI"""
        super(GuiVas, self).__init__(**kwargs)

        self.start_time = time.time()
        self.prev_btn_instance =  None
        self.prev_slider_selected = None
        self.prev_value_of_slider = None
        self.last_pressed_button = None
        
    def serverlogger(self, slider_index=None, btn_instance=None, curr_torque:float=0.0):
        """Log the data/current torque selection and send to the Server/Rpi file"""

        try:
            # if a slider is being adjusted, find that slider's A,B,C,D index
            if slider_index != None:
                slider_selected = {chr(65+slider_index)}
            else:
                slider_selected = None

            # compute elapsed time
            elapsed_time = round(time.time() - self.start_time, 4)
          
            #  If a slider has not been moved, but only a button has been pressed, log the appropriate button's data
            if slider_selected == None: 
                
                # Send the torque value to the server via gRPC
                if config.grpc_needed:
                    with grpc.insecure_channel(config.server_ip, options=(('grpc.enable_http_proxy',0), )) as channel:
                        try:
                            stub = gui2pi_messenger_pb2_grpc.CommunicationServiceStub(channel)
                            response = stub.GUI_Messenger(gui2pi_messenger_pb2.data_stream(logging_data = [gui2pi_messenger_pb2.Value(time=elapsed_time),
                                                                                    gui2pi_messenger_pb2.Value(current_torque_selected=curr_torque),
                                                                                    gui2pi_messenger_pb2.Value(adjusted_slider_btn=str('nan')),
                                                                                    gui2pi_messenger_pb2.Value(adjusted_slider_value=float('nan')),
                                                                                    gui2pi_messenger_pb2.Value(confirm_btn_pressed=config.bool_confirm_button_pressed)
                                                                                    ]))
                        except grpc.RpcError as e:
                            print("Error",e)
                
                self.prev_btn_instance = btn_instance 
                
            # otherwise, if a slider has been moved, log the appropriate slider's data
            else:
                # Send the torque value to the server via gRPC
                if config.grpc_needed:
                    with grpc.insecure_channel(config.server_ip, options=(('grpc.enable_http_proxy',0), )) as channel:
                        try:
                            stub = gui2pi_messenger_pb2_grpc.CommunicationServiceStub(channel)
                            response = stub.GUI_Messenger(gui2pi_messenger_pb2.data_stream(logging_data = [gui2pi_messenger_pb2.Value(time=elapsed_time),
                                                                                    gui2pi_messenger_pb2.Value(current_torque_selected=curr_torque),
                                                                                    gui2pi_messenger_pb2.Value(adjusted_slider_btn=str(slider_selected)),
                                                                                    gui2pi_messenger_pb2.Value(adjusted_slider_value= float(config.button_slider_values[chr(65+slider_index)]) ),
                                                                                    gui2pi_messenger_pb2.Value(confirm_btn_pressed=config.bool_confirm_button_pressed)
                                                                                    ]))
                        except grpc.RpcError as e:
                            print("Error",e)
                
                self.prev_btn_instance = btn_instance 
                self.prev_slider_selected = slider_selected
                self.prev_value_of_slider = config.button_slider_values[chr(65+slider_index)]
         
            # reset the confirm button press after logging
            config.bool_confirm_button_pressed = False

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def on_slider_value(self,additional_variable,instance_slider: Slider, value: float):
        """Slider value change event method"""
        self.vas_value = value

        # Find the index of the slider that triggered the event
        #index = self.num_torque_options - self.ids.slider_layout.children.index(instance_slider.parent) - 1

        if(additional_variable == 'A'):
            index = 0
        elif(additional_variable == 'B'):
            index = 1
        elif(additional_variable == 'C'):
            index = 2
        elif(additional_variable == 'D'):
            index = 3

        # Print the VAS value and the index of the slider
        #print(f"VAS value: {self.vas_value}, Slider: {chr(65+index)}")

        # Update the text and position of the corresponding label
        self.labels[index].text = f"${round(value, 2)}"
        self.labels[index].center_x = instance_slider.value_pos[0]  # Set the x position of the label to the x position of the slider
        self.labels[index].y = instance_slider.value_pos[1] + instance_slider.height / 3  # Set the y position of the label to the y position of the slider
        
        # Set the opacity of the label to 1
        self.labels[index].opacity = 1

        config.bool_slider_value_changed = True
        config.button_slider_values[chr(65+index)] = self.vas_value # Update the dictionary with the new slider value
        print("config.button_slider_values: ", config.button_slider_values)

        # Log the data
        self.serverlogger(slider_index=index)

    def press(self, instance_btn: Button):
        """Button press response method"""
        print(f"You pressed the button: {instance_btn.text}")
        
        # on button press, disable the other buttons and then reenable them after 3 sec
        for child in self.ids.button_layout.children:
            child.disabled = True
        Clock.schedule_once(self.reenable_widgets, 3)

        # randomized button-torque mapping for each trial (wtihout replacement)
        np.random.seed(config.curr_trial_num)
        pseudo_random_presentation_torques = np.random.choice(config.torque_settings, size = config.num_of_tot_torque_settings, replace=False)

        # select a subset of the pseudo-randomized torques based on current presentation number
        if config.current_presentation_num == 1:
            pseudo_random_presentation_torques = pseudo_random_presentation_torques[:config.torques_per_presentation]
        elif config.current_presentation_num == 2:
            pseudo_random_presentation_torques = pseudo_random_presentation_torques[config.torques_per_presentation:]
            
        # Set the torque value based on the button pressed
        if(instance_btn.text == 'A'):
            torque = pseudo_random_presentation_torques[0]
        elif(instance_btn.text == 'B'):
            torque = pseudo_random_presentation_torques[1]
        elif(instance_btn.text == 'C'):
            torque = pseudo_random_presentation_torques[2]
        elif(instance_btn.text == 'D'):
            torque = pseudo_random_presentation_torques[3]
            
        print(round(torque, 3), "Nm")
        
        # Log the new torque option
        self.serverlogger(btn_instance=instance_btn.text, curr_torque=round(torque, 3))
        
    def reenable_widgets(self, *args):
        """Reenables button presses after 3 seconds/3 strides"""
        for child in self.ids.button_layout.children:
            child.disabled = False
                 
    def confirm_button_pressed(self, instance_btn: Button):
        """Confirm button press response method"""
        button = Button(text=f"{'CONFIRM'}")
        config.bool_confirm_button_pressed = True
        self.serverlogger(instance_btn.text)

        config.button_order = sorted(config.button_order, key=lambda button: config.button_slider_values.get(button, config.NPO_MV), reverse=True)

        # Clear the old button layout
        self.ids.button_layout.clear_widgets()
        self.create_buttons()
        self.create_sliders()

    def create_buttons(self):
        """Create variable number of buttons"""
        button_colors = ['#0d9c35','#00954b','#92dc7e','#64c987','#39b48e','#089f8f','#00898a','#08737f','#215d6e','#2a4858']
        button_colors = button_colors[:self.num_torque_options]  # limit the number of buttons to the number of torque options
        self.ids.button_layout.rows =  self.num_torque_options   # set the number of columns in the grid layout
        for count, i in enumerate(config.button_order):
            # Create the button
            button = Button(text=f"{i}") # unicode point for 'A' is 65
            self.last_pressed_button= i
            button.bind(on_press=self.press)
            button.background_color = button_colors[count-1]
            button.font_size = 64
            button.background_normal = ''
            self.ids.button_layout.add_widget(button)


    def create_sliders(self):
        """Create variable number of sliders (called only once at the beginning)"""
        
        slider_colors = ['#0d9c35','#00954b','#92dc7e','#64c987','#39b48e','#089f8f','#00898a','#08737f','#215d6e','#2a4858']
        slider_colors = slider_colors[:self.num_torque_options]  # limit the number of buttons to the number of torque options
        self.ids.slider_layout.rows = self.num_torque_options
        self.labels = []

        self.ids.slider_layout.clear_widgets()
        for count,i in enumerate(config.button_order):
            #for i in range(self.num_torque_options):
            # Create a BoxLayout for each slider
            box_layout = BoxLayout(orientation='horizontal')

            # Create the slider
            slider = Slider(min=config.NPO_MV, max=config.EPO_MV, value=config.button_slider_values[i], cursor_size=(25, 25), cursor_image="pin_1.png")
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        Builder.load_file("GUI_VAS.kv")
        return GuiVas()


if __name__ == "__main__":
    vagui = VAS_GUIApp()
    vagui.run()
