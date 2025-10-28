import math
import time
import curses


"""Constants"""
G = 1  # simplified gravitational constant for easier numbers

pause = False

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
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return 0, 0
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


def draw(stdscr, bodies, camera_y, camera_x, zoom):
    height, width = stdscr.getmaxyx()
    for body in bodies:
        screen_x = int((body.x - camera_x) * zoom + width / 2)
        screen_y = int((body.y - camera_y) * zoom + height / 2)
        if 0 <= screen_x < width and 0 <= screen_y < height:
            try:
                for x in range(int(screen_x - body.r * zoom), int(screen_x + body.r * zoom) + 1):
                    for y in range(int(screen_y - body.r * zoom), int(screen_y + body.r * zoom) + 1):
                        distance = math.sqrt(((x - screen_x))**2 + ((y - screen_y)*2)**2)
                        if abs(distance) <= body.r:
                            stdscr.addch(y, x, '●')
            except curses.error:
                pass


def update_camera(key, camera_y, camera_x, zoom):
    camera_speed = 10 / zoom
    if key == curses.KEY_UP:
        camera_y -= camera_speed
    if key == curses.KEY_DOWN:
        camera_y += camera_speed
    if key == curses.KEY_LEFT:
        camera_x -= camera_speed
    if key == curses.KEY_RIGHT:
        camera_x += camera_speed
    return camera_y, camera_x


def update_zoom(key, zoom):
    if key == ord('+'):
        zoom *= 1.1
    if key == ord('-'):
        zoom /= 1.1
    return zoom


def bar(stdscr):
    height, width = stdscr.getmaxyx()
    
    # Define bar dimensions
    bar_height = 3
    bar_width = width
    bar_y = 0
    bar_x = 0

    # Create a window for the bar
    bar_win = curses.newwin(bar_height, bar_width, bar_y, bar_x)

    # Draw a border around it
    bar_win.box()

    # Define buttons
    buttons = [
        ("(q)", "Quit"),
        ("(p)", "Pause"),
        ("(n)", "New Body"),
        ("(s)", "Sim speed"),
        ("(a)", "Anchor Camera"),
        ("(  )", "Move"),
        ("(+/-)", "Zoom")
    ]

    xpos = 2  # Padding from left
    ypos = 1  # Inside the border
    for key, text in buttons:
        bar_win.addstr(ypos, xpos, key)
        xpos += len(key) + 1
        bar_win.addstr(ypos, xpos, text)
        xpos += len(text) + 3

    # Refresh only the bar window
    bar_win.refresh()



def UI_newBody(stdscr):
    newBody_win = curses.newwin(20, 40, 3,0)
    newBody_win.box()
    newBody_win.addstr(1, 1, "Add a new body (placeholder)")
    newBody_win.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    stdscr.keypad(True)

    sun = CelestialBody("Sun", mass=1000, x=0, y=0, vx=0, vy=0, color="yellow", r=5)
    planet1 = CelestialBody("Planet1", mass=1, x=50, y=0, vx=0, vy=3.5, color="blue", r=3)
    planet2 = CelestialBody("Planet2", mass=2, x=100, y=0, vx=0, vy=2.5, color="green", r=4)
    bodies = [sun, planet1, planet2]

    dt = 0.1
    zoom = 1
    camera_x, camera_y = 0, 0

    while True:
        stdscr.clear()
        update_forces(bodies)
        update_positions(bodies, dt)
        key = stdscr.getch()
        camera_y, camera_x = update_camera(key, camera_y, camera_x, zoom)
        zoom = update_zoom(key, zoom)
        bar(stdscr)
        draw(stdscr, bodies, camera_y, camera_x, zoom)
        if key == ord('q'):
            break
        if key == ord('n'):
            UI_newBody(stdscr)
        stdscr.refresh()
        time.sleep(0.01)


if __name__ == "__main__":
    curses.wrapper(main)
