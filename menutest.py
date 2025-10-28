
import math
import time
import curses
import copy  # Added for deepcopying simulation state


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
        self.color = color  # This is now a curses color_pair index (int)
        self.r = r
        self.ax = 0
        self.ay = 0

    def calc_force(self, other):
        # uses Newton's gravitational law to calculate the force between bodies
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


def draw(stdscr, bodies, camera_y, camera_x, zoom):
    height, width = stdscr.getmaxyx()
    for body in bodies:
        # translate world coordinates to screen coordinates
        screen_x = int((body.x - camera_x) * zoom + width / 2)
        screen_y = int((body.y - camera_y) * zoom + height / 2)

        # draw if inside screen
        if 0 <= screen_x < width and 0 <= screen_y < height:
            try:
                # Iterate over a square bounding box around the circle
                for x in range(int(screen_x - body.r * zoom), int(screen_x + body.r * zoom) + 1):
                    for y in range(int(screen_y - body.r * zoom), int(screen_y + body.r * zoom) + 1):
                        
                        # Check if pixel is within the screen bounds before drawing
                        if not (0 <= x < width and 0 <= y < height):
                            continue
                            
                        # Calculate pixel distance from the center
                        # FIX: Corrected distance formula (was `((y - screen_y)*2)**2`)
                        distance = math.sqrt((x - screen_x)**2 + (y - screen_y)**2)
                        
                        # Draw if pixel is inside the circle's radius (in pixels)
                        # FIX: Corrected radius check (was `abs(distance) <= body.r`)
                        if distance <= (body.r * zoom):
                            stdscr.addch(y, x, '●', curses.color_pair(body.color))

            except curses.error:
                pass  # ignore drawing errors at edges


def draw_preview_path(stdscr, path, camera_y, camera_x, zoom):
    """Draws the calculated trajectory path"""
    height, width = stdscr.getmaxyx()
    for x, y in path:
        screen_x = int((x - camera_x) * zoom + width / 2)
        screen_y = int((y - camera_y) * zoom + height / 2)

        if 0 <= screen_x < width and 0 <= screen_y < height:
            try:
                # Draw the path as faint dots in white (color pair 4)
                stdscr.addch(screen_y, screen_x, '.', curses.color_pair(4))
            except curses.error:
                pass


def calculate_preview(original_bodies, fields, dt=0.1, steps=1000):
    """
    Runs a headless simulation to preview the new body's path.
    """
    # Create a deep copy to not affect the main simulation
    sim_bodies = copy.deepcopy(original_bodies)
    
    try:
        # Parse field values
        name = fields[0]["value"]
        mass = float(fields[1]["value"])
        x = float(fields[2]["value"])
        y = float(fields[3]["value"])
        vx = float(fields[4]["value"])
        vy = float(fields[5]["value"])
        r = float(fields[6]["value"])
    except ValueError:
        return [] # Invalid input, return no path

    # Create the temporary new body
    temp_body = CelestialBody(name, mass, x, y, vx, vy, 4, r)
    sim_bodies.append(temp_body)

    path = []
    for i in range(steps):
        update_forces(sim_bodies)
        update_positions(sim_bodies, dt)
        
        # Store the path of the new body (which is the last one in the list)
        # Only store every few points to avoid visual clutter
        if i % 5 == 0:
            path.append((sim_bodies[-1].x, sim_bodies[-1].y))

    return path


def add_body_menu(stdscr, original_bodies, camera_y, camera_x, zoom, dt):
    """
    Displays a pop-up menu to add a new body.
    Shows a live preview of the body's trajectory.
    """
    # Set terminal to blocking, with echo for typing
    stdscr.nodelay(False)
    curses.echo()

    h, w = stdscr.getmaxyx()
    win_h = 12
    win_w = 40
    win_y = (h - win_h) // 2
    win_x = (w - win_w) // 2

    popup = curses.newwin(win_h, win_w, win_y, win_x)
    popup.keypad(True)

    fields = [
        {"label": "Name:   ", "value": "NewPlanet"},
        {"label": "Mass:   ", "value": "1"},
        {"label": "X pos:  ", "value": "200"},
        {"label": "Y pos:  ", "value": "0"},
        {"label": "X vel:  ", "value": "0"},
        {"label": "Y vel:  ", "value": "2"},
        {"label": "Radius: ", "value": "2"},
    ]
    current_field = 0
    
    new_body = None

    while True:
        # 1. Draw the background (paused simulation)
        stdscr.clear()
        draw(stdscr, original_bodies, camera_y, camera_x, zoom)

        # 2. Calculate and draw the preview path
        preview_path = calculate_preview(original_bodies, fields, dt)
        draw_preview_path(stdscr, preview_path, camera_y, camera_x, zoom)
        
        stdscr.refresh() # Refresh background first

        # 3. Draw the popup window
        popup.clear()
        popup.border()
        popup.addstr(0, 2, " Add New Body ")

        for i, field in enumerate(fields):
            label = field["label"]
            value = field["value"]
            attr = curses.A_REVERSE if i == current_field else curses.A_NORMAL
            popup.addstr(i + 2, 2, f"{label}{value}", attr)

        popup.addstr(win_h - 3, 2, "UP/DOWN: Move, ENTER: Edit")
        popup.addstr(win_h - 2, 2, "'s': Save & Exit, 'q': Quit")
        popup.refresh()

        # 4. Get user input
        key = popup.getch()

        if key == curses.KEY_UP:
            current_field = (current_field - 1) % len(fields)
        elif key == curses.KEY_DOWN:
            current_field = (current_field + 1) % len(fields)
        elif key == ord('\n') or key == curses.KEY_ENTER:
            # Edit mode
            # FIX: Calculate y and x dynamically instead of from dict
            y = current_field + 2  # Matches the drawing loop (i + 2)
            x = 2 + len(fields[current_field]["label"]) # Starts after the label

            popup.addstr(y, x, " " * (win_w - x - 2)) # Clear old value
            
            # Use curses.echo() to show typing
            curses.echo()
            new_val = popup.getstr(y, x, 20).decode('utf-8').strip()
            curses.noecho()
            
            if new_val: # Only update if user typed something
                fields[current_field]["value"] = new_val
        elif key == ord('q'):
            new_body = None # Cancel
            break
        elif key == ord('s'):
            # Save and exit
            try:
                name = fields[0]["value"]
                mass = float(fields[1]["value"])
                x = float(fields[2]["value"])
                y = float(fields[3]["value"])
                vx = float(fields[4]["value"])
                vy = float(fields[5]["value"])
                r = float(fields[6]["value"])
                # Create the body, using white (pair 4) as default for new bodies
                new_body = CelestialBody(name, mass, x, y, vx, vy, 4, r)
                break
            except ValueError:
                # Flash an error message
                popup.addstr(win_h - 1, 2, "Error: Invalid number format!", curses.A_REVERSE)
                popup.refresh()
                time.sleep(1)
                
    # Restore terminal state
    curses.noecho()
    stdscr.nodelay(True)
    stdscr.timeout(0)
    del popup
    
    return new_body


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

def update_zoom (key, zoom):
    if key == ord('+'):
        zoom *= 1.1
    if key == ord('-'):
        zoom /= 1.1

    return zoom


def main(stdscr):
    curses.curs_set(0)      # hide cursor
    stdscr.nodelay(True)    # non-blocking input
    stdscr.timeout(0)
    stdscr.keypad(True)

    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    #               (pair_id, foreground, background)
    curses.init_pair(1, curses.COLOR_YELLOW, -1) # Sun
    curses.init_pair(2, curses.COLOR_BLUE,   -1) # Planet1
    curses.init_pair(3, curses.COLOR_GREEN,  -1) # Planet2
    curses.init_pair(4, curses.COLOR_WHITE,  -1) # New/Preview

    # initialize simulation
    # sun = CelestialBody("Sun", mass=1000, x=0, y=0, vx=0, vy=0, color=1, r=5)
    # planet1 = CelestialBody("Planet1", mass=1, x=50, y=0, vx=0, vy=3.5, color=2, r=3)
    # planet2 = CelestialBody("Planet2", mass=2, x=100, y=0, vx=0, vy=2.5, color=3, r=4)
    # bodies = [sun, planet1, planet2]
    bodies = [ ]

    dt = 0.1
    zoom = 1
    camera_x, camera_y = 0, 0

    while True:
        stdscr.clear()

        # Get key press
        key = stdscr.getch()

        # Update simulation only if not in a menu
        if key != ord('a'):
            update_forces(bodies)
            update_positions(bodies, dt)

        # Update camera and zoom
        camera_y, camera_x = update_camera(key, camera_y, camera_x, zoom)
        zoom = update_zoom(key, zoom)

        # Draw all bodies
        draw(stdscr, bodies, camera_y, camera_x, zoom)
        stdscr.refresh()

        time.sleep(0.01)

        # Handle key presses
        if key == ord('q'):
            break
        elif key == ord('a'):
            # Call the add body menu
            new_body = add_body_menu(stdscr, bodies, camera_y, camera_x, zoom, dt)
            if new_body:
                bodies.append(new_body)
            # Clear any leftover key presses after menu exits
            while stdscr.getch() != -1:
                pass


if __name__ == "__main__":
    curses.wrapper(main)
