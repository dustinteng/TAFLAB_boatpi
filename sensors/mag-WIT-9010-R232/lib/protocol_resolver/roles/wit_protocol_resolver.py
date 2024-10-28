# coding: UTF-8
import time
from lib.protocol_resolver.interface.i_protocol_resolver import IProtocolResolver

"""
    Wit Protocol Resolver
"""

class WitProtocolResolver(IProtocolResolver):
    TempBytes = []         # Temporary data list
    PackSize = 11          # Size of one data packet
    gyroRange = 2000.0     # Gyroscope range
    accRange = 16.0        # Acceleration range
    angleRange = 180.0     # Angle range
    TempFindValues = []    # Data returned from reading a specific register

    def setConfig(self, deviceModel):
        pass

    def sendData(self, sendData, deviceModel):
        success_bytes = deviceModel.serialPort.write(sendData)

    def passiveReceiveData(self, data, deviceModel):
        """
        Data processing upon receiving
        :param data: Serial data
        :param deviceModel: Device model
        :return:
        """
        global TempBytes
        for val in data:
            self.TempBytes.append(val)
            if self.TempBytes[0] != 0x55:                   # Not starting with identifier 0x55
                del self.TempBytes[0]                       # Remove the first byte
                continue
            if len(self.TempBytes) > 1:
                if not (0x50 <= self.TempBytes[1] <= 0x5A or self.TempBytes[1] == 0x5F):   # Second byte value not in 0x50-0x5A or not equal to 0x5F
                    del self.TempBytes[0]                   # Remove the first byte
                    continue
            if len(self.TempBytes) == self.PackSize:        # Indicates one packet of data
                CheckSum = sum(self.TempBytes[:-1])         # Calculate checksum
                if (CheckSum & 0xFF) == self.TempBytes[self.PackSize - 1]:  # Checksum validation
                    if self.TempBytes[1] == 0x50:           # Chip time packet
                        self.get_chiptime(self.TempBytes, deviceModel)  # Process chip time data
                    elif self.TempBytes[1] == 0x51:         # Acceleration packet
                        self.get_acc(self.TempBytes, deviceModel)       # Process acceleration data
                    elif self.TempBytes[1] == 0x52:         # Gyroscope packet
                        self.get_gyro(self.TempBytes, deviceModel)      # Process gyroscope data
                    elif self.TempBytes[1] == 0x53:         # Angle packet
                        self.get_angle(self.TempBytes, deviceModel)     # Process angle data
                    elif self.TempBytes[1] == 0x54:         # Magnetic field packet
                        self.get_mag(self.TempBytes, deviceModel)       # Process magnetic field data
                        deviceModel.dataProcessor.onUpdate(deviceModel) # Trigger data update event
                    elif self.TempBytes[1] == 0x57:         # Longitude and latitude packet
                        self.get_lonlat(self.TempBytes, deviceModel)    # Process longitude and latitude data
                        deviceModel.dataProcessor.onUpdate(deviceModel) # Trigger data update event
                    elif self.TempBytes[1] == 0x58:         # GPS packet
                        self.get_gps(self.TempBytes, deviceModel)       # Process GPS data
                        deviceModel.dataProcessor.onUpdate(deviceModel) # Trigger data update event
                    elif self.TempBytes[1] == 0x59:         # Quaternion packet
                        self.get_four_elements(self.TempBytes, deviceModel)  # Process quaternion data
                        deviceModel.dataProcessor.onUpdate(deviceModel) # Trigger data update event
                    elif self.TempBytes[1] == 0x5F:         # Return data from specific register read
                        self.get_find(self.TempBytes, deviceModel)
                    self.TempBytes = []                     # Clear data
                else:                                       # Checksum failed
                    del self.TempBytes[0]                   # Remove the first byte

    def get_readbytes(self, regAddr):
        """
        Get read command
        :param regAddr: Register address
        :return:
        """
        return [0xFF, 0xAA, 0x27, regAddr & 0xFF, regAddr >> 8]

    def get_writebytes(self, regAddr, sValue):
        """
        Get write command
        :param regAddr: Register address
        :param sValue: Value to write
        :return:
        """
        return [0xFF, 0xAA, regAddr, sValue & 0xFF, sValue >> 8]

    def get_acc(self, datahex, deviceModel):
        """
        Process acceleration and temperature
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        axl, axh = datahex[2], datahex[3]
        ayl, ayh = datahex[4], datahex[5]
        azl, azh = datahex[6], datahex[7]
        tempVal = (datahex[9] << 8 | datahex[8])

        acc_x = (axh << 8 | axl) / 32768.0 * self.accRange
        acc_y = (ayh << 8 | ayl) / 32768.0 * self.accRange
        acc_z = (azh << 8 | azl) / 32768.0 * self.accRange

        # Adjust for range
        if acc_x >= self.accRange: acc_x -= 2 * self.accRange
        if acc_y >= self.accRange: acc_y -= 2 * self.accRange
        if acc_z >= self.accRange: acc_z -= 2 * self.accRange

        deviceModel.setDeviceData("accX", round(acc_x, 4))    # Set device model acceleration X
        deviceModel.setDeviceData("accY", round(acc_y, 4))    # Set device model acceleration Y
        deviceModel.setDeviceData("accZ", round(acc_z, 4))    # Set device model acceleration Z
        deviceModel.setDeviceData("temperature", round(tempVal / 100.0, 2))  # Set device model temperature

    def get_gyro(self, datahex, deviceModel):
        """
        Process gyroscope data
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        wxl, wxh = datahex[2], datahex[3]
        wyl, wyh = datahex[4], datahex[5]
        wzl, wzh = datahex[6], datahex[7]

        gyro_x = (wxh << 8 | wxl) / 32768.0 * self.gyroRange
        gyro_y = (wyh << 8 | wyl) / 32768.0 * self.gyroRange
        gyro_z = (wzh << 8 | wzl) / 32768.0 * self.gyroRange

        # Adjust for range
        if gyro_x >= self.gyroRange: gyro_x -= 2 * self.gyroRange
        if gyro_y >= self.gyroRange: gyro_y -= 2 * self.gyroRange
        if gyro_z >= self.gyroRange: gyro_z -= 2 * self.gyroRange

        deviceModel.setDeviceData("gyroX", round(gyro_x, 4))  # Set device model gyroscope X
        deviceModel.setDeviceData("gyroY", round(gyro_y, 4))  # Set device model gyroscope Y
        deviceModel.setDeviceData("gyroZ", round(gyro_z, 4))  # Set device model gyroscope Z

    def get_angle(self, datahex, deviceModel):
        """
        Process angle data
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        rxl, rxh = datahex[2], datahex[3]
        ryl, ryh = datahex[4], datahex[5]
        rzl, rzh = datahex[6], datahex[7]

        angle_x = (rxh << 8 | rxl) / 32768.0 * self.angleRange
        angle_y = (ryh << 8 | ryl) / 32768.0 * self.angleRange
        angle_z = (rzh << 8 | rzl) / 32768.0 * self.angleRange

        # Adjust for range
        if angle_x >= self.angleRange: angle_x -= 2 * self.angleRange
        if angle_y >= self.angleRange: angle_y -= 2 * self.angleRange
        if angle_z >= self.angleRange: angle_z -= 2 * self.angleRange

        deviceModel.setDeviceData("angleX", round(angle_x, 3))  # Set device model angle X
        deviceModel.setDeviceData("angleY", round(angle_y, 3))  # Set device model angle Y
        deviceModel.setDeviceData("angleZ", round(angle_z, 3))  # Set device model angle Z

    def get_mag(self, datahex, deviceModel):
        """
        Process magnetic field data
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        _x = deviceModel.get_int(bytes([datahex[2], datahex[3]]))
        _y = deviceModel.get_int(bytes([datahex[4], datahex[5]]))
        _z = deviceModel.get_int(bytes([datahex[6], datahex[7]]))

        deviceModel.setDeviceData("magX", round(_x, 0))   # Set device model magnetic field X
        deviceModel.setDeviceData("magY", round(_y, 0))   # Set device model magnetic field Y
        deviceModel.setDeviceData("magZ", round(_z, 0))   # Set device model magnetic field Z

    def get_lonlat(self, datahex, deviceModel):
        """
        Process longitude and latitude data
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        lon = deviceModel.get_unint(bytes([datahex[2], datahex[3], datahex[4], datahex[5]]))
        lat = deviceModel.get_unint(bytes([datahex[6], datahex[7], datahex[8], datahex[9]]))

        tlon = int(lon / 10000000) + ((lon % 10000000) / 100000 / 60)
        tlat = int(lat / 10000000) + ((lat % 10000000) / 100000 / 60)

        deviceModel.setDeviceData("lon", round(tlon, 8))  # Set device model longitude
        deviceModel.setDeviceData("lat", round(tlat, 8))  # Set device model latitude

    def get_gps(self, datahex, deviceModel):
        """
        Process GPS data
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        Height = deviceModel.get_int(bytes([datahex[2], datahex[3]])) / 10.0  # Height
        Yaw = deviceModel.get_int(bytes([datahex[4], datahex[5]])) / 100.0    # Heading angle
        Speed = deviceModel.get_unint(bytes([datahex[6], datahex[7], datahex[8], datahex[9]])) / 1e3  # Nautical miles

        deviceModel.setDeviceData("Height", round(Height, 3))  # Set device model height
        deviceModel.setDeviceData("Yaw", round(Yaw, 2))        # Set device model heading angle
        deviceModel.setDeviceData("Speed", round(Speed, 3))    # Set device model speed

    def get_four_elements(self, datahex, deviceModel):
        """
        Process quaternion data
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        q1 = deviceModel.get_int(bytes([datahex[2], datahex[3]])) / 32768.0
        q2 = deviceModel.get_int(bytes([datahex[4], datahex[5]])) / 32768.0
        q3 = deviceModel.get_int(bytes([datahex[6], datahex[7]])) / 32768.0
        q4 = deviceModel.get_int(bytes([datahex[8], datahex[9]])) / 32768.0

        deviceModel.setDeviceData("q1", round(q1, 5))  # Set device model quaternion component 1
        deviceModel.setDeviceData("q2", round(q2, 5))  # Set device model quaternion component 2
        deviceModel.setDeviceData("q3", round(q3, 5))  # Set device model quaternion component 3
        deviceModel.setDeviceData("q4", round(q4, 5))  # Set device model quaternion component 4

    def get_chiptime(self, datahex, deviceModel):
        """
        Process chip time
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        tempVals = []  # Temporary data for calculations
        for i in range(4):
            tIndex = 2 + i * 2
            tempVals.append(datahex[tIndex+1] << 8 | datahex[tIndex])

        _year = 2000 + (tempVals[0] & 0xFF)      # Year
        _month = ((tempVals[0] >> 8) & 0xFF)     # Month
        _day = (tempVals[1] & 0xFF)              # Day
        _hour = ((tempVals[1] >> 8) & 0xFF)      # Hour
        _minute = (tempVals[2] & 0xFF)           # Minute
        _second = ((tempVals[2] >> 8) & 0xFF)    # Second
        _millisecond = tempVals[3]               # Millisecond

        deviceModel.setDeviceData("Chiptime",
                                  f"{_year}-{_month:02}-{_day:02} {_hour:02}:{_minute:02}:{_second:02}.{_millisecond}")  # Set chip time

    def readReg(self, regAddr, regCount, deviceModel):
        """
        Read register
        :param regAddr: Register address
        :param regCount: Number of registers
        :param deviceModel: Device model
        :return:
        """
        tempResults = []  # Return data
        readCount = (regCount + 3) // 4  # Calculate read count based on the number of registers
        for n in range(readCount):
            self.TempFindValues = []  # Clear data
            tempBytes = self.get_readbytes(regAddr + n * 4)  # Get read command
            deviceModel.serialPort.write(tempBytes)  # Write data
            for i in range(20):  # Timeout of 1 second
                time.sleep(0.05)  # Sleep 50 ms
                if self.TempFindValues:  # Value for the desired register has been returned
                    tempResults.extend(self.TempFindValues[:regCount - len(tempResults)])
                    break
        return tempResults

    def writeReg(self, regAddr, sValue, deviceModel):
        """
        Write to register
        :param regAddr: Register address
        :param sValue: Value to write
        :param deviceModel: Device model
        :return:
        """
        tempBytes = self.get_writebytes(regAddr, sValue)  # Get write command
        deviceModel.serialPort.write(tempBytes)           # Write to register

    def unlock(self, deviceModel):
        """
        Unlock
        :param deviceModel: Device model
        :return:
        """
        tempBytes = self.get_writebytes(0x69, 0xB588)     # Get unlock command
        deviceModel.serialPort.write(tempBytes)           # Write to register

    def save(self, deviceModel):
        """
        Save
        :param deviceModel: Device model
        :return:
        """
        tempBytes = self.get_writebytes(0x00, 0x00)       # Get save command
        deviceModel.serialPort.write(tempBytes)           # Write to register

    def AccelerationCalibration(self, deviceModel):
        """
        Accelerometer calibration
        :param deviceModel: Device model
        :return:
        """
        self.unlock(deviceModel)                          # Unlock
        time.sleep(0.1)                                   # Sleep 100 ms
        tempBytes = self.get_writebytes(0x01, 0x01)       # Get write command
        deviceModel.serialPort.write(tempBytes)           # Write to register
        time.sleep(5.5)                                   # Sleep 5500 ms

    def BeginFiledCalibration(self, deviceModel):
        """
        Start magnetic field calibration
        :param deviceModel: Device model
        :return:
        """
        self.unlock(deviceModel)                          # Unlock
        time.sleep(0.1)                                   # Sleep 100 ms
        tempBytes = self.get_writebytes(0x01, 0x07)       # Get write command for magnetic field calibration
        deviceModel.serialPort.write(tempBytes)           # Write to register

    def EndFiledCalibration(self, deviceModel):
        """
        End magnetic field calibration
        :param deviceModel: Device model
        :return:
        """
        self.unlock(deviceModel)                          # Unlock
        time.sleep(0.1)                                   # Sleep 100 ms
        self.save(deviceModel)                            # Save

    def get_find(self, datahex, deviceModel):
        """
        Process specific register read
        :param datahex: Original data packet
        :param deviceModel: Device model
        :return:
        """
        t0l, t0h = datahex[2], datahex[3]
        t1l, t1h = datahex[4], datahex[5]
        t2l, t2h = datahex[6], datahex[7]
        t3l, t3h = datahex[8], datahex[9]

        val0 = (t0h << 8 | t0l)
        val1 = (t1h << 8 | t1l)
        val2 = (t2h << 8 | t2l)
        val3 = (t3h << 8 | t3l)
        self.TempFindValues.extend([val0, val1, val2, val3])
