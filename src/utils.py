import random
from time import sleep

def randmized_sleep(average=1):
    _min, _max = average * 1 / 2, average * 3 / 2
    sleep(random.uniform(_min, _max))
