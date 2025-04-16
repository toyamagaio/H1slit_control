# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO

class GPIOController(object):
    def __init__(self, pins, edge='both', bouncetime=200):
        """
        :param pins: List of GPIO pin num
        :param edge: 'rising', 'falling', 'both'
        :param bouncetime: chattering eliminatorÅimsÅj
        """
        self.pins = pins
        self.callbacks = {}

        GPIO.setmode(GPIO.BCM)
        for pin in pins:
            GPIO.setup(pin, GPIO.IN)
            self._setup_interrupt(pin, edge, bouncetime)

    def _setup_interrupt(self, pin, edge, bouncetime):
        gpio_edge = {
            'rising': GPIO.RISING,
            'falling': GPIO.FALLING,
            'both': GPIO.BOTH
        }.get(edge, GPIO.BOTH)

        GPIO.add_event_detect(pin, gpio_edge,
                              callback=self._make_internal_callback(pin),
                              bouncetime=bouncetime)

    def _make_internal_callback(self, pin):
        def _callback(channel):
            state = GPIO.input(channel)
            if pin in self.callbacks:
                self.callbacks[pin](pin, state)
        return _callback

    def register_callback(self, pin, callback_fn):
        """ collback func for each pin """
        self.callbacks[pin] = callback_fn

    def get_state(self, pin):
        return GPIO.input(pin)

    def cleanup(self):
        for pin in self.pins:
            GPIO.remove_event_detect(pin)
        GPIO.cleanup()
