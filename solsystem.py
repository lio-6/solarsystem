import curses
import math
import time 

"""Constants"""
G = 6.67430e-11 # gravitational constant used in newton's gravaty law 
AU = 1.496e11 # Astronomical unit in meters (one AU is the average distance from the earth to the sun)

class CelestialBody:
    def __init__(self, name, mass, x, y, vx, vy, color, r):
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.r = r

    def calc_force(self, other):
        #uses newtons gravitational law to calculate the forces effecting the planet

def DrawCircle(r, x0, y0):
    points = []
    for x in range(x0 - r, x0 + r + 1):
        for y in range(y0 - r, y0 + r + 1):
            distance = math.sqrt(((x - x0))**2 + ((y - y0)*2)**2)
            if abs(distance) < r:
                points.append((y, x))  
    return points

