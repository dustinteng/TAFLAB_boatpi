# coding: UTF-8
import threading
import _thread
import time
import struct
import serial
from serial import SerialException

'''
    Serial Configuration
'''

class SerialConfig:
    # Port name
    portName = ''

    # Baud rate
    baud = 9600

'''
Device Model
'''

class DeviceModel:
    # Device name
    deviceName = "my devices"

    # Device ID
    ADDR = 0x50

    # Device data dictionary
    deviceData = {}

    # Whether the device is open
    isOpen = False

    # Serial port
    serialPort = None

    # Serial configuration
    serialConfig = SerialConfig()

    # Update trigger
    dataUpdateListener = ""

    # Data processor
    dataProcessor = None

    # Protocol resolver
    protocolResolver = None

    def __init__(self, deviceName, protocolResolver, dataProcessor, dataUpdateListener):
        print("Initializing device model")
        self.deviceName = deviceName
        self.protocolResolver = protocolResolver
        self.dataProcessor = dataProcessor
        self.dataUpdateListener = dataUpdateListener

    def setDeviceData(self, key, value):
        """
        Set device data
        :param key: Data key
        :param value: Data value
        :return: No return
        """
        self.deviceData[key] = value

    def getDeviceData(self, key):
        """
        Get device data
        :param key: Data key
        :return: Returns data value; returns None if key does not exist
        """
        return self.deviceData.get(key, None)

    def removeDeviceData(self, key):
        """
        Remove device data
        :param key: Data key
        :return: No return
        """
        self.deviceData.pop(key, None)

    def readDataTh(self, threadName, delay):
        """
        Data reading thread
        :return:
        """
        print("Starting " + threadName)
        while True:
            # If the serial port is open
            if self.isOpen:
                try:
                    tlen = self.serialPort.inWaiting()
                    if tlen > 0:
                        data = self.serialPort.read(tlen)
                        self.onDataReceived(data)
                except Exception as ex:
                    print(ex)
            else:
                time.sleep(0.1)
                print("Paused")
                break

    def openDevice(self):
        """
        Open the device
        :return: No return
        """
        # Close the port first
        self.closeDevice()
        try:
            self.serialPort = serial.Serial(self.serialConfig.portName, self.serialConfig.baud, timeout=0.5)
            self.isOpen = True
            t = threading.Thread(target=self.readDataTh, args=("Data-Received-Thread", 10,))  # Start a thread to receive data
            t.start()
        except SerialException:
            print(f"Failed to open {self.serialConfig.portName} at {self.serialConfig.baud}")

    def closeDevice(self):
        """
        Close the device
        :return: No return
        """
        if self.serialPort is not None:
            self.serialPort.close()
            print("Port closed")
        self.isOpen = False
        print("Device closed")

    def onDataReceived(self, data):
        """
        When data is received
        :param data: Received data
        :return: No return
        """
        if self.protocolResolver is not None:
            self.protocolResolver.passiveReceiveData(data, self)

    def get_int(self, dataBytes):
        """
        Convert to signed integer, equivalent to C# BitConverter.ToInt16
        :param dataBytes: Byte array
        :return:
        """
        return int.from_bytes(dataBytes, "little", signed=True)

    def get_unint(self, dataBytes):
        """
        Convert to unsigned integer
        :param dataBytes: Byte array
        :return:
        """
        return int.from_bytes(dataBytes, "little")

    def sendData(self, data):
        """
        Send data
        :return: Success status
        """
        if self.protocolResolver is not None:
            self.protocolResolver.sendData(data, self)

    def readReg(self, regAddr, regCount):
        """
        Read register
        :param regAddr: Register address
        :param regCount: Number of registers
        :return:
        """
        if self.protocolResolver is not None:
            return self.protocolResolver.readReg(regAddr, regCount, self)
        else:
            return None

    def writeReg(self, regAddr, sValue):
        """
        Write to register
        :param regAddr: Register address
        :param sValue: Value to write
        :return:
        """
        if self.protocolResolver is not None:
            self.protocolResolver.writeReg(regAddr, sValue, self)

    def unlock(self):
        """
        Unlock
        :return:
        """
        if self.protocolResolver is not None:
            self.protocolResolver.unlock(self)

    def save(self):
        """
        Save
        :return:
        """
        if self.protocolResolver is not None:
            self.protocolResolver.save(self)

    def AccelerationCalibration(self):
        """
        Acceleration calibration
        :return:
        """
        if self.protocolResolver is not None:
            self.protocolResolver.AccelerationCalibration(self)

    def BeginFiledCalibration(self):
        """
        Start magnetic field calibration
        :return:
        """
        if self.protocolResolver is not None:
            self.protocolResolver.BeginFiledCalibration(self)

    def EndFiledCalibration(self):
        """
        End magnetic field calibration
        :return:
        """
        if self.protocolResolver is not None:
            self.protocolResolver.EndFiledCalibration(self)

    def sendProtocolData(self, data):
        """
        Send data with protocol
        :return:
        """
        if self.protocolResolver is not None:
            self.protocolResolver.sendData(data)
