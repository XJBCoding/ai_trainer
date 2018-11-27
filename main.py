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
        a = self.adc.read_adc(0, gain=(2/3))
        print(a)
        self.muscle.append(a)
        #add acc
        x,y,z = self.acel.read()
        self.acc.append((x,y,z))
        #check length
        #print(self.muscle,self.acc)
        self.check_len()
        return (self.muscle, self.acc)
    
    def save_csv(self):
        print(self.cur_time)
        with open('data.csv','w') as output:
            writer = csv.writer(output, delimiter = ',', lineterminator = '\n')
            for i in range(len(self.muscle)):  
                writer.writerow([self.time[i],self.muscle[i],self.acc[i][0],self.acc[i][1],self.acc[i][2]])
            
    def create_image(self):
        plt.figure()
        plt.subplot(111)
        plt.plot(self.muscle)
        #plt.subplot(122)
        #plt.plot(self.acc[0])
        
        plt.savefig('tem.png')
        #plt.close()
        #print('image created!')
        #print(self.muscle)
        return 'tem.png'
        
    
def repeater(sensor,count):
    if stop == 1:
        #print('stop is 1')
        sensor.read()
        if count == 20:
            sensor.save_csv()
            count = 0
        picture.after(50,repeater,args=[sensor,count+1])
        #print('next round')
    else:
        name = sensor.create_image()
        picture.value = name 
        print('end')

'''def data_repeater(sensor):
    global stop
    if stop == 1:+
    -
        #print('stop is 1')
        muscle,acc = sensor.read()
        data.value = str(muscle)
        data.after(1000,data_repeater,args=[sensor])
        #print('next round')
    else:
        print('data_end')'''
        
        
def calibrate():
    global stop,fig
    picture.value = 'white.png'
    fig = plt.figure()
    sensor = Sensor(300)
    stop = 1
    
    #data.after(500,data_repeater,args=[sensor])
    picture.after(50,repeater,args=[sensor,0])
    
def train():
    pass
def stop_func():
    global stop
    stop = 0
    
def animate(i):
    ftemp = 'data.csv'
    fh = open(ftemp)
    x = []
    y = []
    for line in fh:
        pieces = line.split(',')
        time = pieces[0]
        muscle = pieces[1]
        x.append(time)
        y.append(muscle)
        #print(x,y)
        ax1 = fig.add_subplot(1,1,1,axisbg='white')
        ax1.clear()
        ax1.plot(x,y)
        
    
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
    

