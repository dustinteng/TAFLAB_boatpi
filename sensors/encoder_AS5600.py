# encoder.py

import RPi.GPIO as GPIO

class WindvaneEncoder:
    def __init__(self, pin_a, pin_b):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.position = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_a, GPIO.IN)
        GPIO.setup(self.pin_b, GPIO.IN)

        GPIO.add_event_detect(self.pin_a, GPIO.BOTH, callback=self._update)
        GPIO.add_event_detect(self.pin_b, GPIO.BOTH, callback=self._update)

    def _update(self, channel):
        a = GPIO.input(self.pin_a)
        b = GPIO.input(self.pin_b)
        if a == b:
            self.position += 1
        else:
            self.position -= 1

    def get_position(self):
        return self.position

    def cleanup(self):
        GPIO.cleanup([self.pin_a, self.pin_b])
