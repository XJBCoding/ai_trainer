#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:11:09 2018

@author: yuanjihuang
"""
from guizero import App,Text,PushButton,Picture
import Adafruit_ADS1x15
import Adafruit_ADXL345
import matplotlib as plt

class Sensor:
    def __init__(self,max_len):
        self.adc = Adafruit_ADS1x15.ADS1115(address = 0x48)
        self.acel = Adafruit_ADXL345.ADXL345(address = 0x53)   
        self.cur_time = 0
        self.time = [0]
        self.muscle = []
        self.acc = []   
        self.max_len = max_len
    def check_len(self):
        if len(self.time) > self.max_len:
            self.time.pop(0)
        if len(self.muscle) > self.max_len:
            self.muscle.pop(0)
        if len(self.acc) > self.max_len:
            self.acc.pop(0)
    def read(self):
        #add time
        self.cur_time += 1
        self.time.append(self.cur_time)
        #add muscle
        self.muscle.append(self.adc.read_adc(0, gain=1))
        #add acc
        x,y,z = self.acel.read()
        self.acc.append((x,y,z))
        #check length
        self.check_len()
    def create_image(self):
        self.read()
        plt.figure()
        plt.plot(self.muscle)
        plt.savefig('tem.png')
        plt.close()
        return 'tem.png'
    
def repeater(sensor):
    if stop == 1:
        fig_name = sensor.create_image()
        picture.image = fig_name
        picture.after(500,repeater,args=[sensor])
    else:
        print('end')
        
def calibrate():
    global stop
    sensor = Sensor()
    stop = 1
    picture.after(500,repeater,args=[sensor])
    
def train():
    pass
def stop_func():
    global stop
    stop = 0
    
if __name__ == "__main__":
    plt.ioff()
    app = App(title="AI Trainer")
    welcome_message = Text(app, text="Please choose mode")
    calibrate = PushButton(app, command=calibrate, text="Calibrate")
    train = PushButton(app, command=train, text="Train")
    stop_btn = PushButton(app, command=stop_func, text="stop")
    stop = 0
    picture = Picture(app, image="")
    app.display()
    

