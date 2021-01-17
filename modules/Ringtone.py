from threading import Timer
import time
import alsaaudio
import wave
import RPi.GPIO as GPIO
import time

class Ringtone:
    shouldring = 0
    ringtone = None
    ringfile = None

    ringstart = 0

    shouldplayhandset = 0
    handsetfile = None
    timerHandset = None

    config = None

    def __init__(self, config):
        self.config = config

    def start(self):
        self.shouldring = 1
        self.ringtone = Timer(0, self.doring)
        self.ringtone.start()
        self.ringstart = time.time()

    def stop(self):
        self.shouldring = 0
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
        if self.ringfile is not None:
            self.ringfile.rewind()
        else:
            self.ringfile = wave.open(self.config["soundfiles"]["ringtone"], 'rb')
            self.device = alsaaudio.PCM(card="pulse")
            self.device.setchannels(self.ringfile.getnchannels())
            self.device.setrate(self.ringfile.getframerate())
            self.device.setperiodsize(320)


        while self.shouldring:
            data = self.ringfile.readframes(320)
            while data:
                self.device.write(data)
                data = self.ringfile.readframes(320)

            self.ringfile.rewind()
            time.sleep(2)
            if time.time() - 60 > self.ringstart:
                self.stop()

def ring(duration = 2):
    #ouput to have 12v
    pin_pwr = 14
    #output of the bell
    pin_pos = 15
    pin_neg = 18
    #alternating current period
    alt_period = 0.08
    RELAY_ON = 0

    # Set GPIO mode to Broadcom SOC numbering
    GPIO.setmode(GPIO.BCM)
    # set the output
    GPIO.setup(pin_pwr, GPIO.OUT)
    GPIO.setup(pin_pos, GPIO.OUT)
    GPIO.setup(pin_neg, GPIO.OUT)

    now = time.time()
    begin = now
    alt_current = RELAY_ON
    time_alt = now
    while now - begin <= duration:
        #activate output
        GPIO.output(pin_pwr, RELAY_ON)        
        GPIO.output(pin_pos, alt_current)
        GPIO.output(pin_neg, alt_current)
        
        
        #alternating current logic
        if now - time_alt >= alt_period:
            time_alt = now
            alt_current = not alt_current
        
        time.sleep(0.01)
        now = time.time()

    GPIO.cleanup()
            

        

def main():
    time.sleep(1)
    ring(2)

if __name__ == "__main__":
    main()

    
