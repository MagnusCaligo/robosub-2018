import numpy as np
from math import tan, sin, cos, sqrt


class BicycleModelSim:
    """
    Creates a simulation of the submarine going in a circle.
    The simulation will output ground truth and sensor data
    for six degrees of freedom.
    """
    def __init__(self, count):
        self.pos = [[0, 0, 0]]
        self.rot = [[0, 0, 0]]
        self.posVel = [[2, 0, 0]]
        self.rotVel = [[0.1, 0, 0]]
        self.dvlNoise = 0.01 # 1 cm/s
        self.ahrsNoise = 1 # 1 degree/s
        self.count = count

    def move(self, x, u, dt, wheelbase):
        hdg = x[2]
        vel = u[0]
        steering_angle = u[1]
        dist = vel * dt

        if abs(steering_angle) > 0.001:  # is robot turning?
            beta = (dist / wheelbase) * tan(steering_angle)
            r = wheelbase / tan(steering_angle)  # radius

            sinh, sinhb = sin(hdg), sin(hdg + beta)
            cosh, coshb = cos(hdg), cos(hdg + beta)
            return x + np.array([-r * sinh + r * sinhb,
                                 r * cosh - r * coshb, beta])
        else:  # moving in straight line
            return x + np.array([dist * cos(hdg), dist * sin(hdg), 0])

    def normalize_angle(x):
        x = x % (2 * np.pi)  # force in range [0, 2 pi)
        if x > np.pi:  # move to [-pi, pi)
            x -= 2 * np.pi
        return x

    def residual_h(self,a, b):
        y = a - b
        # data in format [dist_1, bearing_1, dist_2, bearing_2,...]
        for i in range(0, len(y), 2):
            y[i + 1] = self.normalize_angle(y[i + 1])
        return y

    def residual_x(self,a, b):
        y = a - b
        y[2] = self.normalize_angle(y[2])
        return y

    def run_sim(self):





