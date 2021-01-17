# SW debouncer for raw GPIO input, must use polling mehod
import time

class RawInput():
    def __init__(self, init=0, low_high=0.02, high_low=0.02):
        #initial state
        self.out = init
        #time to wait for low to high, 20ms default
        self.low_high = low_high
        #time to wait from high to low, 20ms default
        self.high_low = high_low
        #internal value
        self.timestamp = 0

    def debounce(self, rawin):
        #if input changed, save timestamp
        if rawin != self.out and self.timestamp == 0:
            self.timestamp = time.time()
        #if no change, reset timestamp
        elif rawin == self.out:
            self.timestamp = 0

        #evaluate when input settled to updae output
        if rawin != self.out:
            now = time.time()
            timediff = now - self.timestamp
            if rawin and timediff >= self.low_high or \
               not rawin and timediff >= self.high_low:
                self.out = rawin
        return self.out
