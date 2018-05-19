import filterpy
import numpy as np
import matplotlib.pyplot as plt

from filterpy.kalman import ExtendedKalmanFilter as efk
from scipy.stats import norm
from sympy import Symbol, symbols, Matrix, sin, cos
from sympy import init_printing

init_printing(use_latex=True)


class ExtendedKalmanFilter:
    """
    This class takes in our sensor measurements
    and feeds them through the extended kalman filter algorithm
    to get an estimation of our actual location.
    """
    """
    State Transition Function:
         X dX  Y dY  Z dZ  w dw  p  dp r  dr
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

    Initial Uncertainty (Covariance matrix)
        [1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        [0, 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 1000, 0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 1000, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 1000, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 1000, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 1000, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0, 1000, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1000, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1000, 0]
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1000]


    Measurement Function
        [


    """
    def __init__(self, location):
        self.x = [location[0], location[1], location[2], location[3], location[4],
                  location[5], location[6], location[7], location[8], location[9],
                  location[10], location[11]]  # measurements [x, y, z, dx, dy, dz, yaw, pitch, roll, dyaw, dpitch, droll]
        self.numStates = 12  # Number of states we are going to track
        self.dvlData, self.ahrsData, self.pressTrans = [], [], []
        self.dt = 1.0 / 50.0  # Sample rate of the measurements
        self.dtAHRS = 1.0 / 10.0  # Sample rate of the dvl

        # Setup sympy symbols
        self.vs, self.psis, self.dpsis, self.dts, self.xs, self.ys, self.lats, self.lons = symbols(
            'v \psi \dot\psi T x y lat lon')

        # Used to compute the predicted state from the previous estimate and similarly the function h can be
        # used to compute the predicted measurement from the predicted state.  However, we must find the
        # partial derivates (Jacobian matrix) of g and h.
        self.gs = Matrix([[self.xs],
                          [self.ys],
                          [self.psis],
                          [self.vs],
                          [self.dpsis]])

        # State Transition Function
        self.state = Matrix([self.xs, self.ys, self.psis, self.vs, self.dpsis])
        self.js = self.gs.jacobian(self.state)

        # Initial uncertainty (Covariance Matrix)
        self.P = np.diag([1000.0, 1000.0, 1000.0, 1000.0, 1000.0])

        # Process Noise Covariance Matrix
        # The state uncertainty model models the disturbances which excite the linear system. It estimates
        # how bad things can get when the system is run open loop for a given period of time.
        self.sGPS = 0.5 * 8.8 * self.dt ** 2  # maximum acceleration, forcing the vehicle
        self.sCourse = 0.1 * self.dt  # maximum turn rate of the vehicle
        self.sVelocity = 8.8 * self.dt  # Maximum acceleration
        self.sYaw = 1.0 * self.dt  # Maximum turn rate acceleration
        #                      X             Y             Yaw               V                dYaw
        self.Q = np.diag([self.sGPS ** 2, self.sGPS ** 2, self.sCourse ** 2, self.sVelocity ** 2, self.sYaw ** 2])

        # Measurement Function h. Matrix JHs is the Jacobian of h.  Function h is used to computer the
        # predicted measurement from the predicted state
        self.hs = Matrix([[self.xs],
                          [self.ys],
                          [self.vs],
                          [self.dpsis]])
        self.JHS = self.hs.jacobian(self.state)

        # Measurement noise covariance
        # Initialize to take on the significance of relative weights of state estimates and measurements
        self.varGPS = 6.0  # Standard deviation of GPS measurement
        self.varSpeed = 1.0  # Variance of speed measurement
        self.varYaw = 0.1  # Variance of the yawrate measurement
        self.R = np.matrix([[self.varGPS ** 2, 0.0, 0.0, 0.0],
                            [0.0, self.varGPS ** 2, 0.0, 0.0],
                            [0.0, 0.0, self.varSpeed ** 2, 0.0],
                            [0.0, 0.0, 0.0, self.varYaw ** 2]])

        # Identity matrix
        self.I = np.eye(self.numStates)

        # Control input matrix
        self.U = 0

    def predict(self):
        """
        Time update/Prediction
        Project the state ahead
        :return: Predicted measurements
        """
        # Project the error covariance ahead
        self.P = self.js * self.P * self.js.T + self.Q

    def update(self):
        """
        Measurement update (Correction)
        :return:
        """
        S = self.JHS * self.P * self.JHS.T + self.R
        K = (self.P * self.JHS.T) * np.linalg.inv(S)

        # Update the estimate
        Z = self.x.reshape(self.JHS.shape[0], 1)
        y = Z - self.hs
        self.x += (K * y)

        # Update the error convariance
        self.P = (self.I - (K * self.JHS)) * self.P

    def showCovariance(self):
        """
        Shows the covariance matrix.
        :return:
        """
        fig = plt.figure(figsize=(5, 5))
        im = plt.imshow(self.P, interpolation="none", cmap=plt.get_cmap('binary'))
        plt.title('Initial Covariance Matrix $P$')
        ylocs, ylabels = plt.yticks()
        # set the locations of the yticks
        plt.yticks(np.arange(6))
        # set the locations and labels of the yticks
        plt.yticks(np.arange(5), ('$x$', '$y$', '$\psi$', '$v$', '$\dot \psi$'), fontsize=22)

        xlocs, xlabels = plt.xticks()
        # set the locations of the yticks
        plt.xticks(np.arange(6))
        # set the locations and labels of the yticks
        plt.xticks(np.arange(5), ('$x$', '$y$', '$\psi$', '$v$', '$\dot \psi$'), fontsize=22)

        plt.xlim([-0.5, 4.5])
        plt.ylim([4.5, -0.5])

        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(plt.gca())
        cax = divider.append_axes("right", "5%", pad="3%")
        plt.colorbar(im, cax=cax)

        plt.tight_layout()

def main():
    ekf = ExtendedKalmanFilter()
    print (efk.state)
    print (ekf.js)


main()

'''
from filterpy.kalman import UnscentedKalmanFilter as UKF
from filterpy.kalman import unscented_transform, MerweScaledSigmaPoints
from filterpy.common import Q_discrete_white_noise

class UnscentedKalmanFilter:
    """
    Implements the unscented kalman filter
    to track the state of the submarine.
    """
    def __init__(self, location):
        self.dt = 1.0
        self.wheelbase = 0.5

        self.points = MerweScaledSigmaPoints(n=3, alpha=.00001, beta=2, kappa=0,
                                             subtract=self.residual_x)
        self.ukf = UKF(dim_x=3, dim_z=2, fx=self.fx, hx=self.Hx,
                  dt=self.dt, points=self.points, x_mean_fn=self.state_mean,
                  z_mean_fn=self.z_mean, residual_x=self.residual_x,
                  residual_z=self.residual_h)

        self.ukf.x = np.array([2, 6, .3])
        self.ukf.P = np.diag([.1, .1, .05])
        self.ukf.R = np.diag()
        self.ukf.Q = np.eye(3) * 0.0001
        self.u = 0
        self.z = 0

    def predict(self):
        self.ukf.predict(fx_args=self.u)

    def update(self):
        self.ukf.update(self.z)

    def state_mean(self, sigmas, Wm):
        pass

    def z_mean(self, sigmas, Wm):
        pass

    def fx(self):
        pass

    def hx(self):
        pass

    def residual_x(self):
        pass

    def residual_h(self):
        pass

'''
