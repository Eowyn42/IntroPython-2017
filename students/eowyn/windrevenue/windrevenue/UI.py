#!/usr/bin/env python
import sys
from windrevenue.parse_met_data import MetData as met
from windrevenue.power_curve_tool import PowerCurve as pct
from windrevenue.electricity_pricing import ElectricityPricing as pricing
from windrevenue.peakhours import PeakHours as peak
from windrevenue.revenue import GrossRevenue as rev
from windrevenue.align_data import AlignData as ad


class UI():

    def __init__(self):
        """
        Instantiate classes to store state related to
        different data and funcionality.
        """
        self.met = met()
        self.pct = pct()
        self.pricing = pricing()
        self.peak = peak()
        self.rev = rev()
        self.ad = ad()

    def quit_code(self):
        sys.exit()

    def return_to_menu(self):
        ''' Return True to trigger exit out of sub-loop'''
        return True

    @staticmethod
    def get_user_input(prompt_string):
        ''' Print a prompt_string, return keyboard input if no exceptions'''
        try:
            answer = input(prompt_string)
        except (EOFError, KeyboardInterrupt, TypeError):
            return None
        else:
            return answer

    def select_action(self, arg_dict, answer):
        ''' Execute an action from arg_dict that corresponds to answer.
        Return None if action was executed and False if an error occurs'''
        try:
            return arg_dict[answer]()
        except (KeyError):
            return False

    def run_interactive_loop(self, arg_dict, prompt_string):
        while True:
            answer = self.get_user_input(prompt_string)
            if answer:
                result = self.select_action(arg_dict, answer)
                if result:
                    return True


    def mainloop(self):
        ''' 
        main interactive loop
        '''
        while True:
            arg_dict = {"1": self.met_loop,
                        "2": self.powercurve_loop,
                        "3": self.pricing_loop,
                        "4": self.peakhours_loop,
                        "5": self.revenue_loop,
                        "6": self.quit_code}
            prompt_string = """Calculate gross revenue from a single turbine: \n
            (1) Choose/Modify Meteorological Time Series\n
            (2) Add/Select Power Curve from Repository\n
            (3) Choose/Modify Electricity Pricing Data \n
            (4) Choose/Modify Peak/Off-Peak Hours\n
            (5) Calculate Peak & Off-Peak Monthly Revenue Table\n
            (6) Quit\n>"""
            self.run_interactive_loop(arg_dict, prompt_string)

    def met_loop(self):
        '''
        Parse meteorological time series files
        '''
        while True:
            arg_dict = {"1": self.met.parse_met_file,
                        "2": self.met.inspect_met_sensor,
                        "3": self.met.change_met_sensor,
                        "4": self.return_to_menu}
            prompt_string = """Select one:\n
            (1) Load meteorological time series file\n
            (2) Inspect current met sensor selected for calculations\n
            (3) Change current met sensor selection for calculations\n
            (4) Return to the main menu\n"""
            if self.run_interactive_loop(arg_dict, prompt_string):
                print("Using Sensor: ", self.met.windVar)
                return

    def powercurve_loop(self):
        '''
        Load power curve data new or from existing
        To Do: Enable power curve repository
        '''
        while True:
            arg_dict = {"1": self.pct.list_existing,
                        "2": self.pct.choose_existing,
                        "3": self.pct.load_new,
                        "4": self.return_to_menu}
            prompt_string = """Select one:\n
            (1) View available power curves\n
            (2) Select from available power curves\n
            (3) Load new power curve from file\n
            (4) Return to the main menu\n"""
            if self.run_interactive_loop(arg_dict, prompt_string):
                return

    def pricing_loop(self):
        '''
        Parse electricity pricing time series files
        '''
        while True:
            arg_dict = {"1": self.pricing.load_new,
                        "2": self.pricing.show_pricing_field,
                        "3": self.pricing.set_pricing_field,
                        "4": self.return_to_menu}
            prompt_string = """Select one:\n
            (1) Load electricity prices time series file\n
            (2) Inspect current substation selected for calculations\n
            (3) Change current substation selection for calculations\n
            (4) Return to the main menu\n"""
            if self.run_interactive_loop(arg_dict, prompt_string):
                return

    def peakhours_loop(self):
        '''
        View and select hours of day (out of 24) that are peak & off-peak
        '''
        while True:
            arg_dict = {"1": self.peak.print_peak_hours,
                        "2": self.peak.set_peak_hours,
                        "3": self.return_to_menu}
            prompt_string = """Select one:\n
            (1) Review current peak/off peak hour selection\n
            (2) Adjust current peak/off peak hour selection\n
            (3) Return to the main menu\n"""
            if self.run_interactive_loop(arg_dict, prompt_string):
                return

    def revenue_loop(self):
        '''
        Calculate 12 month x 2 (peak,off-peak) gross revenue
        Pretty-print tables to screen
        Save tables to files on disk
        '''
        while True:
            arg_dict = {"1": self.get_gross_revenue,
                        "2": self.return_to_menu}
            prompt_string = """Select one:\n
            (1) Calculate gross revenue with current selections
             and save results to file\n
            (2) Return to the main menu\n"""
            if self.run_interactive_loop(arg_dict, prompt_string):
                return

    def get_gross_revenue(self):
        # Wrapper to pass self to revenue model
        df = self.ad.align_data()
        print(df.head())
        #rev.get_gross_revenue(self)
