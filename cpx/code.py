from time import sleep
from adafruit_circuitplayground import cp

LIGHT_SENS = 225  # Light reading that would = brightness 1 if allowed.
MIN_BRIGHT = 0.01
MAX_BRIGHT = 0.5
SMOOTHNESS = 0.1

current_bright = MIN_BRIGHT


class LightLevel:
    # If only CPX supported deque :(
    def __init__(self, number_checks):
        self.checks = number_checks
        self.total = 0
        self.count = 0
        self.index = 0
        self.buffer = [0] * number_checks

    def get_avg(self, light):
        self.total -= self.buffer[self.index]
        self.buffer[self.index] = light
        self.total += light
        self.index += 1
        self.index = self.index % self.checks
        if self.count < self.checks:
            self.count += 1
        self.avg = self.total / self.count
        return self.avg


light_level = LightLevel(10)


def get_next_bright(current, light):
    target_bright = max(MIN_BRIGHT, min(light / LIGHT_SENS, MAX_BRIGHT))
    step = (target_bright - current) * SMOOTHNESS
    current += step
    return current


for i in range(1, 10, 2):
    tint = (i * 1234) % 256
    cp.pixels[i] = (tint, 150, 0)

while True:
    light_level_avg = light_level.get_avg(cp.light)
    cp.pixels.brightness = current_bright
    current_bright = get_next_bright(current_bright, light_level_avg)
    sleep(0.2)
