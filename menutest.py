import curses

def menu(stdscr):
    stdscr.clear()
    stdscr.box()

    selection = 0
    tst = input("fort")
    stdscr.addstr(4, 4, tst)

def main(stdscr):
    while True:

    
if __name__ == "__main__":
    curses.wrapper(main)
