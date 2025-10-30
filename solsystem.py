import math
import time
import curses

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

def draw(sim, bodies, camera_y, camera_x, zoom):
    height, width = sim.getmaxyx()
    color_map = {
        "yellow": curses.color_pair(1),
        "blue": curses.color_pair(2),
        "green": curses.color_pair(3),
        "red": curses.color_pair(4),
        "cyan": curses.color_pair(5)
    }
    for body in bodies:
        screen_x = int((body.x - camera_x) * zoom + width / 2)
        screen_y = int((body.y - camera_y) * zoom + height / 2)
        if 0 <= screen_x < width and 0 <= screen_y < height:
            try:
                color_attr = color_map.get(body.color.lower(), 0)
                for x in range(int(screen_x - body.r * zoom), int(screen_x + body.r * zoom) + 1):
                    for y in range(int(screen_y - body.r * zoom), int(screen_y + body.r * zoom) + 1):
                        distance = math.sqrt(((x - screen_x))**2 + ((y - screen_y)*2)**2)
                        if abs(distance) <= body.r * zoom:
                            sim.addch(y, x, '●', color_attr)
            except curses.error:
                pass

def predict_trajectory(bodies, steps=500, dt=0.1):
    # Deep copy bodies so we don't affect the real ones
    tempbodies = [CelestialBody(b.name, b.mass, b.x, b.y, b.vx, b.vy, b.color, b.r) for b in bodies]
    
    # Store trajectories for each body
    trajectories = {b.name: [] for b in tempbodies}

    for _ in range(steps):
        update_forces(tempbodies)
        update_positions(tempbodies, dt)
        for b in tempbodies:
            trajectories[b.name].append((b.x, b.y))
    
    return trajectories

def draw_trajectory(stdscr, bodies, trajectories, camera_y, camera_x, zoom):
    height, width = stdscr.getmaxyx()
    for body in bodies:
        for (x, y) in trajectories[body.name]:
            screen_x = int((x - camera_x) * zoom + width / 2)
            screen_y = int((y - camera_y) * zoom + height / 2)
            if 0 <= screen_x < width and 0 <= screen_y < height:
                try:
                    stdscr.addch(screen_y, screen_x, '.')
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


def bar(bar_win):
    bar_win.clear() 
    
    buttons = [
        ("(q)", "Quit"),
        ("(p)", "Pause"),
        ("(n)", "New Body"),
        ("(t)", "Show Trajectory"),
        ("(e)", "Examples"),
        ("(c)", "Clear"),
        ("( ←↑↓→ )", "Move"),
        ("(+/-)", "Zoom")
    ]

    bar_win.box()

    xpos = 2  
    ypos = 1  
    for key, text in buttons:
        try:
            bar_win.addstr(ypos, xpos, key)
            xpos += len(key) + 1
            bar_win.addstr(ypos, xpos, text)
            xpos += len(text) + 3
        except curses.error:
            pass 

    bar_win.refresh()

def Textbox(key, text):
    if 32 <= key <= 126:
        text += chr(key)
    elif key in (curses.KEY_BACKSPACE, 8, 127):
        if len(text) > 0:
            text = text[:-1]
    return text

def UI_newBody(newBody_win, preview_win, bodies, camera_y, camera_x, zoom):
    newBody_win.keypad(True)
    newBody_win.nodelay(True)

    run_sim = True

    selection = 0 

    fields = [
        ("Name:","NewPlanet"),
        ("Mass:","1.0"),
        ("x:","0.0"),
        ("y:","0.0"),
        ("vx:","0.0"),
        ("vy:","0.0"),
        ("Color:","yellow"),
        ("Radius:", "1.0"),
    ]
    while True:
        newBody_win.erase()
        newBody_win.box()
        key = newBody_win.getch()

        for i, (label, value) in enumerate(fields):
            marker = "->" if selection == i else " "
            newBody_win.addstr(1 + i, 2, f"{marker} {label} {value}")

            try:
                name = fields[0][1]
                mass = float(fields[1][1])
                x = float(fields[2][1])
                y = float(fields[3][1])
                vx = float(fields[4][1])
                vy = float(fields[5][1])
                color = fields[6][1]
                r = float(fields[7][1])
            except Exception:
                continue

            if run_sim:
                preview_win.erase()
                testBody = CelestialBody(name, mass, x, y, vx, vy, color, r)
                testBodies = [CelestialBody(b.name, b.mass, b.x, b.y, b.vx, b.vy, b.color, b.r) for b in bodies]
                testBodies.append(testBody)
                draw_trajectory(preview_win,testBodies,predict_trajectory(testBodies),camera_y, camera_x, zoom)
                preview_win.refresh()
                run_sim = False

        if key == 27: #Escape 
            return None

        if key == curses.KEY_DOWN:
            if selection < 7:
                selection += 1
        if key == curses.KEY_UP:
            if selection > 0:
                selection -= 1
        if key in (curses.KEY_ENTER, 10, 13):

            try:
                new_body = CelestialBody(name, mass, x, y, vx, vy, color.lower(), r)
                return new_body
            except Exception:
                continue

        label, value = fields[selection]
        if label in ("Name:", "Color:"):
            value = Textbox(key, value)
        else:
            if 48 <= key <= 57 or key in (46, 45, curses.KEY_BACKSPACE, 8, 127):
                value = Textbox(key, value)
                run_sim = True
        
        fields[selection] = (label, value)
        newBody_win.refresh()
        time.sleep(0.01)


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    
    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_YELLOW, -1)
    curses.init_pair(2, curses.COLOR_BLUE, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(5, curses.COLOR_CYAN, -1)
    
    height, width = stdscr.getmaxyx()

    bar_win = curses.newwin(3, width, 0, 0)
    newBody_win = curses.newwin(20, 40, 3,0)
    sim = curses.newwin(height - 3, width, 3, 0)
    preview_win = curses.newwin(height - 3, width, 3, 0)


    #test
    bodies = []

    dt = 0.1
    zoom = 1
    camera_x, camera_y = 0, 0
    pause = False

    show_new_body_win = False
    toggleTrajectory = False
    ui = False
    example_mode = 0

    while True:
        sim.erase()
        bar(bar_win)  

        if not pause:
            update_forces(bodies)
            update_positions(bodies, dt)

        key = stdscr.getch()


        if not ui:
            camera_y, camera_x = update_camera(key, camera_y, camera_x, zoom)
            zoom = update_zoom(key, zoom)

            if key == ord('p'):
                pause = not pause
            if key == ord('q'):
                break
            if key == ord('n'):
                show_new_body_win = True
            if key == ord('t'):
                toggleTrajectory = not toggleTrajectory
            if key == ord('e'):

                if example_mode == 0:
                    sun = CelestialBody("Sun", mass=1000, x=0, y=0, vx=0, vy=0, color="yellow", r=5)
                    planet1 = CelestialBody("Planet1", mass=1, x=50, y=0, vx=0, vy=3.5, color="blue", r=3)
                    planet2 = CelestialBody("Planet2", mass=2, x=100, y=0, vx=0, vy=2.5, color="green", r=4)
                    bodies = [sun, planet1, planet2]
                elif example_mode == 1:
                    # Binary stars orbiting each other
                    star1 = CelestialBody("Star A", mass=500, x=-15, y=0, vx=0, vy=1.8, color="yellow", r=4)
                    star2 = CelestialBody("Star B", mass=500, x=15, y=0, vx=0, vy=-1.8, color="red", r=4)

                    # Closer planets in circumbinary orbit
                    planet1 = CelestialBody("Planet Alpha", mass=5, x=0, y=60, vx=-3.5, vy=0, color="blue", r=2)
                    planet2 = CelestialBody("Planet Beta", mass=3, x=0, y=-90, vx=3.0, vy=0, color="green", r=2)

                    bodies = [star1, star2, planet1, planet2]
                else:
                    b1 = CelestialBody("Body1", 1, x = 0.9700436 * 5, y = -0.24308753 * 5, vx = 0.466203685 / math.sqrt(5), vy = 0.43236573 / math.sqrt(5), color = "red", r = 1.0)
                    b2 = CelestialBody("Body2", 1, x = -0.9700436 * 5, y = 0.24308753 * 5, vx = 0.466203685 / math.sqrt(5), vy = 0.43236573 / math.sqrt(5), color = "blue", r = 1.0)
                    b3 = CelestialBody("Body3", 1, x = 0.0, y = 0.0, vx = -0.93240737 / math.sqrt(5), vy = -0.86473146 / math.sqrt(5), color = "green", r = 1.0)
                    bodies = [b1, b2, b3]

                example_mode = (example_mode + 1) % 3

            if key == ord('c'):
                bodies = []

        if toggleTrajectory:
            draw_trajectory(sim, bodies, predict_trajectory(bodies), camera_y, camera_x, zoom)

        draw(sim, bodies, camera_y, camera_x, zoom)


        if show_new_body_win:
            ui = True
            pause = True
            new_body = UI_newBody(newBody_win, preview_win, bodies, camera_y, camera_x, zoom)
            if new_body:
                bodies.append(new_body)

            show_new_body_win = False
            ui = False
            pause = False
            newBody_win.erase()
            newBody_win.refresh()


        sim.refresh()
        time.sleep(0.01)

if __name__ == "__main__":
    curses.wrapper(main)
