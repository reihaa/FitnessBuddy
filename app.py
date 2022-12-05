import customtkinter
import socket
from ast import literal_eval
import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy import integrate

import imufusion
import matplotlib.pyplot as plt

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("400x240")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
acc_bias = np.array([0.01732761, 0.04202371, 10.56737618])

# def calibrate():
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect(("192.168.4.1", 80))
#     global madgwick
#     acc_arr = []
#     gyro_arr = []
#     time_arr = []
#     res = ""
#     ahrs_im = imufusion.Ahrs()
#
#     try:
#         for _ in range(100):
#             read = client.recv(1024)
#             if read == b'':
#                 break
#             res = res + str(read)[2:-1]
#             while res.find("))") != -1:
#                 index = res.find("))") + 2
#                 timestamp, acc, gyr = literal_eval(res[0: index])
#                 res = res[index:]
#                 acc = np.array(acc) * 10
#
#                 ahrs_im.update_no_magnetometer(np.array(gyr), np.array(acc), 1/100)
#                 quater = ahrs_im.quaternion.to_matrix()
#                 new_acc = np.matmul(quater, acc)
#
#                 time_arr.append(timestamp / 1000)
#                 acc_arr.append(np.array(new_acc))
#                 gyro_arr.append(np.array(gyr))
#
#         global acc_bias
#         acc_bias = np.average(acc_arr, axis=0)
#         print("bias", acc_bias)
#     except RuntimeError as e:
#         print("some error happened", e)
#     finally:
#         client.close()
#         print("Calibration Done")


def connect():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.4.1", 80))

    speed = np.zeros(3)
    height = 0
    time = None
    res = ""
    sample_rate = 1000
    offset = imufusion.Offset(sample_rate)
    ahrs = imufusion.Ahrs()
    ahrs.settings = imufusion.Settings(0.5,  # gain
                       10,  # acceleration rejection
                       0,  # magnetic rejection
                       5 * sample_rate)
    moving_up = 1
    try:
        for _ in range(sample_rate):
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
                gyr = offset.update(gyr)

                if time is None:  # Initial values, can not calculate speed and location from them
                    time = timestamp
                    continue

                delta_time = timestamp - time
                time = timestamp

                ahrs.update_no_magnetometer(gyr, acc, delta_time)
                new_acce = ahrs.earth_acceleration

                is_moving = np.linalg.norm(new_acce) > 0.5 # one meter / s2

                if not is_moving:
                    continue

                if (moving_up == 1 and new_acce[2] > 0) or (moving_up == 0 and new_acce[2] < 0):
                    speed = np.zeros(3)
                    moving_up = 1 - moving_up

                height += speed[2] + delta_time * speed[2]
                speed = speed + delta_time * new_acce

                print(height)

    except RuntimeError as e:
        print("some error happened", e)
    finally:
        client.close()


def disconnect():
    client.close()


# Use CTkButton instead of tkinter Button
# calibrate_button = customtkinter.CTkButton(master=app, text="Calibrate", command=calibrate)
# calibrate_button.place(relx=0.5, rely=0.3, anchor=customtkinter.CENTER)

connection_button = customtkinter.CTkButton(master=app, text="Connect", command=connect)
connection_button.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
disconnect_button = customtkinter.CTkButton(master=app, text="Disconnect", command=disconnect)
disconnect_button.place(relx=0.5, rely=0.7, anchor=customtkinter.CENTER)

app.mainloop()
