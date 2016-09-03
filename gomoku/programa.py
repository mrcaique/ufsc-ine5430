import curses, time
w = curses.initscr()
curses.noecho()
curses.cbreak()
curses.mousemask(1)
w.keypad(1)

def ordnator(fn):
    def dec(*args, **kwargs):
        return ord(fn(*args, **kwargs))
    return dec

def locate(y, x):
    return [y//2, x//2]
@ordnator
def get_char(y, x, mapping):
    if y%2 == 0:
        return "-"
    elif x%2 == 0:
        return "|"
    y, x = locate(y, x)
    return mapping[y][x]
mapping = {}
for y in range(15):
    mapping[y] = {}
    for x in range(15):
        mapping[y][x] = " "
def draw(w, mapping):
    # w.clear()
    for x in range(31):
        for y in range(31):
            w.addch(y, x, get_char(y, x, mapping))
    w.refresh()
last_player = "O"
try:
    draw(w, mapping)
    while True:
        i = w.getch()
        if i == curses.KEY_MOUSE:
            _, x, y, _, bstate = curses.getmouse()
            if bstate | curses.BUTTON1_CLICKED:
                y, x = locate(y, x)
                last_player = "O" if last_player == "X" else "X"
                mapping[y][x] = last_player
        draw(w, mapping)
finally:
    curses.nocbreak()
    w.keypad(0)
    curses.echo()
    curses.endwin()
