# importing widgets from kivy
from kivy.app import App
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

# importing packages to enable real-time plotting
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.graph import Graph, LinePlot
import time
from math import sin

# importing packages to enable communication with the Rpi
import grpc
import Message_pb2
import Message_pb2_grpc
import numpy as np

# importing the revenue tracker class
from revenue_tracker import RevenueTracker

class MyLayout(FloatLayout):
    """Actual Class for the GUI"""

    def __init__(self, **kwargs):
        """Initialize the GUI and the plotter"""
        super(MyLayout, self).__init__(**kwargs)

        # initialize the earning rate, percent decrease and preferred speed variables
        self.earnings = 0 # $
        self.percent_decrease = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55]    # percent_exo_fee
        self.action_torque_profile = np.linspace(7.8,22,10)
        self.btn_designation_for_csv_logging = ''

        # initialize variables for the revenue tracker
        self.earning_rate = 1 # $/m
        self.pref_speed = 1 # m/s

        # initialize the revenue tracker
        self.rt = RevenueTracker(self.earning_rate, self.earning_rate, self.pref_speed)

        ## Ask user for name of csv file and start the logger
        print("Filename to save as (format:Data_Subject_WNE/Pref/EPO).csv => ") 
        self.filename = input()
        self.headers = ['Time(mins)', 'Distance', 'Button selected?', 'Total Earnings'] # add 'Torque Commanded', # 'Torque Experienced', 
        self.rt.start_logger(self.filename, self.headers)

        # initialize a plot
        self.plot = LinePlot(color=[119/255, 216/255, 153/255, 1], line_width=4)

        # initialize a graph
        self.graph = Graph(
            xlabel="Distance (m)",
            ylabel="Earnings ($)",
            x_ticks_major=1, 
            y_ticks_major=1,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=-0,
            xmax=100,
            ymin=-1,
            ymax=100,
        )

        # link the two together
        self.graph.add_plot(self.plot)

        # initialize a label widget for displaying the earnings
        self.title_label = Label(text=str(0) + "$", size_hint=(0.1, 0.1), pos_hint={'x': 1, 'y': 0.5})

        print("Starting plotter")
        plotter = self.ids.plotter
        plotter.add_widget(self.title_label)
        plotter.add_widget(self.graph)

        # initialize data atribute
        self.my_points = [(0, 0)]

        self.counter = 0
        Clock.schedule_interval(self.update_points, 1.)
        Clock.schedule_interval(self.update_xaxis, 1.)
        Clock.schedule_interval(self.update_yaxis, 1.)

    def update_points(self,*args):
        """Update points on the graph"""
        self.counter = self.counter + 1
        self.plot.points = self.my_points
        self.earnings = self.rt.get_revenue(self.rt.current_fee())
        self.distance = self.counter * self.pref_speed
        self.my_points.append((self.distance,self.earnings))

        # update the widget for displaying the earnings
        self.update_title_label(f"{self.earnings:0.2f}$")

        # save the logs to a csv file
        self.rt.save_logs(self.counter, self.distance, self.btn_designation_for_csv_logging, self.earnings)
        
    def update_xaxis(self,*args):
        """Update the x-axis of the graph"""

        # Step 1: Keep track of the last 5 points
        if not hasattr(self, 'last_five_points'):
            self.last_five_points = []      # create the attribute if it doesn't exist
        self.last_five_points.append(self.my_points[-1])
        if len(self.last_five_points) > 5:
            self.last_five_points.pop(0)    # remove the first element so min is constantly updated

        # Step 2: Set xmin and xmax based on the last 5 points
        if len(self.last_five_points) > 0:
            self.graph.xmin = self.last_five_points[0][0]
            self.graph.xmax = self.last_five_points[-1][0] + 5

    def update_yaxis(self,*args):
        """Update the y-axis of the graph"""
        self.graph.ymin = 0
        self.graph.ymax = int(np.max(self.my_points, axis=0)[1] + 5)

    def update_title_label(self, new_text):
        self.title_label.text = new_text

    def press(self, button_select: str, *args):
        """Button press response method"""
        print(f"The button {button_select} is being pressed")
               
        for button_id, button in self.ids.items():
            button.disabled = True

        # Schedule all buttons to be enabled after 2 seconds
        Clock.schedule_once(lambda dt: self.enable_all_buttons(), 2)

        if(button_select == 'A'):
            self.btn_designation_for_csv_logging = button_select
            
            # redefining the earnings rate and the log_percent_fee based on exo assistance level
            self.rt.step(self.percent_decrease[0])
            
            print("Earning rate decreased by " + str(100*self.rt.current_fee()) + "%")
            # self.update_points()

            # messaging the server (RPI) with the torque magnitude corresponding to the button_select designation
            # with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
            #     try:
            #         stub = Message_pb2_grpc.ActionStateStub(channel)
            #         stub.ActionMessage(
            #             Message_pb2.SendingAction(self.action_torque_profile[0]))
            #     except grpc.RpcError as e:
            #         print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")

        elif(button_select == 'B'):
            self.btn_designation_for_csv_logging = button_select
            
            # redefining the earnings rate and the log_percent_fee based on exo assistance level
            self.rt.step(self.percent_decrease[1])
            
            print("Earning rate decreased by " + str(100*self.rt.current_fee()) + "%")
            
            # with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
            #     try:
            #         stub = Message_pb2_grpc.ActionStateStub(channel)
            #         stub.ActionMessage(
            #             Message_pb2.SendingAction(self.action_torque_profile[1]))
            #     except grpc.RpcError as e:
            #         print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")

        elif(button_select == 'C'):
            self.btn_designation_for_csv_logging = button_select
            
            # redefining the earnings rate and the log_percent_fee based on exo assistance level
            self.rt.step(self.percent_decrease[2])
            
            print("Earning rate decreased by " + str(100*self.rt.current_fee()) + "%")
            
            # with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
            #     try:
            #         stub = Message_pb2_grpc.ActionStateStub(channel)
            #         stub.ActionMessage(
            #             Message_pb2.SendingAction(self.action_torque_profile[2]))
            #     except grpc.RpcError as e:
            #         print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")

        elif(button_select == 'D'):
            self.earning_rate = self.earning_rate - self.earning_rate*self.percent_decrease[3]
            print("Earning rate decreased by 25%")
            self.update_points()
            
            with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
                try:
                    stub = Message_pb2_grpc.ActionStateStub(channel)
                    stub.ActionMessage(
                        Message_pb2.SendingAction(self.action_torque_profile[3]))
                except grpc.RpcError as e:
                    print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")
        
        elif(button_select == 'E'):
            self.earning_rate = self.earning_rate - self.earning_rate*self.percent_decrease[4]
            print("Earning rate decreased by 30%")
            self.update_points()
            
            with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
                try:
                    stub = Message_pb2_grpc.ActionStateStub(channel)
                    stub.ActionMessage(
                        Message_pb2.SendingAction(self.action_torque_profile[4]))
                except grpc.RpcError as e:
                    print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")
        
        elif(button_select == 'F'):
            self.earning_rate = self.earning_rate - self.earning_rate*self.percent_decrease[5]
            print("Earning rate decreased by 35%")
            self.update_points()
            
            with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
                try:
                    stub = Message_pb2_grpc.ActionStateStub(channel)
                    stub.ActionMessage(
                        Message_pb2.SendingAction(self.action_torque_profile[5]))
                except grpc.RpcError as e:
                    print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")
        
        elif(button_select == 'G'):
            self.earning_rate = self.earning_rate - self.earning_rate*self.percent_decrease[6]
            print("Earning rate decreased by 40%")
            self.update_points()
            
            with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
                try:
                    stub = Message_pb2_grpc.ActionStateStub(channel)
                    stub.ActionMessage(
                        Message_pb2.SendingAction(self.action_torque_profile[6]))
                except grpc.RpcError as e:
                    print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")

        elif(button_select == 'H'):
            self.earning_rate = self.earning_rate - self.earning_rate*self.percent_decrease[7]
            print("Earning rate decreased by 45%")
            self.update_points()
            
            with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
                try:
                    stub = Message_pb2_grpc.ActionStateStub(channel)
                    stub.ActionMessage(
                        Message_pb2.SendingAction(self.action_torque_profile[7]))
                except grpc.RpcError as e:
                    print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")
        
        elif(button_select == 'I'):
            self.earning_rate = self.earning_rate - self.earning_rate*self.percent_decrease[8]
            print("Earning rate decreased by 50%")
            self.update_points()
            
            with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
                try:
                    stub = Message_pb2_grpc.ActionStateStub(channel)
                    stub.ActionMessage(
                        Message_pb2.SendingAction(self.action_torque_profile[8]))
                except grpc.RpcError as e:
                    print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")
        
        elif(button_select == 'J'):
            self.btn_designation_for_csv_logging = button_select
            
            # redefining the earnings rate and the log_percent_fee based on exo assistance level
            self.rt.step(self.percent_decrease[9])
            
            print("Earning rate decreased by " + str(100*self.rt.current_fee()) + "%")
            
            # with grpc.insecure_channel("10.0.0.200", options=(('grpc.enable_http_proxy',0), )) as channel:
            #     try:
            #         stub = Message_pb2_grpc.ActionStateStub(channel)
            #         stub.ActionMessage(
            #             Message_pb2.SendingAction(self.action_torque_profile[9]))
            #     except grpc.RpcError as e:
            #         print("ERROR!!!!: ", e, "Check if the Rpi IP is correct or if the ControllerCommunication server is running")

    def enable_all_buttons(self):
        """Enable all buttons and reset button designation to empty"""
        for button_id, button in self.ids.items():
            button.disabled = False
        self.btn_designation_for_csv_logging = ''   

class VAfee_GUIApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        Builder.load_file("VAfee_GUI.kv")
        return MyLayout()


if __name__ == "__main__":
    vagui = VAfee_GUIApp()
    vagui.run()
