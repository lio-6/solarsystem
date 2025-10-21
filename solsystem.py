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
        #uses newtons gravitational law to calculate the force between bodies
        dx = other.x - self.x
        dy = other.y - self.y
        
        dist = math.sqrt((dx**2 + dy**2)) # Pytagoras sats 

        if dist == 0: # avoid dividing by 0
            return 0, 0

        force = G * (self.mass * other.mass) / dist**2

        fx = force * (dx / dist)
        fy = force * (dy / dist)

        return fx, fy
        
    def update_forces(bodies):
        # sums every acting force and convers it to acceleration with netwon's second law
    for body in bodies:
        fx_tot = 0
        fy_tot = 0
        for other in bodies:
            if other is body:
                continue # makes sure that the body doesn't calc the force exerted on itself 
            fx, fy = calc_force(other)
            fx_tot += fx
            fy_tot += fy 
        body.ax = fx_tot / body.mass
        body.ay = fy_tot / body.mass

    def update_positions(bodies, dt):
        for body in bodies:
        # Update velocity from acceleration
            body.vx += body.ax * dt
            body.vy += body.ay * dt

        # Update position from velocity
            body.x += body.vx * dt
            body.y += body.vy * dt
        

def DrawCircle(r, x0, y0):
    points = []
    for x in range(x0 - r, x0 + r + 1):
        for y in range(y0 - r, y0 + r + 1):
            distance = math.sqrt(((x - x0))**2 + ((y - y0)*2)**2)
            if abs(distance) < r:
                points.append((y, x))  
    return points

