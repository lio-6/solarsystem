import curses
import time
import math

def DrawCircle(r, x0, y0):
    points = []
    for x in range(x0 - r, x0 + r + 1):
        for y in range(y0 - r, y0 + r + 1):
            distance = math.sqrt(((x - x0))**2 + ((y - y0)*2)**2)
            # allow small tolerance around r
            if abs(distance) < r:
                points.append((y, x))  # note: (y, x) order for curses
    return points


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.clear()

    h, w = stdscr.getmaxyx()  # screen height and width

    # Initial circle parameters
    r = 8
    x0 = w // 2
    y0 = h // 2
    dx = 1   # horizontal velocity
    dy = 1   # vertical velocity

    while True:
        stdscr.clear()

        # Draw the circle
        for (y, x) in DrawCircle(r, x0, y0):
            if 0 <= y < h and 0 <= x < w:
                stdscr.addch(y, x, '#')

        stdscr.refresh()
        time.sleep(0.05)

        # Update position
        x0 += dx
        y0 += dy

        # Bounce off edges
        if x0 - r <= 0 or x0 + r >= w:
            dx = -dx
        if y0 - r <= 0 or y0 + r >= h:
            dy = -dy

        # Allow user to quit with 'q'
        key = stdscr.getch()
        if key == ord('q'):
            break


# Start the curses application
curses.wrapper(main)
