# RotaryDial parser using polling mehod

import RPi.GPIO as GPIO
import time
from RawInput import RawInput

      

def pollDial():
    #use Dial input to get the number typed
    USE_DIAL_INPUT = True
    pin_digit = 2
    pin_dial = 3
    pin_hook = 4
    # Set GPIO mode to Broadcom SOC numbering
    GPIO.setmode(GPIO.BCM)
    # set the input to pullup (no need for 2 and 3)
    GPIO.setup(pin_digit, GPIO.IN)
    GPIO.setup(pin_dial, GPIO.IN)
    GPIO.setup(pin_hook, GPIO.IN, GPIO.PUD_UP)
    #timeout to declare which digit it is
    timeout = 0.5

    
    lastedge = time.time()
    #inialize the debouncer wih 20ms deboucne time
    DebDigit = RawInput(init = 1, low_high=0.02, high_low=0.02)
    DebDial = RawInput(init = 1, low_high=0.02, high_low=0.02)
    digit_state = DebDigit.debounce(GPIO.input(pin_digit))
    #trick to avoid a digit detection at start
    time.sleep(0.03)
    digit_state = DebDigit.debounce(GPIO.input(pin_digit))
    old_digit_state = digit_state
    old_dial_state = DebDial.debounce(GPIO.input(pin_dial))
    countzeroes = 0 
    while(1):
        #digit_state = GPIO.input(pin_digit) #does not work wihout debounce
        digit_state = DebDigit.debounce(GPIO.input(pin_digit))
        dial_state = DebDial.debounce(GPIO.input(pin_dial))

        #we detect edges and count zeroes
        if digit_state != old_digit_state and not dial_state:
            old_digit_state = digit_state
            lastedge = time.time()
            if not digit_state:
                countzeroes += 1
        
        #when no mo edges for timeout, it means it is the end and we have our number
        #Or we use use rising edge of Dial pin 
        if not USE_DIAL_INPUT and (time.time() - lastedge > timeout) and countzeroes \
           or USE_DIAL_INPUT and not old_dial_state and dial_state and countzeroes:

            if countzeroes >= 10:
                digit = 0
            else:
                digit = countzeroes
            countzeroes = 0
            
            print("digit: %d"%(digit))
        old_dial_state = dial_state
            
    

    
def main():
    pollDial()
    #dial = RotaryDial()
    #dial.RegisterCallback(NumberCallback = debugcallback, OffHookCallback = debugcallback, OnHookCallback = debugcallback, OnVerifyHook = debugcallback)

    

if __name__ == "__main__":
    main()
