#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:11:09 2018

@author: yuanjihuang
"""
import csv
import Adafruit_ADS1x15
import Adafruit_ADXL345


class Sensor:
    def __init__(self, max_len=20):
        self.adc = Adafruit_ADS1x15.ADS1115(address=0x48)
        self.acel = Adafruit_ADXL345.ADXL345(address=0x53)
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
        # add time
        self.cur_time += 1
        self.time.append(self.cur_time)
        # add muscle
        a = self.adc.read_adc(0, gain=(2 / 3))
        self.muscle.append(a)
        # add acc
        x, y, z = self.acel.read()
        self.acc.append((x, y, z))
        # check length
        self.check_len()

    def save_csv(self, name):
        # print(self.cur_time)
        with open(name, 'w') as output:
            writer = csv.writer(output, delimiter=',', lineterminator='\n')
            for i in range(len(self.muscle)):
                writer.writerow([self.time[i], self.muscle[i], self.acc[i][0],\
                                 self.acc[i][1], self.acc[i][2]])
