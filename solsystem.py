import math
import time
import curses


"""Constants"""
G = 1  # simplified gravitational constant for easier numbers

"""graphics stuff"""
stdscr = curses.initscr() # init the screen
height, width = stdscr.getmaxyx() # get terminal height and width 
zoom = 1 
camera_y, camera_x = height/2, width/2 #centers camera

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
        self.ax = 0
        self.ay = 0

    def calc_force(self, other):
        # uses newton's gravitational law to calculate the force between bodies
        dx = other.x - self.x
        dy = other.y - self.y

        dist = math.sqrt(dx**2 + dy**2)

        if dist == 0:
            return 0, 0  # avoid dividing by zero

        force = G * (self.mass * other.mass) / dist**2
        fx = force * (dx / dist)
        fy = force * (dy / dist)

        return fx, fy


def update_forces(bodies):
    for body in bodies:
        fx_tot, fy_tot = 0, 0
        for other in bodies:
            if other is body:
                continue
            fx, fy = body.calc_force(other)
            fx_tot += fx
            fy_tot += fy

        body.ax = fx_tot / body.mass
        body.ay = fy_tot / body.mass


def update_positions(bodies, dt):
    for body in bodies:
        body.vx += body.ax * dt
        body.vy += body.ay * dt
        body.x += body.vx * dt
        body.y += body.vy * dt


def draw(bodies, stdscr, camera_x, camera_y, zoom, width, height):
    for body in bodies:
        screen_x = (body.x - camera_x) * zoom + width
        screen_y = (body.y - camera_y) * zoom + height
