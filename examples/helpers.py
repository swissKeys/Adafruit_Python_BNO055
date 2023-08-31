import numpy as np
from scipy.constants import *

def gamma(p):
    gamma0 = 0.5445
    gamma1 = np.zeros(3)
    gamma1[0] = (gamma0 + (p * gamma0) / 100)
    gamma1[2] = (gamma0 - (p * gamma0) / 100)
    gamma1[1] = gamma0
    return gamma1

def zi(le, z, p):
    i = 0

    z1= np.zeros((3, len(z)))
    z2= np.zeros((3, len(z)))

    while i<3:
      j = 0
      while j < len(z):
        z1[i, j] = j + D(le,p)[i]/2
        z2[i, j] = j - D(le,p)[i]/2
        j+=1
      i+=1
    return z1, z2

def D(le, p):
    D = gamma(p) * le
    return D

def B_z_s(z, I, N, L):
    return 4 * ((mu_0*I*N*L*L)/(np.pi)) * (1/(L*L + 4*z*z)) * (1/(2*L*L + 4*z*z)**0.5) * 1e6
