import math
import time


"""Constants"""
G = 1  # simplified gravitational constant for easier numbers


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


def print_positions(bodies, t):
    print(f"\nTime: {t:.2f}")
    for body in bodies:
        print(f"{body.name:10s} x={body.x:10.3f}, y={body.y:10.3f}")


def main():
    sun = CelestialBody(
        "Sun", mass=1000, x=0, y=0, vx=0, vy=0, color="yellow", r=3
    )
    planet1 = CelestialBody(
        "Planet1", mass=1, x=50, y=0, vx=0, vy=3.5, color="blue", r=1
    )
    planet2 = CelestialBody(
        "Planet2", mass=2, x=100, y=0, vx=0, vy=2.5, color="green", r=1.5
    )

    bodies = [sun, planet1, planet2]

    dt = 0.05  # timestep
    t = 0

    try:
        while True:
            update_forces(bodies)
            update_positions(bodies, dt)
            print_positions(bodies, t)
            t += dt
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nSimulation stopped.")


main()
