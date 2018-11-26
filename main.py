#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:11:09 2018

@author: yuanjihuang
"""
from guizero import App,Text,PushButton
import Adafruit_ADS1x15
import Adafruit_ADXL345


class Sensor:
    def __init__(self):
        self.adc = Adafruit_ADS1x15.ADS1115(address = 0x48)
        self.acel = Adafruit_ADXL345.ADXL345(address = 0x53)   
    def read(self):
        muscle = self.adc.read_adc(0, gain=1)
        x,y,z = self.acel.read()
        return (muscle,x,y,z)
    
    
def repeater():
    if stop == 1:
        muscle,x,y,z = sensor.read()
        data.value = ('muscle={0},x={1},y={2},z={3}'.format(muscle,x,y,z))
        data.after(500,repeater)
    else:
        data.value = 'success!'
        
def calibrate():
    global stop
    stop = 1
    data.after(500,repeater)
    
def train():
    pass
def stop_func():
    global stop
    stop = 0
    
if __name__ == "__main__":
    sensor = Sensor()
    muscle,x,y,z = sensor.read()
    app = App(title="AI Trainer")
    welcome_message = Text(app, text="Please choose mode")
    calibrate = PushButton(app, command=calibrate, text="Calibrate")
    train = PushButton(app, command=train, text="Train")
    stop_btn = PushButton(app, command=stop_func, text="stop")
    stop = 0
    data = Text(app, text="")
    app.display()
    

