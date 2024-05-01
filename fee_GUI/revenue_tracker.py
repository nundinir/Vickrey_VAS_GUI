import time
import random
import csv

class RevenueTracker:
    def __init__(self, earnings_rate, max_fee, treadmill_speed):
        self.earnings_rate = earnings_rate
        self.max_fee = max_fee
        self.treadmill_speed = treadmill_speed

        self.net_revenue = 0

        self.log_percent_fee: list[float] = []
        self.log_times = []

        self.filename = "None"
        self.headers = [0]

    def start_logger(self, filename, headers):
        """Starts the RevenueTracker and logs the current time and fee"""
        self.log_percent_fee.append(0)
        self.log_times.append(time.time())
        self.filename = filename
        self.headers = headers

    def current_fee(self):
        """Returns the current exo penalty"""
        return self.log_percent_fee[-1]

    def calculate_earnings(self, percent_fee, t0, t1):
        """
        {baseline_earnings - (penalty_percentage * baseline_monetary_fees)} * speed * time_interval
        baseline_earnings: This is decided based on the no exoskeleton condition at user's self selected {We can think about this as normalizing based on user's ability to walk}
        baseline_monetary_fees: This is decided based on user's annual income or based on their analysis on a preceding biding study (Note: Need suggestions from people who know economics to decide this) {We can think about this as normalizing based on user's monetary/spending tendencies}
        """
        return (self.earnings_rate - percent_fee * self.max_fee) * self.treadmill_speed * (t1 - t0)

    def step(self, percent_fee):
        """computes the earnings anytime there is a change in the percent_fee"""
        t1 = time.time()

        #Add previous fee net to net_revenue total
        self.net_revenue += self.calculate_earnings(self.log_percent_fee[-1], self.log_times[-1], t1)
        print(self.net_revenue)

        self.log_percent_fee.append(percent_fee)
        self.log_times.append(t1)
        
    def get_revenue(self, percent_fee):
        """Returns the net revenue at the current time"""
        return self.net_revenue + self.calculate_earnings(percent_fee, self.log_times[-1], time.time())
    
    def project_revenue(self, percent_fee, eta):
        """Returns the projected net revenue at a future time in eta seconds from now"""
        # EtA in seconds
        interval = 0.05
        return self.calculate_earnings(percent_fee, 0, eta + random.uniform(-interval * eta, interval * eta))
        
    def exit(self):
        """Exits the RevenueTracker and removes the last log entry to avoid double counting the last fee change."""
        self.step(100000)
        del self.log_percent_fee[-1]

    # TODO: Add logging for torque_commanded, torque_experienced
    def save_logs(self, time, distance, button_selected, total_earnings):  
        """Saves the logs to a csv file"""
        with open(self.filename, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            if (self.net_revenue == 0): # write headers & time stamp to csv file only once
                csvwriter.writerow(self.headers)
        
            # Filling data: time stamp, distance, button selected?, total earnings
            csvwriter.writerow([time, distance, button_selected, total_earnings])   

# if __name__ == "__main__":
#     """Testing Example"""
#     rt = RevenueTracker(5.00, 5.00, 1.0)

#     print("~~~Example RevenueTracker Usage~~~")
#     print("Step 0\nCurrent Fee = {}".format(rt.current_fee()))
#     print("Net Revenue = {}".format(rt.get_revenue(rt.current_fee())))
#     eta = 1.0
#     print("Projected Revenue for {}s: {}\n".format(eta, rt.project_revenue(rt.current_fee(), eta)))

#     # Step RevenueTracker
#     t1 = 1.0
#     f1 = 0.5
#     time.sleep(t1)
#     rt.step(f1)

#     print("Step 1: Elapsed time = {}s".format(t1))
#     print("Current Fee = {}".format(rt.current_fee()))
#     print("Net Revenue =  {}".format(rt.get_revenue(rt.current_fee())))
#     eta1 = 1.0
#     print("Projected Revenue for {}s: {}\n".format(eta, rt.project_revenue(rt.current_fee(), eta1)))
    
#     # Query RevenueTracker for revenue right now
#     time.sleep(1.0)
#     print("Query RevenueTracker: Elapsed time = {}s".format(1.0))
#     print("Net Revenue = {}\n".format(rt.get_revenue(rt.current_fee())))

#     # Step RevenueTracker
#     t2 = 1.0
#     f2 = 0.9
#     time.sleep(t2)
#     rt.step(f2)

#     print("Step 2: Elapsed time = {}s".format(t2))
#     print("Current Fee = {}".format(rt.current_fee()))
#     print("Net Revenue =  {}".format(rt.get_revenue(rt.current_fee())))
#     eta2 = 1.0
#     print("Projected Revenue for {}s: {}\n".format(eta, rt.project_revenue(rt.current_fee(), eta2)))

#     # Step RevenueTracker
#     t3 = 1.0
#     f3 = 0.2
#     time.sleep(t3)
#     rt.step(f3)
    
#     print("Step 3: Elapsed time = {}s".format(t3))
#     print("Current Fee = {}".format(rt.current_fee()))
#     print("Net Revenue =  {}".format(rt.get_revenue(rt.current_fee())))
#     eta3 = 2.0
#     print("Projected Revenue in {}s: {}\n".format(eta, rt.project_revenue(rt.current_fee(), eta3)))


#     time.sleep(eta3)
#     rt.exit()

#     print("Net Revenue of example trial: {}".format(rt.net_revenue))
#     print("log_percent_fee: {}".format(rt.log_percent_fee))
#     print("log_times: {}".format(rt.log_times))
