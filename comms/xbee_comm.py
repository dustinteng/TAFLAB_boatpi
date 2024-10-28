# comms/xbee_comm.py

from digi.xbee.devices import XBeeDevice
import json

port_address = "/dev/ttyXbee"
class XBeeComm:
    def __init__(self, port= port_address, baud_rate=115200):
        self.device = XBeeDevice(port, baud_rate)
        self.device.open()

    def add_data_received_callback(self, callback):
        self.device.add_data_received_callback(callback)

    def close(self):
        if self.device is not None and self.device.is_open():
            self.device.close()
            
    def send_data(self, data):
        self.device.send_data_broadcast(data)
