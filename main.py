#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:11:09 2018

@author: yuanjihuang
"""

from scipy import signal
import numpy as np
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
        self.muscle.append(a)
        #add acc
        x,y,z = self.acel.read()
        self.acc.append((x,y,z))
        #check length
        #print(self.muscle,self.acc)
        self.check_len()
        return (self.muscle, self.acc)
    
    def save_csv(self,name):
        #print(self.cur_time)
        with open(name,'w') as output:
            writer = csv.writer(output, delimiter = ',', lineterminator = '\n')
            for i in range(len(self.muscle)):  
                writer.writerow([self.time[i],self.muscle[i],self.acc[i][0],self.acc[i][1],self.acc[i][2]])
        
        
        
def calibrate_result():
    global y_min,y_max,muscle_max
    ftemp = 'cali_data.csv'
    fh = open(ftemp)
    list1 = []
    list2 = []
    list3 = []
    for line in fh:
        pieces = line.split(',')
        time = pieces[0]
        muscle = pieces[1]
        axis_y = pieces[3]
        list1.append(int(time))
        list2.append(int(muscle))
        list3.append(int(axis_y))
    b,a = signal.butter(10,0.2,'low')
    f2 = signal.lfilter(b,a,list2)
    f3 = signal.lfilter(b,a,list3)
    sort_f2 = sorted(f2)
    sort_f3 = sorted(f3)
    y_min = np.mean(sort_f3[:90])
    y_max = np.mean(sort_f3[-90:])
    muscle_max = np.mean(sort_f2[-100:])
    
    if muscle_max > 16000:
        muscle_max = 16000
    plt.hlines(muscle_max, list1[0], list1[-1], colors = "red", linestyles = "dashed")
    plt.plot(list1,f2)
    a = muscle_max / (y_max-y_min)
    plt.plot(list1,f3*a)
    plt.savefig('tem.png')
    print(y_min,y_max,muscle_max)
    plt.clf()
    return 'tem.png'

def train_result():
    ftemp = 'train_data.csv'
    fh = open(ftemp)
    list1 = []
    list2 = []
    list3 = []    
    for line in fh:
        pieces = line.split(',')
        time = pieces[0]
        muscle = pieces[1]
        axis_y = pieces[3]
        list1.append(int(time))
        list2.append(int(muscle))
        list3.append(int(axis_y))
    b,a = signal.butter(10,0.3,'low')
    f2 = signal.lfilter(b,a,list2)
    f3 = signal.lfilter(b,a,list3)
    plt.hlines(muscle_max, list1[0], list1[-1], colors = "red", linestyles = "dashed")
    plt.plot(list1,f2)
    a = muscle_max / (y_max-y_min)
    plt.plot(list1,f3*a)
    plt.savefig('train_tem.png')
    plt.clf()
    return 'train_tem.png'

def repeater(sensor,count):
    if stop == 1:
        #print('stop is 1')
        sensor.read()
        if count == 20:
            print(sensor.muscle[-1],sensor.acc[-1][1])
            sensor.save_csv('cali_data.csv')
            count = 0
        picture.after(50,repeater,args=[sensor,count+1])
        #print('next round')
    else:
        data.value = 'generating result...'
        name = calibrate_result()
        data.value = 'Ready for training!'
        picture.value = name 
        print('end')
        
        
def calibrate():
    global stop,fig
    picture.value = 'white.png'
    fig = plt.figure()
    data.value = 'start calibration!'
    sensor = Sensor(300)
    stop = 1
    
    #data.after(500,data_repeater,args=[sensor])
    picture.after(50,repeater,args=[sensor,0])
 
    
    
def train_repeater(sensor,count,state,direction):
    
    # state: 0 mid, 1 up, -1 down
    # direction: 1 up, -1 down
    global y_min,y_max,muscle_max,movement_count
    if stop == 1:
        sensor.read()
        if direction == 1: # arm is going up
            if state == -1: # arm was in the bottom
                if sensor.acc[-1][1] > y_min: # arm in middle now
                    state = 0
            elif state == 0: # arm was in the middle
                if sensor.acc[-1][1] > y_max: #arm in top now
                    state = 1
            elif state == 1:
                if sensor.muscle[-1] > muscle_max:
                    movement_count += 1 # one movement finish
                    data.value = 'movement complete! count: '+str(movement_count)
                    direction = -1
        elif direction == -1:
            if state == 1:
                if sensor.acc[-1][1] < y_max:
                    state = 0
            elif state == 0: # arm was in the middle
                if sensor.acc[-1][1] < y_min: #arm in top now
                    state = -1
                    direction = 1

        if count == 20:
            print(sensor.muscle[-1],sensor.acc[-1][1],state,direction)
            data.value = 'count: '+str(movement_count)
            sensor.save_csv('train_data.csv')
            count = 0
        
        picture.after(50,train_repeater,args=[sensor,count+1,state,direction])
        #print('next round')
    else:
        name = train_result()
        picture.value = name 
        print('training_end')
        
        
def train():
    global stop,fig
    stop = 1
    picture.value = 'white.png'
    sensor = Sensor(5000)
    data.after(50,train_repeater,args=[sensor,0,-1,1])
    
    
    
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
    y_min = 0
    y_max = 0
    movement_count = 0
    muscle_max = 0
    data = Text(app, text = "")
    picture = Picture(app, image="white.png",width=500,height=250)
    app.display()
    

