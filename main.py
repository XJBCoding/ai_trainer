#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:11:09 2018

@author: yuanjihuang
"""
from guizero import App,Text,PushButton
import Adafruit_ADS1x15

def
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
    
app = App(title="AI Trainer")
welcome_message = Text(app, text="Please choose mode")
calibrate = PushButton(app, command=calibrate, text="Calibrate")
train = PushButton(app, command=train, text="Train")
stop_btn = PushButton(app, command=stop_func, text="stop")
stop = 0
data = Text(app, text="")
app.display()
