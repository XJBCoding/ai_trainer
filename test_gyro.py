import board
import busio
import time
import adafruit_l3gd20
i2c = busio.I2C(board.SCL,board.SDA)
l3gd20 = adafruit_l3gd20.L3GD20_I2C(i2c)
while True:
    print(l3gd20.gyro)
    time.sleep(0.5)
