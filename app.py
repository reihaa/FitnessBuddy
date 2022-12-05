import threading
import socket
from ast import literal_eval
import numpy as np
import imufusion
import tkinter as tk


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
acc_bias = np.array([0.01732761, 0.04202371, 10.56737618])

ahrs = imufusion.Ahrs()
is_started = False
calibration = False


def start():
    global is_started, canvas, circle
    time = None
    res = ""
    try:
        while is_started:
            read = client.recv(1024)
            if read == b'':
                break
            res = res + str(read)[2:-1]
            while res.find("))") != -1:
                index = res.find("))") + 2
                timestamp, acc, gyr = literal_eval(res[0: index])
                acc = np.array(acc)
                gyr = np.array(gyr)
                res = res[index:]
                timestamp = timestamp / 1000

                if time is None:  # Initial values, can not calculate speed and location from them
                    time = timestamp
                    continue

                delta_time = timestamp - time
                time = timestamp

                ahrs.update_no_magnetometer(gyr, acc, delta_time)
                euler = ahrs.quaternion.to_euler()

                if calibration:
                    if -180 <= euler[0] <= -170 or -180 <= euler[0] <= -170:
                        print('Calibrated')
                        is_started = False
                else:
                    location = -1 * np.sin(euler[0] * np.pi / 180.)
                    x = 20
                    y = (image_height - 45) - (20 + location * (image_height - 100))
                    canvas.coords(circle, x, y, x + size, y+size)

    except RuntimeError as e:
        print("some error happened", e)
    finally:
        client.close()


def calibrate():
    global client, is_started, calibration
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.4.1", 80))
    is_started = True
    calibration = True
    tread = threading.Thread(target=start)
    tread.start()


def connect():
    global client, is_started, calibration
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.4.1", 80))
    is_started = True
    calibration = False
    tread = threading.Thread(target=start)
    tread.start()


def disconnect():
    global is_started
    is_started = False


root = tk.Tk()
root.title("FitnessBuddy!")
canvas = tk.Canvas(root, width=270, height=284)
canvas.pack()

# create a circle on the canvas
image = tk.PhotoImage(file="image.png")
image_width, image_height = image.width(), image.height()
image_id = canvas.create_image(image_width // 2, image_height // 2, image=image)
x, y, size = 20, image_height - 65, 30
circle = canvas.create_oval(x, y, x + size, y + size, fill="red")


move_button = tk.Button(root, text="Calibrate", command=calibrate)
move_button.pack()

color_button = tk.Button(root, text="Start", command=connect)
color_button.pack()

clear_button = tk.Button(root, text="Stop", command=disconnect)
clear_button.pack()


def move_image():
    global is_started, calibration
    if is_started and not calibration:
        if canvas.coords(image_id)[0] <= -image_width // 2 + 280:
            print("Done!")
            is_started = False
        canvas.move(image_id, -5, 0)
    canvas.after(35, move_image)


canvas.after(50, move_image)

# start the main loop
root.mainloop()
