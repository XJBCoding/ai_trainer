#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:11:09 2018

@author: yuanjihuang
"""
from guizero import App,Text,PushButton
import Adafruit_ADS1x15
import Adafruit_ADXL345

def reader(i):
    global stop
    if stop == 1:
        data.value = i
        data.after(500,reader,args = [i+1])
    else:
        data.value = 'success!'
def calibrate():
    global stop
    stop = 1
    data.after(500,reader,args = [1])
def train():
    pass
def stop_func():
    global stop
    stop = 0
if __name__ == "__main__":
    adc = Adafruit_ADS1x15.ADS1115(address = 0x48)
    acel = Adafruit_ADXL345.ADXL345(address = 0x53)
    app = App(title="AI Trainer")
    welcome_message = Text(app, text="Please choose mode")
    calibrate = PushButton(app, command=calibrate, text="Calibrate")
    train = PushButton(app, command=train, text="Train")
    stop_btn = PushButton(app, command=stop_func, text="stop")
    stop = 0
    data = Text(app, text="")
    app.display()
    '''while True:
        
        values = adc.read_adc(0, gain=1)
        x,y,z = acel.read()
        #gyro = adafruit_l3gd20.L3GD20_I2C(i2c)
        print(values)
        print('x={0},y={1},z={2}'.format(x,y,z))
        #print(gyro.gyro)
        # Pause for half a second.
        time.sleep(0.3)'''

