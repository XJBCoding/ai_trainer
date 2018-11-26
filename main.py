#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:11:09 2018

@author: yuanjihuang
"""
import time
import csv
from guizero import App,Text,PushButton,Picture
import Adafruit_ADS1x15
import Adafruit_ADXL345
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Sensor:
    def __init__(self,max_len = 20):
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
        #print(self.muscle,self.acc)
        self.check_len()
        return (self.muscle, self.acc)
    
    def save_csv(self):
        with open('data.csv','a') as output:
            writer = csv.writer(output, delimiter = ',', lineterminator = '\n')
            writer.writerow([self.muscle,self.acc[0],self.acc[1],self.acc[2]])
            
    def create_image(self):
        plt.figure()
        plt.plot(self.muscle)
        plt.savefig('tem.png')
        plt.close()
        #print('image created!')
        #print(self.muscle)
        return 'tem.png'
    
def repeater(sensor):
    if stop == 1:
        #print('stop is 1')
        sensor.read()
        sensor.save_csv()
        picture.after(200,repeater,args=[sensor])
        #print('next round')
    else:
        print('end')

def data_repeater(sensor):
    global stop
    if stop == 1:
        #print('stop is 1')
        muscle,acc = sensor.read()
        data.value = str(muscle)
        data.after(1000,data_repeater,args=[sensor])
        #print('next round')
    else:
        print('data_end')
        
        
def calibrate():
    global stop
    sensor = Sensor(100)
    stop = 1
    #data.after(500,data_repeater,args=[sensor])
    picture.after(50,repeater,args=[sensor])
    
def train():
    pass
def stop_func():
    global stop
    stop = 0
    
if __name__ == "__main__":
    app = App(title="AI Trainer")
    welcome_message = Text(app, text="Please choose mode")
    calibrate = PushButton(app, command=calibrate, text="Calibrate")
    train = PushButton(app, command=train, text="Train")
    stop_btn = PushButton(app, command=stop_func, text="stop")
    stop = 0
    data = Text(app, text = "123")
    picture = Picture(app, image="white.png",width=300,height=250)
    app.display()
    

