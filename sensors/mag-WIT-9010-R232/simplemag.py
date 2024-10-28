# coding: UTF-8
"""
    Test file
"""
import time
import platform
import lib.device_model as deviceModel
from lib.data_processor.roles.jy901s_dataProcessor import JY901SDataProcessor
from lib.protocol_resolver.roles.wit_protocol_resolver import WitProtocolResolver

welcome = """
Welcome to the Wit-Motion sample program
"""

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
        print('check other coms')
        device.serialConfig.portName = "COM17"          # Set serial port for other systems
    device.serialConfig.baud = 115200                   # Set baud rate
    device.openDevice()                                 # Open serial port

    readConfig(device)                                  # Read configuration information
    device.dataProcessor.onVarChanged.append(onUpdate)  # Register data update event

    # Run indefinitely to observe onUpdate triggers
    try:
        while True:
            time.sleep(1)  # Adjust sleep duration as needed
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        device.closeDevice()  # Close the device when done
