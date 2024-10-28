# coding: UTF-8
from abc import abstractmethod, ABCMeta

"""
Protocol Resolver Interface Class
"""

class IProtocolResolver(metaclass=ABCMeta):

    @abstractmethod
    def setConfig(self, config):
        """
        Set configuration
        :param config: Configuration information
        :return:
        """
        pass

    @abstractmethod
    def sendData(self, sendData, deviceModel):
        """
        Send data
        :param sendData: Data to send
        :param deviceModel: Device model
        :return:
        """
        pass

    @abstractmethod
    def readReg(self, regAddr, regCount, deviceModel):
        """
        Read register
        :param regAddr: Register address
        :param regCount: Number of registers
        :param deviceModel: Device model
        :return:
        """
        pass

    @abstractmethod
    def writeReg(self, regAddr, sValue, deviceModel):
        """
        Write to register
        :param regAddr: Register address
        :param sValue: Value to write
        :param deviceModel: Device model
        :return:
        """
        pass

    @abstractmethod
    def passiveReceiveData(self, data, deviceModel):
        """
        Parse data passively received
        :param data: Received data
        :param deviceModel: Device model
        :return:
        """
        pass

    @abstractmethod
    def unlock(self, deviceModel):
        """
        Unlock
        :return:
        """
        pass

    @abstractmethod
    def save(self, deviceModel):
        """
        Save
        :return:
        """
        pass

    @abstractmethod
    def AccelerationCalibration(self, deviceModel):
        """
        Accelerometer calibration
        :return:
        """
        pass

    @abstractmethod
    def BeginFiledCalibration(self, deviceModel):
        """
        Start magnetic field calibration
        :return:
        """
        pass

    @abstractmethod
    def EndFiledCalibration(self, deviceModel):
        """
        End magnetic field calibration
        :return:
        """
        pass
