#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:11:09 2018

@author: yuanjihuang
"""
# from IMU import IMUupdate,acc_IMUupdate
from scipy import signal
import numpy as np
import time
from guizero import App, Text, PushButton, Picture
import matplotlib.pyplot as plt
import pymongo
import datetime
import random
import string
from sensor import Sensor
from controller import PlanController
from server import run_server



def stop_func():
    global stop
    stop = 0


def finish():
    global movement_count, actual_cal

    history = {'userid': 'kunjian', 'date': str(datetime.datetime.now())[0:10],
               'movement': [movement_name], 'target': [target_count], 'count': [movement_count],
               'qualifiedrate': [100], 'target_cal': calorie, 'actual_cal': actual_cal}
    uploadTrainingSummary(history)
    data.value = 'upload finished!'
    time.sleep(1)
    data.value = ''
    current_data.value = ''
    movement_count = 0
    picture.value = 'coupon.png'


def boxing():
    global stop, fig
    stop = 1
    picture.value = 'white.png'
    sensor = Sensor(100)
    data.after(200, boxing_repeater, args=[sensor, 1000])


def boxing_repeater(sensor, hp):
    global stop
    data.value = 'hp left: ' + str(hp)
    if stop == 1 and hp > 0:
        sensor.read()
        print(sensor.acc[-1][0])
        if sensor.acc[-1][0] > 300:
            hp = hp - (sensor.acc[-1][0] - 300)
            data.value = 'punch!' + 'hp left: ' + str(hp)
        data.after(200, boxing_repeater, args=[sensor, hp])
    else:
        data.value = 'game finished!'
        stop = 0


def train_init():
    plan = getTodayTraining('kunjian')
    movement_name = plan[0]['name']
    target_count = plan[0]['unit']
    calorie = plan[0]['calorie']





def start_server():
    global status, planController, movement_num
    status,id = run_server()
    print(status)
    print(id+"ok")
    #status = 1
    #id ='kunjian@g.c'
    if status == 1:
        plan_count = 0
        planController = PlanController(id)
        movement_num = len(planController.plan)
        print(planController.plan)
        print("database controller created")
        signin_UI()


def signin_UI():
    welcome_message.hide()
    button1.update_command(show_training_plan)
    terminate_message.visible = 0
    welcome_pic.resize(200, 200)
    button1.update_command(show_training_plan)
    button1.set_text("Training")
    button2.update_command(boxing)
    button2.set_text("Boxing")
    button1.visible = 1
    button2.visible = 1

def show_training_plan():

    button1.update_command(next)
    button1.set_text("Next")
    button2.visible = 0
    welcome_pic.resize(25,25)
    #get_today_training()
    display_plan = "Today\'s Training\n"
    for item in planController.plan:
        display_plan  =  display_plan + "Movement: " + item['name'] + "    Target: " + str(item["unit"])+"\n"
    train_message.set(display_plan)
    train_message.visible = 1

def next():
    train_message.visible = 0
    training_message1.visible = 1
    button1.update_command(calibrate)
    button1.set_text("Calibrate")
    button2.update_command(start_train)
    button2.set_text("Start Training")
    training_message1.visible = 1
    calibrate_pic.visible = 1
    training_message2.visible = 1


def cal_repeater(sensor, count):
    if stop == 1:
        # print('stop is 1')
        sensor.read()
        if count == 20:
            # print(sensor.muscle[-1],sensor.acc[-1][1])
            sensor.save_csv('cali_data.csv')
            count = 0
        calibrate_pic.after(50, cal_repeater, args=[sensor, count + 1])
        # print('next round')
    else:
        name = calibrate_result()
        calibrate_pic.values = name
        print('end')


def calibrate_result():
    global y_min, y_max, muscle_max
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
    b, a = signal.butter(10, 0.2, 'low')
    f2 = signal.lfilter(b, a, list2)
    f3 = signal.lfilter(b, a, list3)
    sort_f2 = sorted(f2)
    sort_f3 = sorted(f3)
    y_min = np.mean(sort_f3[:90])
    y_max = np.mean(sort_f3[-90:])
    muscle_max = np.mean(sort_f2[-100:])

    if muscle_max > 16000:
        muscle_max = 16000
    plt.hlines(muscle_max, list1[0], list1[-1], colors="red", linestyles="dashed")
    plt.plot(list1, f2)
    a = muscle_max / (y_max - y_min)
    plt.plot(list1, f3 * a)
    plt.savefig('calibration_result.png')
    plt.clf()
    return 'calibration_result.png'


def calibrate():
    global stop
    calibrate_pic.value = 'white.png'
    sensor = Sensor(300)
    stop = 1

    training_message1.visible = 0
    training_message2.visible = 0
    calibrate_pic.visible = 0
    button2.visible = 0
    button1.update_command(finish_calibrate)
    button1.set_text("Finish")
    calibrate_message.visible = 1
    calibrate_pic.visible = 1

    calibrate_pic.after(50, cal_repeater, args=[sensor, 0])


def finish_calibrate():
    global stop,start_time
    start_time = time.time()
    stop = 0
    calibrate_message.visible = 0
    calibrate_pic.visible = 0
    button1.update_command(calibrate)
    '''
    do calibrate first
    '''
    button2.visible = 1
    training_message1.visible = 1
    calibrate_pic.visible = 1
    training_message2.visible = 1
    button1.set_text("Calibrate Again")

def start_train():
    global current_movement, current_weight, current_target_count, current_calorie, actual_calorie
    button1.visible = 0
    button2.visible = 0
    training_message1.visible = 0
    calibrate_pic.visible = 0
    training_message2.visible = 0
    current_movement = planController.plan[plan_count]['name']
    current_weight = int(planController.recommendWeight(current_movement))
    current_target_count = int(planController.plan[plan_count]['unit'])
    current_calorie = float(planController.caloriePerSet(current_movement))
    actual_cal = 0
    tem = "Current Movement:" + current_movement+ " Weight: " +str(current_weight)+  " Goal: " +\
                              str(current_target_count)+"\n"
    intermediate_message.set(tem)
    intermediate_message.visible = 1
    button1.update_command(train)
    button1.set_text("Begin")
    button1.visible = 1
    intermediate_pic.visible = 1

'''
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
    b, a = signal.butter(10, 0.3, 'low')
    f2 = signal.lfilter(b, a, list2)
    f3 = signal.lfilter(b, a, list3)
    plt.hlines(muscle_max, list1[0], list1[-1], colors="red", linestyles="dashed")
    plt.plot(list1, f2)
    a = muscle_max / (y_max - y_min)
    plt.plot(list1, f3 * a)
    plt.savefig('train_tem.png')
    plt.clf()
    return 'train_tem.png'
'''


def train_repeater(sensor, count, state, direction):
    # state: 0 mid, 1 up, -1 down
    # direction: 1 up, -1 down
    global y_min, y_max, muscle_max, movement_count, actual_cal, current_target_count,start_time
    if movement_count == current_target_count:
        skip()
    if stop == 1:
        sensor.read()
        if direction == 1:  # arm is going up
            if state == -1:  # arm was in the bottom
                if sensor.acc[-1][1] > y_min:  # arm in middle now
                    state = 0
            elif state == 0:  # arm was in the middle
                if sensor.acc[-1][1] > y_max:  # arm in top now
                    state = 1
            elif state == 1:
                if sensor.muscle[-1] > muscle_max:
                    movement_count += 1  # one movement finish
                    tem = "Current Movement:" + current_movement + " Weight: " + str(current_weight) + " Goal: "\
                          + str(movement_count)+"/" + str(current_target_count) + "\n"
                    movement_message.set(tem)
                    direction = -1
        elif direction == -1:
            if state == 1:
                if sensor.acc[-1][1] < y_max:
                    state = 0
            elif state == 0:  # arm was in the middle
                if sensor.acc[-1][1] < y_min:  # arm in top now
                    state = -1
                    direction = 1

        if count == 20:
            current_time = time.time()
            duration = int(current_time - start_time)
            accleration = abs(sensor.acc[-1][1] - sensor.acc[-3][1])
            power = 1/4 * current_weight * accleration / 3
            actual_cal = movement_count  * current_calorie
            print(sensor.muscle[-1], sensor.acc[-1][1], state, direction)
            strength = float(sensor.muscle[-1] + sensor.muscle[-2] + sensor.muscle[-3])/muscle_max/3
            # set text
            statistic_message.set("\nCalorie consumption: "+str(actual_cal)+"\nAcceleration: "+str(accleration)+" m/s^2 \nStrength: "+str(strength * 100)+"% \nPower: "+str(power)+"W\nDuration: "+str(duration)+"s \n")
            sensor.save_csv('train_data.csv')
            count = 0
        statistic_message.after(50, train_repeater, args=[sensor, count + 1, state, direction])
    else:
        print('training_end')


def train():
    global stop,plan_count
    stop = 1
    plan_count += 1
    statistic_message.set("\nCalorie consumption: 0\nAcceleration: 0 m/s^2\nStrength: 0% \nDuration: 0s \n")
    movement_message.set("Current Movement:" + current_movement + " Weight: " + str(current_weight) + " Goal: "+str(current_target_count) + "\n")
    button1.visible = 0
    button2.visible = 0
    intermediate_message.visible = 0
    intermediate_pic.visible = 0
    movement_message.visible = 1
    button1.update_command(skip)
    button1.set_text("Skip Movement")
    button1.visible = 1
    button2.update_command(terminate)
    button2.set_text("Terminate Training")
    button2.visible = 1
    movement_message.visible = 1
    statistic_message.visible = 1

    sensor = Sensor(5000)
    statistic_message.after(50, train_repeater, args=[sensor, 0, -1, 1])

def skip():
    global movement_num, stop, current_movement, current_target_count, movement_count, current_target_calorie, actual_cal, current_weight
    movement_message.visible = 0
    button2.visible = 0
    statistic_message.visible = 0
    stop=0
    planController.updateHistory(current_movement,current_target_count,movement_count,100,current_target_count*current_calorie,actual_cal, current_weight)
    actual_cal = 0
    movement_count = 0
    #if have next movement
    if plan_count < movement_num:
        start_train()
    else:
        terminate()
    #if not: call terminate
def generateCoupon(id):
    client = pymongo.MongoClient(
            "mongodb+srv://kunjian:iotproject@cluster0-ttnra.mongodb.net/test?retryWrites=true")
    mydb = client["IoTProject"]
    coupondb = mydb['Coupon']
    coupon = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
    while coupondb.find_one({'coupon': coupon}) is not None:
        coupon = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
    coupondb.insert_one({'userid': id, 'coupon': coupon})
    return coupon

def deleteLastPlan(id):
    client = pymongo.MongoClient(
            "mongodb+srv://kunjian:iotproject@cluster0-ttnra.mongodb.net/test?retryWrites=true")
    mydb = client["IoTProject"]
    trainingPlan = mydb['TrainingPlan']
    day = 0
    for plan in trainingPlan.find({'userid': id}):
        if plan['day'] > day:
            day = plan['day']
    trainingPlan.delete_many({"userid": id, 'day': day})

def terminate():
    global plan_count
    plan_count = 0
    planController.uploadTrainingHistory()
    movement_message.visible = 0
    button2.visible = 0
    button1.visible = 0
    statistic_message.visible = 0
    terminate_message.set("\n\n\nCongratulations!\nYou have finished today's training\n Coupon code: "+str(generateCoupon(planController.id))+"\nSaving progress to our database...")
    terminate_message.visible = 1
    deleteLastPlan(planController.id)
    app.after(3000, welcome)





if __name__ == "__main__":
    status = 0
    planController = None
    plan_count = 0
    stop = 0
    current_movement = ''
    current_weight = 0
    current_target_count = 0
    current_calorie = 0
    actual_cal = 0
    movement_count = 0
    movement_num = 0
    start_time = 0
    app = App(title="AI Trainer", layout="auto", bg=(239, 106, 135))
    welcome_pic = Picture(app, image="welcome.jpg", width=200, height=200)
    welcome_message = Text(app, text="Please Login on Your Phone\nto Unlock This Device", color="white", size=12)
    button1 = PushButton(app, command=start_server,text="Syncronize", width=12)
    button2 = PushButton(app, command=boxing, text="Boxing", width=12)
    button2.visible = 0

    # plan page
    train_message = Text(app, text="", color="white", size=12)
    train_message.visible = 0

    # pre-train page
    training_message1 = Text(app, text="Please calibrate before training!", color="white", size=10)
    training_message1.visible = 0
    training_message2 = Text(app,
                             text="Peak of red line determine your max strength.\nBlue line determine the range of your movement.",
                             color="white", size=10)
    training_message2.visible = 0
    calibrate_pic = Picture(app, image="button.jpg", width=200, height=150)
    calibrate_pic.visible = 0

    # calibrate
    calibrate_message = Text(app, text="Please Finish the Standard\nMovement for Three Times", color="white", size=10)
    calibrate_message.visible = 0

    # training
    movement_message = Text(app, text="", color="white", size=10)
    movement_message.visible = 0
    statistic_message = Text(app, text="\nCalorie consumption:\nAcceleration:\nStrength:\nDuration:\n", color="white",
                             size=10)
    statistic_message.visible = 0

    # intermediate
    intermediate_message = Text(app, text="Next Movement:  , Weight: , Goal:\n", color="white", size=10)
    intermediate_message.visible = 0
    intermediate_pic = Picture(app, image="button.jpg", width=200, height=150)
    intermediate_pic.visible = 0

    # terminate page
    terminate_message = Text(app,
                             text="",
                             color="white", size=10)
    terminate_message.visible = 0
    app.display()


