from m5stack import *
from m5ui import *
from uiflow import *
import network
from imu import IMU

im0 = IMU()

try:
    import usocket as socket
except:
    import socket

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='FitnessBuddy')
ap.config(authmode=3, password='123456789')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('192.168.4.1', 80))
s.listen(5)

while True:
    lcd.clear()
    lcd.print("Waiting for connection", 0, 0)

    conn, addr = s.accept()
    try:
        lcd.clear()
        lcd.print("Sending data", 0, 0)

        while True:
            data = str((time.ticks_ms(), im0.acceleration, im0.gyro))
            conn.sendall(data)
    except:
        pass

    conn.close()