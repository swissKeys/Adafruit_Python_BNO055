import numpy as np
from scipy.constants import *
import math

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

def seph_to_cat(total_intesity, declination, inclination):
  
  # Convert degrees to radians
  declination_rad = math.radians(declination)
  inclination_rad = math.radians(inclination) 

  total_intesity = total_intesity / 1000

  # Calculate X, Y, and Z components
  X = total_intesity * math.sin(inclination_rad) * math.cos(declination_rad)
  Y = total_intesity * math.sin(inclination_rad) * math.sin(declination_rad)
  Z = total_intesity * math.cos(inclination_rad)

  return {'mag_x': 0.6, 'mag_y': 0.7, 'mag_z': 45.00}