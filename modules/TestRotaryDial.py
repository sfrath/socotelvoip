# RotaryDial parser using polling mehod

import RPi.GPIO as GPIO
import time
from modules.RawInput import RawInput

      

def pollDial():
    pin_digit = 2
    pin_dial = 3
    pin_hook = 4
    # Set GPIO mode to Broadcom SOC numbering
    GPIO.setmode(GPIO.BCM)
    # set the input to pullup!
    GPIO.setup(pin_digit, GPIO.IN, GPIO.PUD_UP)
    #timeout to declare which digit it is
    timeout = 0.5

    
    lastedge = time.time()
    #inialize the debouncer wih 20ms deboucne time
    rawinput = RawInput(init = 1, low_high=0.02, high_low=0.02)
    newstate = rawinput.debounce(GPIO.input(pin_digit))
    #trick to avoid a digit detection at start
    time.sleep(0.03)
    newstate = rawinput.debounce(GPIO.input(pin_digit))
    state = newstate    
    countzeroes = 0 
    while(1):
        #newstate = GPIO.input(pin_digit) #does not work wihout debounce
        newstate = rawinput.debounce(GPIO.input(pin_digit))

        #we detect edges and count zeroes
        if newstate != state:
            state = newstate
            lastedge = time.time()
            if not newstate:
                countzeroes += 1
                
            #print("Edge detected, state is now %d"%newstate)
        #when no mo edges for timeout, it means it is the end and we have our number
        if (time.time() - lastedge > timeout) and countzeroes:

            if countzeroes >= 10:
                digit = 0
            else:
                digit = countzeroes
            countzeroes = 0
            
            print("digit: %d"%(digit))
            
    

    
def main():
    pollDial()
    #dial = RotaryDial()
    #dial.RegisterCallback(NumberCallback = debugcallback, OffHookCallback = debugcallback, OnHookCallback = debugcallback, OnVerifyHook = debugcallback)

    

if __name__ == "__main__":
    main()
