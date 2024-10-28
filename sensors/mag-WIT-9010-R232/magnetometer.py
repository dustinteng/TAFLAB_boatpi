# coding: UTF-8
"""
    Test file
"""
import time
import datetime
import platform
import struct
import lib.device_model as deviceModel
from lib.data_processor.roles.jy901s_dataProcessor import JY901SDataProcessor
from lib.protocol_resolver.roles.wit_protocol_resolver import WitProtocolResolver

welcome = """
Welcome to the Wit-Motion sample program
"""
_writeF = None                    # File for writing data
_IsWriteF = False                 # Flag indicating whether to write data

def readConfig(device):
    """
    Example of reading configuration information
    :param device: Device model
    :return:
    """
    tVals = device.readReg(0x02, 3)  # Read data content, return rate, communication rate
    if len(tVals) > 0:
        print("Return result: " + str(tVals))
    else:
        print("No return data content return rate comm rate")
    tVals = device.readReg(0x23, 2)  # Read installation direction and algorithm
    if len(tVals) > 0:
        print("Return result: " + str(tVals))
    else:
        print("No return installation direction and algo")

def setConfig(device):
    """
    Example of setting configuration information
    :param device: Device model
    :return:
    """
    device.unlock()                # Unlock
    time.sleep(0.1)                # Sleep 100ms
    device.writeReg(0x03, 6)       # Set the transmission rate to 10Hz
    time.sleep(0.1)                # Sleep 100ms
    device.writeReg(0x23, 0)       # Set installation direction: horizontal and vertical
    time.sleep(0.1)                # Sleep 100ms
    device.writeReg(0x24, 0)       # Set installation direction: nine-axis, six-axis
    time.sleep(0.1)                # Sleep 100ms
    device.save()                  # Save configuration

def AccelerationCalibration(device):
    """
    Acceleration calibration
    :param device: Device model
    :return:
    """
    device.AccelerationCalibration()  # Perform acceleration calibration
    print("Acceleration calibration completed")

def FiledCalibration(device):
    """
    Magnetic field calibration
    :param device: Device model
    :return:
    """
    device.BeginFiledCalibration()  # Start magnetic field calibration
    if input("Please slowly rotate around the X, Y, and Z axes one at a time. After completing all three, end calibration (Y/N)?").lower() == "y":
        device.EndFiledCalibration()  # End magnetic field calibration
        print("Magnetic field calibration completed")

def onUpdate(deviceModel):
    """
    Data update event
    :param deviceModel: Device model
    :return:
    """
    print("Chip Time:" + str(deviceModel.getDeviceData("Chiptime")),
          " Temperature:" + str(deviceModel.getDeviceData("temperature")),
          " Acceleration:" + str(deviceModel.getDeviceData("accX")) + "," + str(deviceModel.getDeviceData("accY")) + "," + str(deviceModel.getDeviceData("accZ")),
          " Gyro:" + str(deviceModel.getDeviceData("gyroX")) + "," + str(deviceModel.getDeviceData("gyroY")) + "," + str(deviceModel.getDeviceData("gyroZ")),
          " Angle:" + str(deviceModel.getDeviceData("angleX")) + "," + str(deviceModel.getDeviceData("angleY")) + "," + str(deviceModel.getDeviceData("angleZ")),
          " Magnetic Field:" + str(deviceModel.getDeviceData("magX")) + "," + str(deviceModel.getDeviceData("magY")) + "," + str(deviceModel.getDeviceData("magZ")),
          " Longitude:" + str(deviceModel.getDeviceData("lon")) + " Latitude:" + str(deviceModel.getDeviceData("lat")),
          " Yaw:" + str(deviceModel.getDeviceData("Yaw")) + " Speed:" + str(deviceModel.getDeviceData("Speed")),
          " Quaternion:" + str(deviceModel.getDeviceData("q1")) + "," + str(deviceModel.getDeviceData("q2")) + "," + str(deviceModel.getDeviceData("q3")) + "," + str(deviceModel.getDeviceData("q4"))
          )
    if _IsWriteF:  # Record data
        Tempstr = " " + str(deviceModel.getDeviceData("Chiptime"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("accX")) + "\t" + str(deviceModel.getDeviceData("accY")) + "\t" + str(deviceModel.getDeviceData("accZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("gyroX")) + "\t" + str(deviceModel.getDeviceData("gyroY")) + "\t" + str(deviceModel.getDeviceData("gyroZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("angleX")) + "\t" + str(deviceModel.getDeviceData("angleY")) + "\t" + str(deviceModel.getDeviceData("angleZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("temperature"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("magX")) + "\t" + str(deviceModel.getDeviceData("magY")) + "\t" + str(deviceModel.getDeviceData("magZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("lon")) + "\t" + str(deviceModel.getDeviceData("lat"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("Yaw")) + "\t" + str(deviceModel.getDeviceData("Speed"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("q1")) + "\t" + str(deviceModel.getDeviceData("q2"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("q3")) + "\t" + str(deviceModel.getDeviceData("q4"))
        Tempstr += "\r\n"
        _writeF.write(Tempstr)

def startRecord():
    """
    Start recording data
    :return:
    """
    global _writeF
    global _IsWriteF
    _writeF = open(str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".txt", "w")  # Create a new file
    _IsWriteF = True  # Enable writing flag
    Tempstr = "Chiptime"
    Tempstr += "\tax(g)\tay(g)\taz(g)"
    Tempstr += "\twx(deg/s)\twy(deg/s)\twz(deg/s)"
    Tempstr += "\tAngleX(deg)\tAngleY(deg)\tAngleZ(deg)"
    Tempstr += "\tT(°)"
    Tempstr += "\tmagx\tmagy\tmagz"
    Tempstr += "\tlon\tlat"
    Tempstr += "\tYaw\tSpeed"
    Tempstr += "\tq1\tq2\tq3\tq4"
    Tempstr += "\r\n"
    _writeF.write(Tempstr)
    print("Started recording data")

def endRecord():
    """
    End recording data
    :return:
    """
    global _writeF
    global _IsWriteF
    _IsWriteF = False             # Disable writing flag
    _writeF.close()               # Close file
    print("Data recording ended")

if __name__ == '__main__':

    print(welcome)
    """
    Initialize a device model
    """
    device = deviceModel.DeviceModel(
        "myJY901",
        WitProtocolResolver(),
        JY901SDataProcessor(),
        "51_0"
    )

    if platform.system().lower() == 'linux':
        device.serialConfig.portName = "/dev/ttyUSB1"   # Set serial port for Linux
    else:
        print('check other coms')         # Set serial port for other systems
    device.serialConfig.baud = 115200                   # Set baud rate
    device.openDevice()                                 # Open serial port
    readConfig(device)                                  # Read configuration information
    device.dataProcessor.onVarChanged.append(onUpdate)  # Register data update event

    startRecord()                                       # Start recording data
    input()
    device.closeDevice()
    endRecord()                                         # End data recording
