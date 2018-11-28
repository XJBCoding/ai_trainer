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
import pymongo
import datetime
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
                    data.value = 'movement complete! count: '+str(movement_count)+'/'+str(target_count)
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
            data.value = 'count: '+str(movement_count)+'/'+str(target_count)
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
    
def generatePlan(id):
    global mydb
    movement_num = 1
    profile = mydb['Profile']
    movements = mydb['Movements']
    trainingplan = mydb["TrainingPlan"]
    target = profile.find_one({"userid": id})["target"]
    muscles = ["chest", "back", "biceps", "triceps", "shoulder", "quadricep", "hamstring"]
    day = 0
    for muscle in muscles:
        day += 1
        muscle_move = list()
        for movement in movements.find({'type': target, 'muscle': muscle}):
            muscle_move.append(movement["name"])
        selection = random.sample(range(len(muscle_move)), movement_num)
        for i in selection:
            mov_name = muscle_move[i]
            mov_unit = movements.find_one({'name': mov_name})["unit"]
            mov_calorie = movements.find_one({'name': mov_name})["calorie"]
            trainingplan.insert_one({'userid': id, 'day': day, 'name': mov_name, 'type': target, 'muscle': muscle,
                                     'unit': mov_unit, 'calorie': mov_calorie})

# The return object is a list of dictionaries, dictionaries' structure is the same as that in mongoDB
def getTodayTraining(id):
    global mydb
    day = 0
    trainingplan = mydb["TrainingPlan"]

    if trainingplan.find_one({'userid': id}) is None:
        generatePlan(id)

    for plan in trainingplan.find({'userid': id}):
        if plan['day'] > day:
            day = plan['day']

    temp_plan = list()
    for movement in trainingplan.find({'userid': id, 'day':day}):
        temp_plan.append(movement)
    return temp_plan

def uploadTrainingSummary(history):
    global mydb
    traininghistory = mydb["TrainingHistory"]
    traininghistory.insert_one(history)
def finish():
    actual_cal = (movement_count/target_count) * calorie
    history = {'userid':'kunjian','date':str(datetime.datetime.now())[0:10],
               'movement':[movement_name],'target':[target_count],'count':[movement_count],
               'qualifiedrate':[100],'target_cal':calorie,'actual_cal':actual_cal}
    uploadTrainingSummary(history)
    
if __name__ == "__main__":
    client = pymongo.MongoClient("mongodb+srv://kunjian:iotproject@cluster0-ttnra.mongodb.net/test?retryWrites=true")
    mydb = client["IoTProject"]
    plan = getTodayTraining('kunjian')
    movement_name = plan[0]['name']
    target_count = plan[0]['unit']
    calorie = plan[0]['calorie']
    app = App(title="AI Trainer",layout="grid",bg=(255,204,204))
    welcome_message = Text(app, text='Current movement:'+movement_name, grid=[0,0,6,1],size=20)
    calibrate = PushButton(app, command=calibrate, text="Calibrate",width = 12, grid=[1,1])
    train = PushButton(app, command=train, text="Train", grid=[2,1])
    stop_btn = PushButton(app, command=stop_func, text="Stop", grid=[4,1])
    finish_btn = PushButton(app, command=finish , text="Finish",width = 12, grid=[5,1])
    stop = 0
    y_min = 0
    y_max = 0
    movement_count = 0
    muscle_max = 0
    data = Text(app, text = "", grid=[0,2,6,1],size=20)
    picture = Picture(app, image="white.png",width=500,height=250, grid=[0,3,6,1])
    app.display()
    

