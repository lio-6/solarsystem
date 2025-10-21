import curses
import math
import time

# --- Constants ---
G = 6.67430e-11  # Gravitational constant
AU = 1.496e11    # Astronomical Unit (meters)
TIMESTEP = 3600 * 24  # Time step for simulation (1 day in seconds)
SCALE = 10 / AU # Scale for display (pixels per meter)

# --- Celestial Body Class ---
class CelestialBody:
    """Represents a celestial body with physical properties."""
    def __init__(self, name, mass, x, y, vx, vy, color, char):
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.char = char

    def calculate_force(self, other):
        """Calculates the gravitational force exerted by another body."""
        dx = other.x - self.x
        dy = other.y - self.y
        dist_sq = dx**2 + dy**2
        
        # Avoid division by zero if bodies are at the same position
        if dist_sq == 0:
            return 0, 0

        dist = math.sqrt(dist_sq)
        force = G * self.mass * other.mass / dist_sq
        
        # Calculate force components
        fx = force * dx / dist
        fy = force * dy / dist
        return fx, fy

    def update_position(self, bodies):
        """Updates the body's velocity and position based on total force."""
        total_fx = total_fy = 0
        for other_body in bodies:
            if self is not other_body:
                fx, fy = self.calculate_force(other_body)
                total_fx += fx
                total_fy += fy

        # Update velocity (F = ma => a = F/m)
        self.vx += total_fx / self.mass * TIMESTEP
        self.vy += total_fy / self.mass * TIMESTEP
        
        # Update position
        self.x += self.vx * TIMESTEP
        self.y += self.vy * TIMESTEP

# --- Main Simulation Function ---
def main(stdscr):
    """Main function to run the simulation."""
    # Curses setup
    curses.curs_set(0) # Hide the cursor
    stdscr.nodelay(1)  # Make getch() non-blocking
    stdscr.timeout(50) # Set a timeout for getch()

    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Sun
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Mercury
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # Venus (often appears reddish)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Earth
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)    # Mars

    # --- Initial Conditions for Celestial Bodies ---
    # Data from NASA factsheets (mass, distance, velocity)
    sun = CelestialBody('Sun', 1.989e30, 0, 0, 0, 0, 1, 'O')
    
    mercury = CelestialBody('Mercury', 3.30e23, 0.387 * AU, 0, 0, -47.4e3, 2, 'o')
    
    venus = CelestialBody('Venus', 4.87e24, 0.723 * AU, 0, 0, -35.0e3, 3, '*')

    earth = CelestialBody('Earth', 5.972e24, -1 * AU, 0, 0, 29.8e3, 4, '@')

    mars = CelestialBody('Mars', 6.42e23, -1.524 * AU, 0, 0, 24.1e3, 5, 'x')

    bodies = [sun, mercury, venus, earth, mars]

    # --- Simulation Loop ---
    while True:
        # Get screen dimensions
        max_y, max_x = stdscr.getmaxyx()
        center_x, center_y = max_x // 2, max_y // 2

        # Handle user input
        key = stdscr.getch()
        if key == ord('q'):
            break # Exit on 'q'
        
        stdscr.clear()

        # Update and draw each body
        for body in bodies:
            # Update position first
            body.update_position(bodies)
            
            # Convert simulation coordinates to screen coordinates
            draw_x = int(center_x + body.x * SCALE * 2) # Multiply x by 2 for better aspect ratio
            draw_y = int(center_y + body.y * SCALE)

            # Draw the body if it's within the screen bounds
            if 0 <= draw_x < max_x and 0 <= draw_y < max_y:
                stdscr.addstr(draw_y, draw_x, body.char, curses.color_pair(body.color))

        # Display info
        stdscr.addstr(0, 1, "TUI Solar System Simulator | Press 'q' to quit")
        
        stdscr.refresh()
        time.sleep(0.001) # Control simulation speed

# --- Run the application ---
if __name__ == "__main__":
    curses.wrapper(main)
