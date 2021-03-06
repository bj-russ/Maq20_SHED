from simple_pid import PID
from datetime import datetime


class shed():

    def __init__(self, name, settings):
        self.settings = settings
        self.request = False
        self.name = name
        self.state = "off"
        self.configs = settings['state_settings'] # ['on'], ['off'], ['alarm']
        self.set_temp = settings['set_temp']
        self.set_temp_high = self.set_temp + 3
        self.set_temp_low = self.set_temp - 3
        self.pid_state = "off" 
        self.dependent = settings['dependent']  # List of dependent variables required to be alarm free for operation 
        if "PID" in settings:
            self.p = settings["PID"]["p"]
            self.i = settings["PID"]["i"]
            self.d = settings["PID"]["d"]
            self.pid = PID(self.p, self.i, self.d, self.set_temp)
            self.pid_valve_hot = settings["PID"]["valve_control_hot"]
            self.pid_valve_cold = settings["PID"]["valve_control_cold"]
            self.pid_control = settings["PID"]["control"]
            self.pid_state = False
            self.pid.output_limits = (0,10)
        self.timer_start = datetime.now()
        self.timer_elapsed = datetime.now() - self.timer_start
        self.timer_state = 0
        self.timer_output = ""
    def change_request(self, value):
        self.request = value
        # print (self.request)
        self.update_state()


    def update_state(self):
        if self.state != "alarm":
            if self.request == "true":
                self.state = "on"
            if self.request == "false":
                self.state = "off"          
        if self.state == "alarm":
            pass # possibly add in fuction to bring up pop up window to clear alarms?

    def state_monitor(self, active_alarm):
        count = 0
        if self.request == True or self.request == "true":
            # print(self.dependent)
            # print(active_alarm)
            for item in self.dependent:
                if "Gas" not in item:
                    if item in active_alarm:
                        count =+ 1 
                    else:
                        pass 
                else:
                    if item in active_alarm:
                        count =+ 100
                    else:
                        pass
            #print(count)
            if count > 100:
                self.state = "alarm"
            elif count > 0:
                self.state = "out_of_range"
            elif count == 0:
                self.state = "on"
            else:
                self.state ="ERROR!"

        else:
            self.state = "off"
        #print(self.name, "state: ", self.state)
                
                

    def new_state_output(self):
        return self.configs[self.state]

    def change_set_temp(self, temp_set):
        self.set_temp = float(temp_set)
    
    def change_pid(self, newset):
        self.pid_state = newset
        

    def pid_func(self, SHED_temp_current):
        output = {}
        # print(self.pid_state)
        if self.pid_state == True or self.pid_state == "true" or self.pid_state == "True":
            self.pid.setpoint = float(self.set_temp)
            valve_temp = self.pid(float(SHED_temp_current))
            print(valve_temp)
            output[self.pid_valve_hot] = valve_temp 
            print(self.set_temp, SHED_temp_current)
            print(output)
        return output

    def timer(self):
        if self.timer_state == 0:
            self.timer_start = datetime.now()
        self.timer_elapsed = datetime.now() - self.timer_start
        weeks = 0
        if self.timer_elapsed.days >= 7:
            weeks = self.timer_elapsed // 7
        days = self.timer_elapsed.days - 7 * weeks
        hours = self.timer_elapsed.seconds // 3600
        minutes = self.timer_elapsed.seconds // 60 % 60
        seconds = self.timer_elapsed.seconds - minutes*60 - hours*3600 - days * 86400

        self.timer_output = str(weeks) + "W " + str(days) + "d " + str(hours) + "h " +str(minutes) + "m " + str(seconds)
        return self.timer_output
    
    def timer_toggle(self):
        if self.timer_state == 0:
            self.timer_state = 1
            self.timer_start = datetime.now()
        else:
            self.timer_state = 0



class alarm():
    def __init__(self, name, settings):
        self.settings = settings
        self.name = name
        self.state = settings["state"]
        self.type = settings["limit_type"]
        self.limit_high = settings["limits"]["high"]
        self.limit_low = settings["limits"]["low"]
        self.active_config = settings["active_config"]

    def update_state(self, reading, pump_state):
        if "Gas" in self.name:
            if self.state == 0: 
                if self.type == "inside":
                    if float(reading) > float(self.limit_high) or float(reading) < float(self.limit_low):
                        self.state = 1
            elif self.state == 1: 
                pass # Alarm will not automatically reset!
        
        else:
            #print("pump: ", pump_state)
            if pump_state == 0:
                self.state = 2
            else:
                if self.state == 1: ## change this if disabling alarm is required
                    if self.type == "inside":
                        if float(reading) < float(self.limit_high) and float(reading) > float(self.limit_low):
                            self.state = 0
                        else:
                            self.state = 1
                else: 
                    if self.type == "inside":
                        if float(reading) < float(self.limit_high) and float(reading) > float(self.limit_low):
                            self.state = 0
                        else:
                            self.state = 1
           
            

            #print("state: ",self.state)
    def reset(self):
        self.state = 0

    def alarm_output(self):
        return self.active_config

    def change_limit(self, limit, lim_set):
        """
        lim name: name from javascript including "high_" or "low_" as the prefix
        lim_set: set limit value entered in web interface
        """
        if limit == "low" and lim_set.isnumeric():
            self.limit_low = lim_set
            #print("Change alarm great success!")
        if limit == "high" and lim_set.isnumeric():
            self.limit_high = lim_set
    
