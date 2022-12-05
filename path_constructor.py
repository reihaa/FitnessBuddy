import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from ahrs.filters import Madgwick
from ahrs.common.orientation import acc2q
from ahrs.utils import WMM
from scipy.spatial.transform import Rotation as R
from scipy import integrate


df = pd.read_csv("data/data_5.csv")
# time, acc[1:4], gyro[4:7]
data = df.to_numpy()

time = (data[:, 0] / 1000)

madgwick = Madgwick(gyr=data[:, 4:7], acc=data[:, 1:4])


n_samples = time.shape[0]
new_acce = np.zeros((n_samples, 3))

for t in range(n_samples):
    r = R.from_quat(madgwick.Q[t])
    # Getting a Rotation Matrix from the Quaternions
    new_acce[t] = np.matmul(r.as_matrix().T, data[t][1:4])


vel_x = integrate.cumtrapz(new_acce[:, 0], time, initial=0)
vel_y = integrate.cumtrapz(new_acce[:, 1], time, initial=0)
vel_z = integrate.cumtrapz(new_acce[:, 2], time, initial=0)
print (vel_x, len(time))
pos_x = integrate.cumtrapz(vel_x, time, initial=0)
pos_y = integrate.cumtrapz(vel_y, time, initial=0)
pos_z = integrate.cumtrapz(vel_z, time, initial=0)


fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot3D(pos_x, pos_y, pos_z)
fig.show()
