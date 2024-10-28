# servos.py

import RPi.GPIO as GPIO
import time

class Servos:
    def __init__(self, rudder_pin=16, sail_pin=18):
        # Servo initiation for rudder and sail
        self.rudder_pin = rudder_pin  # GPIO pin for rudder servo
        self.sail_pin = sail_pin      # GPIO pin for sail servo

        # Set up GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.rudder_pin, GPIO.OUT)
        GPIO.setup(self.sail_pin, GPIO.OUT)

        # Set up PWM for both servos (50Hz frequency)
        self.rudder_pwm = GPIO.PWM(self.rudder_pin, 50)
        self.sail_pwm = GPIO.PWM(self.sail_pin, 50)

        # Start PWM with 0% duty cycle (off)
        self.rudder_pwm.start(0)
        self.sail_pwm.start(0)

    def move_servo(self, pwm, angle):
        duty_cycle = 2 + (angle / 18)  # Convert angle to duty cycle (0-180 degrees)
        pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)  # Adjust time as needed
        pwm.ChangeDutyCycle(0)

    def set_rudder_angle(self, angle):
        if 0 <= angle <= 180:
            self.move_servo(self.rudder_pwm, angle)
        else:
            print("Invalid rudder angle. Must be between 0 and 180.")

    def set_sail_angle(self, angle):
        if 0 <= angle <= 90:  # Assuming sail angle is limited to 90 degrees
            self.move_servo(self.sail_pwm, angle)
        else:
            print("Invalid sail angle. Must be between 0 and 90.")

    def cleanup(self):
        self.rudder_pwm.stop()
        self.sail_pwm.stop()
        GPIO.cleanup()
