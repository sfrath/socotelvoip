# Rotary Dial Parser
# Expects the following hardware rules:
# 1 is 1 pulse
# 9 is 9 pulses
# 0 is 10 pulses

import RPi.GPIO as GPIO
from threading import Timer
import time

class RotaryDial:
    
    # we read GPIO 2 and 3 (both pullup) to acquire digits
    pin_digit = 2
    #pin_dial will go to low state when the rotary dial is touched
    pin_dial = 3

    #the hook pin will be 4, need to be configured as pullup
    pin_onhook = 4

    # After 900ms, we assume the rotation is done and we get
    # the final digit. 
    digit_timeout = 0.9

    #current coutn of rising edges
    count_rising_edges = 0 

    digit = 0

    # Simple timer for handling the number callback
    number_timeout = None

    last_input = 0

    # Timer to ensure we're on hook
    onhook_timer = None
    should_verify_hook = True

    def __init__(self):
        # Set GPIO mode to Broadcom SOC numbering
        GPIO.setmode(GPIO.BCM)

        # set the input to pullup (no need for 2 and 3)
        GPIO.setup(self.pin_digit, GPIO.IN)
        GPIO.setup(self.pin_dial, GPIO.IN)
        GPIO.setup(self.pin_onhook, GPIO.IN, GPIO.PUD_UP)

        # we will listen for the pin_digit rising edge to count
        GPIO.add_event_detect(self.pin_digit, GPIO.RISING, callback = self.DigitEdgeCounter, bouncetime=20)

        # we listen for the pin_dial edges, the falling edges will reset variables, the rising edge will end the digit acquisition
        GPIO.add_event_detect(self.pin_digit, GPIO.BOTH, callback = self.BeginEndDigit, bouncetime=50)
        
        # Listen for on/off hooks
        GPIO.add_event_detect(self.pin_onhook, GPIO.BOTH, callback = self.HookEvent, bouncetime=100)
        
        self.onhook_timer = Timer(2, self.verifyHook)
        self.onhook_timer.start()

    # mark the beginning and end of digit acquisition
    def BeginEndDigit(self, channel):
        #dial input acquisition
        dial_input = GPIO.input(self.pin_dial)

        #input high marks end of digit acquisition
        if dial_input:
            if self.count_rising_edges >= 10: #10 edges is 0
                self.digit = 0
            elif self.count_rising_edges > 0:
                self.digit = self.count_rising_edges
            else: #invalid
                self.digit = -1
            
            print("digit: %d"%(self.digit))
            self.FoundNumber()
            self.count_rising_edges = 0
        #input low marks the beginning of digit acquisition
        else:
            self.count_rising_edges = 0
            self.digit = -1

    # parse the digit by counting the rising edges of pin_digit
    def DigitEdgeCounter(self, channel):
        #dial input acquisition
        dial_input = GPIO.input(self.pin_dial)

        #we make sure the dial input is low
        if not dial_input: 
            count_rising_edges += 1

    # Wrapper around the off/on hook event 
    def HookEvent(self, channel):
        input = GPIO.input(self.pin_onhook)
        if not input:
            self.hook_state = 1
            self.OffHookCallback()
        else:
            self.hook_state = 0
            self.OnHookCallback()

    def StopVerifyHook(self):
        self.should_verify_hook = False

    def verifyHook(self):
        while self.should_verify_hook:
            state = GPIO.input(self.pin_onhook) 
            self.OnVerifyHook(state)
            time.sleep(1)

    # When the rotary movement has timed out, we callback with the final digit
    def FoundNumber(self):
        print("Found number: %d"%self.digit)
        self.NumberCallback(self.digit)

    # Handles the callbacks we're supplying
    def RegisterCallback(self, NumberCallback, OffHookCallback, OnHookCallback, OnVerifyHook):
        self.NumberCallback = NumberCallback
        self.OffHookCallback = OffHookCallback
        self.OnHookCallback = OnHookCallback
        self.OnVerifyHook = OnVerifyHook

        input = GPIO.input(self.pin_onhook)
        if not input:
            self.OffHookCallback()
        else:
            self.OnHookCallback()



def debugcallback(donnee):
    print(donnee)
    
def main():
    dial = RotaryDial()
    #dial.RegisterCallback(NumberCallback = debugcallback, OffHookCallback = debugcallback, OnHookCallback = debugcallback, OnVerifyHook = debugcallback)

    

if __name__ == "__main__":
    main()
