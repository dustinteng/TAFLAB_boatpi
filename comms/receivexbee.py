from digi.xbee.devices import XBeeDevice
import RPi.GPIO as GPIO
import time
import json

# Servo initiation for rudder and sail
rudder_pin = 16  # GPIO pin for rudder servo
sail_pin = 18    # GPIO pin for sail servo

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(rudder_pin, GPIO.OUT)
GPIO.setup(sail_pin, GPIO.OUT)

# Set up PWM for both servos (50Hz frequency)
rudder_pwm = GPIO.PWM(rudder_pin, 50)
sail_pwm = GPIO.PWM(sail_pin, 50)

# Start PWM with 0% duty cycle (off)
rudder_pwm.start(0)
sail_pwm.start(0)

# XBee initiation
PORT = "/dev/ttyXbee"
BAUD_RATE = 115200

# Function to move the servo to the desired angle
def move_servo(pwm, angle):
    duty_cycle = 2 + (angle / 18)  # Convert angle to duty cycle (0-180 degrees)
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)  # Adjust time as needed
    pwm.ChangeDutyCycle(0)

def main():
    print(" +-----------------------------------------+")
    print(" | XBee Python Library Receive Data Sample |")
    print(" +-----------------------------------------+\n")

    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()

        def data_receive_callback(xbee_message):
            print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),
                                     xbee_message.data.decode()))
            try:
                # Decode the JSON message
                data = json.loads(xbee_message.data.decode())
                
                # Extract angles for rudder, sail, and throttle
                rudder_angle = float(data.get('rudder_angle', 0))
                sail_angle = float(data.get('sail_angle', 0))
                throttle = float(data.get('throttle', 0))  # Assuming throttle is a percentage

                # Print the received angles
                print(f"Rudder Angle: {rudder_angle}, Sail Angle: {sail_angle}, Throttle: {throttle}")

                # Validate and move the servos
                if 0 <= rudder_angle <= 180:
                    move_servo(rudder_pwm, rudder_angle)
                else:
                    print("Invalid rudder angle. Must be between 0 and 180.")

                if 0 <= sail_angle <= 90:  # Assuming sail angle is limited to 90 degrees
                    move_servo(sail_pwm, sail_angle)
                else:
                    print("Invalid sail angle. Must be between 0 and 90.")

                # You can add functionality to use throttle if needed (e.g., control motor speed)
                # Here throttle is just printed, you can process it accordingly.
                print(f"Throttle: {throttle}%")

            except (ValueError, json.JSONDecodeError) as e:
                print(f"Error: {e}")
                print("Invalid data received. Please send valid JSON.")

        # Set up the XBee to receive data
        device.add_data_received_callback(data_receive_callback)

        print("Waiting for data...\n")
        input()  # Keep the script running and waiting for input

    finally:
        if device is not None and device.is_open():
            device.close()
        rudder_pwm.stop()
        sail_pwm.stop()
        GPIO.cleanup()  # Cleanup GPIO when done

if __name__ == '__main__':
    main()
