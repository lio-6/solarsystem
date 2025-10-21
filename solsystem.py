import curses
import math
import time 

"""Constants"""
G = 1 # gravitational constant used in newton's gravaty law simplified to one for easier numbers 

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
            fx, fy = body.calc_force(other)
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
 
def draw_bodies(stdscr, bodies, scale, center_x, center_y):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for body in bodies:
        sx = int(w // 2 + (body.x - center_x) * scale)
        sy = int(h // 2 + (body.y - center_y) * scale)
        if 0 <= sx < w and 0 <= sy < h:
            stdscr.addstr(sy, sx, "o", curses.color_pair(body.color))
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    sun = CelestialBody("Sun", 1000, 0, 0, 0, 0, 1, 3)
    planet = CelestialBody("Planet", 1, 10, 0, 0, 3.5, 2, 1)
    moon = CelestialBody("Moon", 0.1, 11, 0, 0, 4.2, 3, 1)
    bodies = [sun, planet, moon]

    scale = 2  # zoom factor
    dt = 0.02

    while True:
        update_forces(bodies)
        update_positions(bodies, dt)
        draw_bodies(stdscr, bodies, scale, 0, 0)
        time.sleep(0.02)


if __name__ == "__main__":
    curses.wrapper(main)   
