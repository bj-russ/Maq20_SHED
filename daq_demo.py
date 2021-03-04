import time
import random
#import json


#-----Initialize daq and assign modules to physical variables----- Could be automated to scan daq and return the module types, then name accordingly.
class dataforth():

    def __init__(self, settings):
        self.settings = settings
        self.channel_map_inputs = self.settings['channel_map_inputs']
        self.channel_map_outputs = self.settings['channel_map_outputs']
        self.channel_configs = self.settings['channel_configs']
        #self.daq = MAQ20(ip_address=self.settings['host'], port=self.settings['port'])
        self.module_names = ['mod1_AI_MVDN', 'mod2_AI_TTC', 'mod3_AO_VO', 'mod4_DI_DIV20', 'mod5_DIO_DIOL', 'mod6_DIO_DIOL', 'mod7_DIO_DIOL', 'mod8_DIO_DIOL']
        self.mod1_AI_MVDN = [-2.988048, -2.988048, -2.988048, -2.988048, -2.988048, -2.988048, -2.988048, -2.988048] 
        self.mod2_AI_TTC = [50, 5, 50, 5, 50, 5, 5, 50]
        self.mod3_AO_VO = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.mod4_DI_DIV20 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.mod5_DIO_DIOL = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        self.mod6_DIO_DIOL = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.mod7_DIO_DIOL = [0, 1, 1234, 1, 1, 1, 1, 1, 1, 1]
        self.mod8_DIO_DIOL = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.module_instances = [self.mod1_AI_MVDN, self.mod2_AI_TTC]#, self.mod3_AO_VO, self.mod4_DI_DIV20, self.mod5_DIO_DIOL, self.mod6_DIO_DIOL, self.mod7_DIO_DIOL, self.mod8_DIO_DIOL]
        self.modules = dict(zip(self.module_names, self.module_instances))

        #-----Initialize Special Functions on DIOL modules----
        

        #----- Functions for accessing maq20 api  DEMO -----

    def read_modules(self, modules): #accepts dict of module name: module instance and returns dict of module name: list of channel values
        data = modules
        for key in modules:
            if 'VDN' in key:
                for i in range(0, len(modules[key])):
                    data[key][i] = random.uniform(0.4,.5)
            if 'TTC' in key:
                for i in range(0,len(modules[key])):
                    if ( i% 2) == 0: #check if even
                        data[key][i] = random.uniform(45,60)
                    else:
                        data[key][i] = random.uniform(9,15)

            if 'DIO' in key or 'AO' in key:
                pass
            elif 'DI' in key:
                pass
        return data

    def read(self, channel, channel_type): #accepts channel name, returns dict of {channel name: value} and checks for enabled counters.
        pass

    def read_modbus_register(self, channel): #used to read the state of DIO outputs.
        pass

    def read_channels(self, channels): # ignores the list of requested channels and updates all channels with random numbers.
        data = {
            'T_shed3_l': random.uniform(0.4, 0.5),
            'T_shed3_r': random.uniform(0.4, 0.5),
            'T_shed2_l': random.uniform(0.4, 0.5),
            'T_shed2_r': random.uniform(0.4, 0.5),
            'Flowmeter_shed3_hot' : random.uniform(8, 10),
            'Flowmeter_shed3_cold' : random.uniform(7, 8),
            'Flowmeter_shed2_hot' : random.uniform(6, 7),
            'Flowmeter_shed2_cold' : random.uniform(5, 10),
            'Flowmeter_main_hot' : random.uniform(1, 10),
            'Flowmeter_main_cold' : random.uniform(5, 8),
            'Flowmeter_shed1_hot' : random.uniform(5, 9),
            'Flowmeter_shed1_cold' : random.uniform(10, 16),
            'T_shed3_hot' :  random.uniform(10, 65),
            'T_shed3_cold' : random.uniform(10, 65),
            'T_shed2_hot' : random.uniform(10, 65),
            'T_shed2_cold' : random.uniform(10, 65),
            'T_main_hot' : random.uniform(10, 65),
            'T_main_cold' : random.uniform(10, 65),
            'T_shed1_hot' : random.uniform(10, 65),
            'T_shed1_cold' : random.uniform(10, 65)
        }
        
        
        # call scale/calibration function and correct values before returning
        return data

    def write_channels(self, channels):    # accepts a dict of the engineering channels to write to and the desired values. Gets the physical channel from the map and writes to the physical channel.    for key, value in channels, values:
        '''
        for key in channels.keys():
            if key in self.channel_configs.keys(): # check for special function
                if self.channel_configs[key] == "frequency_generator":
                    module = str(self.channel_map_outputs[key])[:-3]
                    if str(self.channel_map_outputs[key])[-2] == '0': #case for timer 0 on input 0
                        timer = 0
                    elif str(self.channel_map_outputs[key])[-2] == '2': #case for time 1 on input 2
                        timer = 1
                    frequency = str(channels[key])
                    exec("self." + module + ".write_special_function_5_frequency_generator(timer=" + str(timer) + ", frequency=" + frequency + ")")
            else: # regular output (boolean + AO) add other function with elif statements
                if key in self.channel_map_outputs.keys():
                    if 'DIO' in str(self.channel_map_outputs[key]):
                        if channels[key] == 'true' or channels[key] == 1:
                            value = 0
                        else:
                            value = 1
                    elif 'AO' in str(self.channel_map_outputs[key]):
                        value = channels[key]
                    channel_to_write = str(self.channel_map_outputs[key])
                    exec("self." + channel_to_write + '=' + str(value))
                else:
                    pass'''
        pass



#-----Function Testing-----
#with open("config.txt", 'w') as outfile:
#    json.dump(settings, outfile)

'''
try:
    daq = dataforth(settings)
    channels_read = []
    for channel in settings['channel_map_inputs'].keys():
        channels_read.append(channel)
    channels_write = {}
    for channel in settings['channel_map_outputs'].keys():
        channels_write[channel] = 1
    while True:
        daq.write_channels(channels_write)
        channel = daq.read_channels(channels_read)
        print(channel)
        time.sleep(1)
except KeyboardInterrupt:
    pass
'''

   