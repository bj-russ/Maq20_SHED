import maq20.utilities as utils


class MAQ20Module:
    """
    Every Module, including the COM inherits from MAQ20Object.
    This contains every functionality that is shared between all modules.
    """

    no_ranges_error = AttributeError('Converting to Engineering units not available for this module')

    def __init__(self, com=None, registration_number=0):
        """
        Reads general information about the MAQ20 module to registers.
        Registers: [0, 100]
        :param com: a reference to the COM object in the system.
        :param registration_number: this is used to calculate address map automatically.
        """
        self._com = com
        self._registration_number = registration_number
        self._starting_address = registration_number * 2000
        self._name = self.read_name()
        self._inputs = self.read_input_channels()
        self._outputs = self.read_output_channels()
        self._number_of_channels = self._inputs + self._outputs
        if self._number_of_channels < 0:
            self._number_of_channels = 0
        self._serialNumber = self.read_serial_number()
        self._dateCode = self.read_date_code()
        self._firmwareVersion = self.read_firmware_revision()
        self._iter_index = 0

        # This variable stores the number of ranges that have range information available,
        #     A module could still have multiple ranges but no range information was available.
        self._number_of_ranges = None
        self._load_number_of_ranges()
        self._ranges_information = None  # type: list(dict)
        self._channel_active_ranges = None  # type: list
        if self._number_of_ranges is not None and self._number_of_ranges > 0:
            self.load_ranges_information()
            self.load_channel_active_ranges()

    #######################
    # Modbus Communication.
    #######################

    def read_register(self, address):
        """
        Calls the MAQ20-COMx module's read_register().
        Performs a modbus read register request to the MAQ20
        :param address: requested address
        :return: int - [-32767, 32767]
        """
        if 0 <= address < 2000:
            return self._com.read_register(address + self._starting_address)
        else:
            return False

    def read_registers(self, address, number_of_registers):
        """
        Calls the MAQ20-COMx module's read_registers().
        Performs a modbus read registers request to the MAQ20
        :param address: starting address.
        :param number_of_registers: number of registers to be read in sequence.
        :return: list(int) [-32767, 32767]
        """
        if 0 <= address < 2000 and 0 < number_of_registers <= 250 and (address + number_of_registers) < 2000:
            return self._com.read_registers(address + self._starting_address, number_of_registers)
        else:
            return False

    def write_register(self, address, value):
        """
        Calls the MAQ20-COMx module's write_register().
        Performs a modbus write register request to the MAQ20
        :param address: starting address.
        :param value: int [-32767, 32767] or a str of size 1
        :return: modbus response.
        """
        if 0 <= address < 2000:
            return self._com.write_register(address + self._starting_address, value)
        else:
            return False

    def write_registers(self, address, values=None):
        """
        Calls the MAQ20-COMx module's write_registers().
        Performs a modbus write registers request to the MAQ20
        :param address: starting address.
        :param values: list(int) [-32767, 32767] or a str
        :return: modbus response.
        """
        if 0 <= address < 2000:
            return self._com.write_registers(address + self._starting_address, values)
        else:
            return False

    def module_information(self) -> str:
        """
        :return: a str containing information about this module. (Registers [0, 100] and registration number).
        """
        result_str = ""
        result_str += self._name + "\n"
        result_str += "Registration Number: " + str(self._registration_number) + "\n"
        result_str += "Serial Number -----: " + self._serialNumber + "\n"
        result_str += "Date Code ---------: " + self._dateCode + "\n"
        result_str += "Firmware Revision -: " + self._firmwareVersion + "\n"
        result_str += "Input  Channels ---: " + str(self._inputs) + "\n"
        result_str += "Output Channels ---: " + str(self._outputs) + "\n"
        return result_str

    def read_name(self) -> str:
        return utils.response_to_string(self.read_registers(0, 15))

    def read_serial_number(self) -> str:
        return utils.response_to_string(self.read_registers(19, 11))

    def read_date_code(self) -> str:
        return utils.response_to_string(self.read_registers(30, 5))

    def read_firmware_revision(self) -> str:
        return utils.response_to_string(self.read_registers(35, 5))

    def read_input_channels(self) -> int:
        return self.read_register(40)

    def read_output_channels(self) -> int:
        return self.read_register(41)

    def write_module_detect(self):
        return self.write_register(98, 1)

    def write_reset_register(self, input_value):
        return self.write_register(99, input_value)

    ################################
    # Ranges Information [1700,1899]
    ################################

    def has_range_information(self):
        """
        Checks if this module has range information stored.
        Range information is used to convert from counts to engineering units.
        :return: Boolean
        """
        if self._number_of_ranges is None or self._number_of_ranges <= 0:
            return False
        else:
            return True

    def read_range_count(self):
        return self.read_register(1700)

    def read_range(self, a_range=0):
        return self.read_registers(1710 + (a_range * 20), 11) if a_range < self._number_of_ranges else None

    def _load_number_of_ranges(self):
        self._number_of_ranges = self.read_range_count() if self._number_of_channels > 0 else None

    def load_ranges_information(self):
        """
        Loads a module's ranges information into RAM.
        Ranges are stored in a list of dictionaries that has the keys:
        "Engineering-FS"
        "Engineering+FS"
        "EngineeringUnits"
        "CountValue-FS"
        "CountValue+FS"
        """
        # self._load_number_of_ranges()  # Ask module how many ranges it has

        if self._number_of_ranges > 0:
            try:
                self._ranges_information = []
                for range_num in range(self._number_of_ranges):
                    range_info = self.read_range(range_num)  # type: list
                    self._ranges_information.append({
                        "Engineering-FS": range_info[0] * 10 ** range_info[4],
                        "Engineering+FS": range_info[2] * 10 ** range_info[4],
                        "EngineeringUnits": str(chr(range_info[5])) + str(chr(range_info[6])),
                        "CountValue-FS": utils.int16_to_int32(range_info[7:9]),
                        "CountValue+FS": utils.int16_to_int32(range_info[9:11]),
                    })
                    check = self._ranges_information[-1]
                    passed = self._check_range_validity(check)
                    if not passed:
                        if range_num == 1:
                            # May be Old Module
                            """
                            Old modules Contain the range information right next to the previous one instead of
                            skipping to 1710+(i*20), where i is the range number.
                            """
                            del self._ranges_information[-1]
                            for a_range in range(1, self._number_of_ranges):
                                range_info = self.read_registers(1710+(a_range*11), 11)
                                self._ranges_information.append({
                                    "Engineering-FS": range_info[0] * 10 ** range_info[4],
                                    "Engineering+FS": range_info[2] * 10 ** range_info[4],
                                    "EngineeringUnits": str(chr(range_info[5])) + str(chr(range_info[6])),
                                    "CountValue-FS": utils.int16_to_int32(range_info[7:9]),
                                    "CountValue+FS": utils.int16_to_int32(range_info[9:11]),
                                })
                                check = self._ranges_information[-1]
                                passed = self._check_range_validity(check)
                                if not passed:
                                    break
                        if not passed:
                            raise TypeError("Invalid Range Value")
                        break
            except Exception as e:
                pass
        else:
            self._number_of_ranges = None
            self._ranges_information = None  # type: list(dict)
            self._channel_active_ranges = None  # type: list

    @staticmethod
    def _check_range_validity(a_range):
        """
        Called by load_ranges_information(). Checks whether range information read makes sense
        :param a_range: list of range information. This is usually read from registers 1710+ and is length 11
        :return: boolean
        """
        passed = True
        if -10000 > a_range["Engineering-FS"] or a_range["Engineering-FS"] > 10000:
            passed = False
        if -10000 > a_range["Engineering+FS"] or a_range["Engineering+FS"] > 10000:
            passed = False
        if -2147483648 > a_range["CountValue-FS"] or a_range["CountValue-FS"] > 2147483648:
            passed = False
        if -2147483648 > a_range["CountValue+FS"] or a_range["CountValue+FS"] > 2147483648:
            passed = False
        return passed

    def get_engineering_full_scale_positive(self, channel):
        if channel > self._number_of_channels:
            return None
        return self._ranges_information[self._channel_active_ranges[channel]]["Engineering+FS"]

    def get_engineering_full_scale_negative(self, channel):
        if channel > self._number_of_channels:
            return None
        return self._ranges_information[self._channel_active_ranges[channel]]["Engineering-FS"]

    def get_counts_full_scale_positive(self, channel):
        if channel > self._number_of_channels:
            return None
        return self._ranges_information[self._channel_active_ranges[channel]]["CountValue+FS"]

    def get_counts_full_scale_negative(self, channel):
        if channel > self._number_of_channels:
            return None
        return self._ranges_information[self._channel_active_ranges[channel]]["CountValue-FS"]

    def get_engineering_units(self, channel):
        if channel > self._number_of_channels:
            return None
        return self._ranges_information[self._channel_active_ranges[channel]]["EngineeringUnits"]

    def load_channel_active_ranges(self):
        """
        All channel's active range is stored in RAM.
        :return: the list saved.
        """
        if self.get_number_of_channels() > 0:
            self._channel_active_ranges = self.read_registers(100, self.get_number_of_channels())
        else:
            pass
        return self._channel_active_ranges

    def get_channel_active_range(self, channel=0):
        """
        :param channel: channel requested.
        :return: integer of the active channel range.
        """
        return self._channel_active_ranges[channel] if channel < self._number_of_channels else False

    def get_ranges_information(self):
        """
        returns the current ranges information.
        :return: list(dict())
        """
        return self._ranges_information

    def get_channel_ranges_information(self, channel):
        return self._ranges_information[self._channel_active_ranges[channel]]

    def display_ranges_information(self):
        """
        Construct a string in human readable form of range information for all ranges in the module.
        :return: str
        """
        if self._number_of_ranges is None:
            return False
        info_str = ''
        range_num = 0
        for range_info in self._ranges_information:
            info_str += "Range: {}\n".format(range_num)
            range_num += 1
            for key, data in range_info.items():
                info_str += "{} : {}\n".format(key, data)
            info_str += "\n"
        return info_str

    def counts_to_eng_units_list(self, data_list, channel):
        result = []
        for i, data in enumerate(data_list):
            result.append(
                utils.counts_to_engineering_units_dict_input(
                    data,
                    self._ranges_information[self._channel_active_ranges[channel + i]]
                )
            )
        return result

    # TODO: Figure out if there is a common structure to the status registers and implement if there is.

    # Getters

    def get_name(self) -> str:
        return self._name

    def get_registration_number(self):
        return self._registration_number

    def get_inputs(self) -> int:
        return self._inputs

    def get_outputs(self) -> int:
        return self._outputs

    def get_number_of_channels(self) -> int:
        return self._number_of_channels

    def get_serial_number(self) -> str:
        return self._serialNumber

    def get_date_code(self) -> str:
        return self._dateCode

    def get_firmware_version(self) -> str:
        return self._firmwareVersion

    def get_com_module(self):
        return self._com

    ###############
    # Channel Data.
    ###############

    def _read_channel_data_counts_address_input(self, address, channel):
        self._check_channel_inputs(channel)
        return self.read_register(address + channel)

    def _read_data_counts_address_input(self, address, start_channel, number_of_channels):
        self._check_channel_inputs(start_channel, number_of_channels)
        return self.read_registers(address + start_channel, number_of_channels)

    def _read_channel_data_address_input(self, address, channel):
        counts = self._read_channel_data_counts_address_input(address, channel)
        if self.has_range_information():
            return utils.counts_to_engineering_units_dict_input(counts, self.get_channel_ranges_information(channel))
        elif self._name.find('DIO') != -1:  # Check if the module is a digital module.
            return counts  # same as counts.
        else:
            raise AttributeError('This module does not have Range information available. Try reading counts instead.')

    def _read_data_address_input(self, address, start_channel, number_of_channels):
        counts = self._read_data_counts_address_input(address, start_channel, number_of_channels)
        if self.has_range_information():
            return self.counts_to_eng_units_list(counts, start_channel)
        elif self._name.find('DIO') != -1:  # Check if the module is a digital module.
            return counts  # same as counts.
        else:
            raise AttributeError('This module does not have Range information available. Try reading counts instead.')

    def _check_channel_inputs(self, channel, number_of_channels=1):
        if number_of_channels < 0:
            raise AttributeError('Number of channels cannot be negative.')
        if 0 <= channel < self._number_of_channels and channel + number_of_channels <= self._number_of_channels:
            return True
        else:
            raise AttributeError('Outside number of channels range: {}'.format(self._number_of_channels))

    # Counts:

    def read_channel_data_counts(self, channel):
        """
        Reads data from a channel of this module in raw counts.
        :param channel: channel number to read.
        :return: int
        """
        return self._read_channel_data_counts_address_input(1000, channel)

    def write_channel_data_counts(self, channel, data):
        self._check_channel_inputs(channel)
        p_fs_c = self.get_counts_full_scale_positive(channel)
        n_fs_c = self.get_counts_full_scale_negative(channel)
        if n_fs_c <= data <= p_fs_c:
            self.write_register(1000+channel, data)
        else:
            raise AttributeError('Outside available Range values in counts: {} to {}'.format(n_fs_c, p_fs_c))

    def read_data_counts(self, start_channel=0, number_of_channels=1):
        """
        Reads data for the requested channel in COUNTS.
        :param start_channel: channel to start reading from.
        :param number_of_channels: number of channels to be read.
        :return: list(int)
        """
        return self._read_data_counts_address_input(1000, start_channel, number_of_channels)

    def write_data_counts(self, start_channel, data_set):
        self._check_channel_inputs(start_channel, len(data_set))
        for i in range(len(data_set)):
            self.write_data_counts(i+start_channel, data_set[i])

    # Engineering values:

    def read_channel_data(self, channel):
        """
        Reads channel data from the module.
        :param channel: channel to read.
        :return: float 
        """
        return self._read_channel_data_address_input(1000, channel)

    def write_channel_data(self, channel, data):
        """
        Writes data to channel.
        :param channel: int
        :param data: float
        :return: modbus_response
        """
        if self.has_range_information():
            p_fs = self.get_engineering_full_scale_positive(channel)
            n_fs = self.get_engineering_full_scale_negative(channel)
            if n_fs >= data >= p_fs:
                raise AttributeError('Outside available Range values: {} to {}'.format(n_fs, p_fs))
            return self.write_register(1000 + channel,
                                       utils.engineering_units_to_counts_dict_input(data,
                                                                                    self.get_channel_ranges_information(
                                                                                        channel)))
        elif self._name.find('DIO') != -1:  # Check if the module is a digital module.
            return self.write_register(1000+channel, data)
        else:
            raise AttributeError('This module does not have Range information available. Try reading counts instead.')

    def read_data(self, start_channel=0, number_of_channels=1):
        """
        Reads channel data from the module.
        :param start_channel: channel to start reading from.
        :param number_of_channels: how many channels you want to read, self.get_number_of_channels() can be used.
        :return: list(float)
        """
        return self._read_data_address_input(1000, start_channel, number_of_channels)

    def write_data(self, start_channel, data_set):
        """
        Writes data_set to the module starting at channel start_channel, data_set has to be iterable.
        :param start_channel: 
        :param data_set: 
        :return: 
        """
        for i in range(len(data_set)):
            self.write_data_counts(i+start_channel, data_set[i])

    #########################
    # Magic Methods Override.
    #########################

    # String

    def __str__(self):
        return self.module_information()

    def __repr__(self):
        return self.__str__()

    # Iteration

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        try:
            data = self.read_channel_data(self._iter_index)
            self._iter_index += 1
            return data
        except (IndexError, AttributeError):
            raise StopIteration

    # List Behaviour

    def __len__(self):
        return self.get_number_of_channels()

    def __getitem__(self, item):
        if isinstance(item, slice):
            m_slice = list(range(self._number_of_channels))[item]
            return self.read_data(m_slice[0], len(m_slice))
        else:
            item = list(range(self._number_of_channels))[item]
            return self.read_channel_data(item)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            m_slice = list(range(self._number_of_channels))[key]
            if len(m_slice) != len(m_slice):
                raise AssertionError('key and value are not the same length.')
            for i in range(len(m_slice)):
                m_slice[i] = self.write_channel_data(m_slice[i], value[i])
        else:
            key = list(range(self._number_of_channels))[key]
            return self.write_channel_data(key, value)
