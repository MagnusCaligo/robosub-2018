import matplotlib
matplotlib.use('Qt4Agg')


from scipy.linalg import block_diag
from filterpy.common import Q_discrete_white_noise
from numpy.random import randn
from filterpy.kalman import KalmanFilter
from filterpy.stats import NESS
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import axes3d, Axes3D
import numpy as np

plt.interactive(False)
matplotlib.get_backend()

class Sensors():
    """
    Inputs:
        dt -> time step
        vel -> (Vx, Vy, Vz) data
    """
    def __init__(self, vel=(0, 0, 0), noise_scale=0.35):
        self.vel = vel
        self.noise_scale = noise_scale
        self.randn = randn()

    def VelSensorRead(self):
        """
        Returns noisy velocity data
        """
        vel0 = self.vel[0] + (randn() * self.noise_scale)
        vel1 = self.vel[1] + (randn() * self.noise_scale)
        vel2 = self.vel[2] + (randn() * self.noise_scale)

        return [vel0, vel1, vel2]

    def GetPosition(self, pos):
        """
        Returns position based on velocity
        """
        posX = pos[0] + self.vel[0]
        posY = pos[1] + self.vel[1]
        posZ = pos[2] + self.vel[2]
        return [posX + (self.vel[0] * randn()),
                posY + (self.vel[1] * randn()),
                posZ + (self.vel[2] * randn())]


def Simulation(pos, vel, noise_scale, count):
    """
    Runs a simulation
    :param pos: start position
    :param vel: start velocity
    :param noise_scale: how noisy is the sensor?
    :param count: number of iterations
    :return: position and velocity
    """
    sensors = Sensors(vel=vel, noise_scale=noise_scale)
    position = [pos]
    velocity = [vel]
    for x in range(count):
        if (x == 20):
            sensors.vel = (0, 2, 0)
        if (x == 40):
            sensors.vel = (0, 0, 2)
        if (x == 60):
            sensors.vel = (2, 0, 0)
        if (x == 80):
            sensors.vel = (2, 2, 0)
        position.append(sensors.GetPosition(position[x]))
        velocity.append(sensors.VelSensorRead())
    return np.vstack(position), np.vstack(velocity)

class Filter():
    """
    Sets up the Kalman filter and provides utility functions
    for the filter.
    """
    def __init__(self, dt, Q, std_vel):
        """
        Initializes the filter's variables
        :param dt: time step
        :param Q: The process noise
        :param std_vel: The measurement noise
        """
        self.ekf = KalmanFilter(dim_x=6, dim_z=3, dim_u=1)
        self.dt = dt
        self.Q = Q
        self.R_std = std_vel

    def CreateFilter(self):
        """
        Builds the Kalman filter
        """
        self.ekf.F = np.array([[1, self.dt, 0, 0, 0, 0],
                               [0, 1, 0, 0, 0, 0],
                               [0, 0, 1, self.dt, 0, 0],
                               [0, 0, 0, 1, 0, 0],
                               [0, 0, 0, 0, 1, self.dt],
                               [0, 0, 0, 0, 0, 1]])

        q = Q_discrete_white_noise(dim=3, dt=self.dt, var=self.Q**2)
        self.ekf.Q = block_diag(q, q)
        self.ekf.H = np.array([[0, 1, 0, 0, 0, 0],
                               [0, 0, 0, 1, 0, 0],
                               [0, 0, 0, 0, 0, 1]])
        self.ekf.R = np.array([[self.R_std**2, 0, 0],
                                   [0, self.R_std**2, 0],
                                   [0, 0, self.R_std**2]])
        self.ekf.x = np.array([[0, 0, 0, 2, 0, 0]]).T
        self.ekf.P = np.eye(6) * 100

    def NEES(self, xs, est_xs, ps):
        """
        Calculated the Normalized Estimated Error Squared
        :param xs: Measurements
        :param est_xs: Filter's predicted measurements
        :param ps: Filter's covariances
        :return: None
        """
        nees = NESS(xs=xs, est_xs=est_xs, ps=ps)
        eps = np.mean(nees)

        print ('mean NEES is: ', eps)
        if eps < self.ekf.dim_x:
            print ('passed')
        else:
            print ('failed')

    def TestMatrixDimensions(self):
        """
        Tests to make sure all the filter's dimensions are properly
        setup
        :return: None
        """
        self.ekf.test_matrix_dimensions(None, self.ekf.H,
                                           self.ekf.R, self.ekf.F,
                                           self.ekf.Q)

    def PrintMatrixes(self):
        print (self.ekf.F)
        print (self.ekf.Q)
        print (self.ekf.H)
        print (self.ekf.R)
        print (self.ekf.x)
        print (self.ekf.P)

    def FilterData(self, measurements):
        """
        Filters the simulated data
        :param measurements: Velocity measurements
        :return: Predicted measurements and covariance matrices
        """
        xs = []
        ps = []
        count = 0
        for z in measurements:
            count += 1
            if (count < 120):
                print (count)
                z = z.T
                z = np.expand_dims(z, axis=1)
                self.ekf.predict()
                self.ekf.update(z)
                xs.append(self.ekf.x)
                ps.append(self.ekf.P)

        return np.asarray(xs), np.asarray(ps)

'''
###################################################
######   SIMULATION     ###########################
###################################################
'''
dt = 1.0
Q = 0.04
R = 0.35

def RunSimulation():
    np.random.seed(124)
    init_pos, init_vel = (0, 0, 0), (2, 0, 0)
    count = 100
    meas_pos, meas_vel = Simulation(init_pos, init_vel, Q, count)
    fig = plt.figure(0)
    ax = Axes3D(fig)
    ax.scatter(meas_pos[:, 0], meas_pos[:, 1], meas_pos[:, 2])
    return meas_pos, meas_vel

meas_pos, meas_vel = RunSimulation()

'''
##################################################
#########  FILTER DATA ###########################
##################################################
'''
def swap_cols(arr, frm, to):
    arr[:, [frm, to]] = arr[:, [to, frm]]

filter = Filter(dt, Q, R)
filter.CreateFilter()
filter.PrintMatrixes()
filter.TestMatrixDimensions()
filt_meas, filt_conv = filter.FilterData(meas_vel)
swap_cols(filt_meas, 1, 4)
swap_cols(filt_meas, 1, 2)
filter.NEES(np.concatenate((meas_pos, meas_vel),axis=1).shape, filt_meas, filt_conv)

'''
################################################
######## PLOT MEASUREMENTS #####################
################################################
'''
fig = plt.figure(1)
ax = Axes3D(fig)
ax.scatter(filt_meas[:, 0], filt_meas[:, 1], filt_meas[:, 2],
           color='pink', marker='o', s=30)

ax.scatter(meas_pos[:, 0], meas_pos[:, 1], meas_pos[:, 2],
           color='black', marker='x', s=30)

fig = plt.figure(2)
ax = Axes3D(fig)
ax.scatter(filt_meas[:, 3], filt_meas[:, 4], filt_meas[:, 5],
           color='purple', marker='o', s=30)
ax.scatter(meas_vel[:, 0], meas_vel[:, 1], meas_vel[:, 2],
           color='black', marker='o', s=30)

plt.show()