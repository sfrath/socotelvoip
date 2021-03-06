from threading import Timer
import time
import alsaaudio
import wave
import RPi.GPIO as GPIO
import time
import sys
import os
import yaml

class Ringtone:
    shouldring = 0
    ringtone = None

    ringstart = 0

    shouldplayhandset = 0
    handsetfile = None
    timerHandset = None

    config = None

    #ouput to have 12v on the bell actuator
    pin_pwr = 14
    #output of the bell
    pin_pos = 15
    pin_neg = 18
    #alternating current period
    flipping_period = 0.05
    #how long ring is on while ringing
    time_ring_on = 2
    #pause time between two rings
    time_ring_off = 4

    def __init__(self, config):
        self.config = config
        
        
        # Set GPIO mode to Broadcom SOC numbering
        GPIO.setmode(GPIO.BCM)
        # set the output
        GPIO.setup(self.pin_pwr, GPIO.OUT)
        GPIO.setup(self.pin_pos, GPIO.OUT)
        GPIO.setup(self.pin_neg, GPIO.OUT)

            

    def start(self):
        self.shouldring = 1
        self.ringtone = Timer(0, self.doring)
        print("starting thread")
        self.ringtone.start()
        self.ringstart = time.time()
        

    def stop(self):
        self.shouldring = 0
        time.sleep(0.05)
        if self.ringtone is not None:
            self.ringtone.cancel()

    def starthandset(self, file):
        self.shouldplayhandset = 1
        self.handsetfile = file
        if self.timerHandset is not None:
            print("[RINGTONE] Handset already playing?")
            return

        self.timerHandset = Timer(0, self.playhandset)
        self.timerHandset.start()

    def stophandset(self):
        self.shouldplayhandset = 0
        if self.timerHandset is not None:
            self.timerHandset.cancel()
            self.timerHandset = None

    def playhandset(self):
        print("Starting dialtone")
        wv = wave.open(self.handsetfile)
        device = alsaaudio.PCM(card="plug:external")
        #device.setchannels(wv.getnchannels())
        #device.setrate(wv.getframerate())
        #device.setperiodsize(320)

        data = wv.readframes(320)
        while data and self.shouldplayhandset:
            device.write(data)
            data = wv.readframes(320)
        wv.rewind()
        wv.close()


    def playfile(self, file):
        wv = wave.open(file)
        self.device = alsaaudio.PCM(card="pulse")
        self.device.setchannels(wv.getnchannels())
        self.device.setrate(wv.getframerate())
        self.device.setperiodsize(320)

        data = wv.readframes(320)
        while data:
            self.device.write(data)
            data = wv.readframes(320)
        wv.rewind()
        wv.close()

    def doring(self):
        #value to activate relay (Low side control)
        RELAY_ON = 0

        #switch off bell
        GPIO.output(self.pin_pos, RELAY_ON)
        GPIO.output(self.pin_neg, not RELAY_ON)
        time.sleep(0.2)
        #activate 12V output
        GPIO.output(self.pin_pwr, RELAY_ON)
        time.sleep(0.2)
        
        flip_output = RELAY_ON
        time_to_flip = time.time()
        time_to_pause = time.time()

        print("start ringing")
        while self.shouldring :
            now = time.time()

            

            if now - time_to_pause >= self.time_ring_on + self.time_ring_off:
                time_to_pause = now
                print("pausing")
            elif now - time_to_pause < self.time_ring_on:
                #flip bell output
                GPIO.output(self.pin_pos, flip_output)
                GPIO.output(self.pin_neg, flip_output)

                #alternating current logic
                if now - time_to_flip >= self.flipping_period:
                    time_to_flip = now
                    flip_output = not flip_output
            
            if now - 60 > self.ringstart:
                self.stop()

            time.sleep(0.01)
        
        #deactivate 12V output
        GPIO.output(self.pin_pwr, not RELAY_ON) 
            

        
if __name__ == "__main__":
    with open("../configuration.yml") as file:
        config = yaml.load(file)
        #GPIO.cleanup()
        ringtone = Ringtone(config)
        print("start ringing")
        ringtone.start()
        print("sleep")
        time.sleep(10)
        print("stop thread")
        ringtone.stop()
        GPIO.cleanup()

    
