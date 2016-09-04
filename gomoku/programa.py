# encoding: utf-8
import curses, time, copy, textwrap, collections

__all__ = ["Display", "State"]

BOARD_WIDTH = 15
BOARD_HEIGHT = 15

class InvalidLocation(Exception):
    def __init__(self, y, x):
        super(InvalidLocation, self).__init__("Position y={} and x={} is not a valid position".format(y, x))

class AlreadyMarked(Exception):
    def __init__(self, y, x):
        super(AlreadyMarked, self).__init__("Position y={} and x={} is already marked".format(y, x))


class Mouse(object):
    __slots__ = ["x", "y", "button"]
    LEFT_CLICKED = curses.BUTTON1_CLICKED
    MIDDLE_CLICKED = curses.BUTTON2_CLICKED
    RIGHT_CLICKED = curses.BUTTON3_CLICKED

    def __init__(self):
        _, x, y, _, button = curses.getmouse()
        self.x = x
        self.y = y
        self.button = button

    def match(self, m):
        return self.button | m

class Key(str):
    pass

BaseState = collections.namedtuple(
    "State",
    ["board", "player", "message", "parent"]
)

class State(BaseState):
    """
    This class represents a state in the gomoku game
    """

    @classmethod
    def get_initial_state(cls, initial_player):
        return cls(
            board=tuple(tuple("+" for _ in range(BOARD_WIDTH)) for _ in range(BOARD_HEIGHT)),
            player=initial_player,
            message=None,
            parent=None
        )

    def get_next_player(self):
        if self.player == "X":
            return "O"
        else:
            return "X"

    def is_marked(self, y, x):
        return self.board[y][x] in ("X", "O")

    def is_marked_by(self, y, x, player):
        return player in ("X", "O") and self.board[y][x] == player

    def display(self, message):
        return State(self.board, self.player, message, self)

    def mark(self, y, x):
        if self.is_marked(y, x):
            raise AlreadyMarked(y, x)
        if y >= BOARD_HEIGHT or y < 0 or x >= BOARD_WIDTH or x < 0:
            raise InvalidLocation(y, x)
        board = copy.copy(self.board)
        board = list(board)
        board[y] = list(board[y])
        board[y][x] = self.player
        board[y] = tuple(board[y])
        board = tuple(board)
        player = self.get_next_player()
        return State(board, player, self.message, self)

    def get_next_states(self):
        for y in range(15):
            for x in range(15):
                if self.is_marked(y, x):
                    continue
                yield self.mark(y, x)


class Display(object):
    __slots__ = ["window", "handlers"]

    MOUSE_EVENT = object()
    KEY_EVENT = object()

    def __init__(self):
        self.window = curses.initscr()
        self.handlers = {}
        curses.noecho()
        curses.cbreak()
        curses.mousemask(1)
        self.window.keypad(1)
        curses.curs_set(0)

    def close(self):
        curses.nocbreak()
        self.window.keypad(0)
        curses.echo()
        curses.endwin()

    def get_char(self, y, x, state):
        xm = x%2
        ym = y%2
        if xm == 0 and ym == 0:
            y, x = self.locate(y,x)
            if not state.is_marked(y, x):
                return "+"
            elif state.is_marked_by(y, x, "X"):
                return "X"
            else:
                return "O"
        elif xm == 1 and ym == 1:
            return " "
        elif xm == 1 and ym == 0:
            return "-"
        elif xm == 0 and ym == 1:
            return "|"

    def locate(self, y, x):
        """
        Given y and x in the actual screen, locate the real position in the board
        """
        if y%2 != 0 or x%2 != 0:
            raise InvalidLocation(y, x)
        return [y//2, x//2]

    def get_width(self):
        return (BOARD_WIDTH*2)-1

    def get_height(self):
        return (BOARD_HEIGHT*2)-1

    def display(self, message):
        width  = self.get_width()
        height = self.get_height()
        lines = [s.center(width-2) for s in textwrap.wrap(message, width-2)]
        for i in range(len(lines)):
            lines[i] = "|".join(["", lines[i], ""])
        lines.insert(0, "="*width)
        lines.append("="*width)
        lines_count = len(lines)
        for i, line in enumerate(lines):
            self.window.addstr((height//2)-((lines_count//1))+i, width, line)

    def draw(self, state):
        width  = self.get_width()
        height = self.get_height()
        self.window.clear()
        for x in range(width):
            for y in range(height):
                self.window.addch(y, x, ord(self.get_char(y, x, state)))
        if state.message:
            self.display(state.message)
        self.window.refresh()

    def on(self, event, fn):
        self.handlers.setdefault(event, []).append(fn)

    def once(self, event, fn):
        def cb(*args, **kwargs):
            self.off(event, cb)
            fn(*args,**kwargs)
        self.on(event, cb)

    def off(self, event, fn=None):
        if fn is None:
            self.handlers[event] = []
            return
        self.handlers.setdefault(event, []).remove(fn)

    def trigger(self, event, state, *args, **kwargs):
        for fn in self.handlers.get(event, []):
            state = fn(self, state, *args, **kwargs)
        return state

    def loop(self, state):
        self.draw(state)
        try:
            while True:
                ev = self.window.getch()
                args = []
                if ev >= 0 and ev <= 255:
                    args.append(Key(chr(ev)))
                    ev = self.KEY_EVENT
                elif ev == curses.KEY_MOUSE:
                    args.append(Mouse())
                    ev = self.MOUSE_EVENT
                try:
                    state = self.trigger(ev, state, *args)
                except Exception as e:
                    state = state.display(str(e))
                self.draw(state)
                if state.message:
                    state = state.display(None)
        finally:
            self.close()
        return state


def process_mouse_click(display, state, ev):
    if not ev.match(Mouse.LEFT_CLICKED):
        return state
    y, x = display.locate(ev.y, ev.x)
    return state.mark(y, x)

if __name__ == "__main__":
    state = State.get_initial_state("O")
    display = Display()
    display.on(display.MOUSE_EVENT, process_mouse_click)
    display.loop(state)
