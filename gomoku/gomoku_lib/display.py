# encoding: utf-8
import curses
import textwrap
import time
from .constants import BOARD_WIDTH, BOARD_HEIGHT
from .events import Mouse, Key
from .exceptions import Quit, GameWarning, StopPropagation, InvalidLocation


class Display(object):
    __slots__ = [
        "window", "handlers", "has_colors", "computer_player"
    ]

    MOUSE_EVENT = object()
    KEY_EVENT = object()
    PREDRAW_EVENT = object()
    POSDRAW_EVENT = object()
    MARK_EVENT = object()
    IA_MOVE = object()

    def __init__(self):
        self.handlers = {}

    def initialize(self):
        self.window = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.mousemask(1)
        self.window.keypad(1)
        curses.curs_set(0)
        self.window.timeout(100)
        self.has_colors = curses.can_change_color()
        if self.has_colors:
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_YELLOW)
            curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_YELLOW)

    def close(self):
        curses.nocbreak()
        if self.window:
            self.window.keypad(0)
        curses.echo()
        curses.endwin()

    def get_char(self, y, x, state):
        xm = x % 2
        ym = y % 2
        if xm == 0 and ym == 0:
            y, x = self.locate(y, x)
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
        Dado y e x, localiza a posicao correspondente no tabuleiro
        """
        if y % 2 != 0 or x % 2 != 0:
            raise InvalidLocation(y, x)
        return [y // 2, x // 2]

    def get_width(self):
        return (BOARD_WIDTH * 2) - 1

    def get_height(self):
        return (BOARD_HEIGHT * 2) - 1

    def format(self, message):
        width = self.get_width()
        height = self.get_height()
        lines = [s.center(width - 2)
                 for line in message.split("\n")
                 for s in textwrap.wrap(line, width - 2)]
        for i in range(len(lines)):
            lines[i] = "|".join(["", lines[i], ""])
        lines.insert(0, "=" * width)
        lines.append("=" * width)
        return lines

    def display_message(self, message):
        width = self.get_width()
        height = self.get_height()
        lines = self.format(message)
        lines_count = len(lines)
        for i, line in enumerate(lines):
            self.window.addstr((height // 2) - ((lines_count // 2)) + i, width,
                               line)

    def display_status(self, state):
        dif = time.time() - state.started_at
        dif_type = "seconds"
        if dif > 60:
            dif /= 60.0
            dif_type = "minutes"
        if dif > 60:
            dif /= 60.0
            dif_type = "hours"
        message = "Pieces in board %d\n" % state.move_count
        message += "Actual player: %s\n" % (state.player)
        message += "Playing for: %.2f %s" % (dif, dif_type)
        width = self.get_width()
        lines = self.format(message)
        lines_count = len(lines)
        for i, line in enumerate(lines):
            self.window.addstr(((lines_count // 2)) + i, width, line)

    def draw(self, state):
        width = self.get_width()
        height = self.get_height()
        self.window.clear()
        for x in range(width):
            for y in range(height):
                char = self.get_char(y, x, state)
                attr = None
                if self.has_colors:
                    color_pair = 1
                    if char == "O":
                        color_pair = 2
                    elif char == "X":
                        color_pair = 3
                        char = "O"
                    attr = curses.color_pair(color_pair)
                if char in ("O", "X"):
                    if attr is None:
                        attr = 0
                    attr = attr | curses.A_BOLD
                if attr is not None:
                    self.window.addch(y, x, ord(char), attr)
                else:
                    self.window.addch(y, x, ord(char))
        if state.message:
            self.display_message(state.message)
        self.display_status(state)
        self.window.refresh()

    def on(self, event, fn):
        self.handlers.setdefault(event, []).insert(0, fn)

    def once(self, event, fn):
        def cb(*args, **kwargs):
            self.off(event, cb)
            return fn(*args, **kwargs)

        self.on(event, cb)

    def off(self, event, fn=None):
        if fn is None:
            self.handlers[event] = []
            return
        self.handlers.setdefault(event, []).remove(fn)

    def trigger(self, event, state, *args, **kwargs):
        for fn in self.handlers.get(event, []):
            try:
                state = fn(self, state, *args, **kwargs)
            except StopPropagation as e:
                if e.state:
                    state = e.state
                break
        return state

    def trigger_delay(self, event, *args, **kwargs):
        def dispatch(display, state, *args, **kwargs):
            return display.trigger(event, state, *args, **kwargs)
        self.once(self.POSDRAW_EVENT, dispatch)

    def select_player(self, state):
        state = state.display(
            "Enter the player you want: \n" +
            "- X \n" +
            "- O \n" +
            "- V (let the AI play against itself)\n" +
            "- M (let you play against yourself (?))\n" +
            "(press the key in your keyboard)"
        )

        def disable_mouse(_, state, ev, *args, **kwargs):
            state = state.display(
                "Enter the player you want: \n" +
                "- X \n" +
                "- O \n" +
                "- V (let the AI play against itself)\n" +
                "- M (let you play against yourself (?))\n" +
                "(press the key in your keyboard)"
            )
            raise StopPropagation(state)

        def disable_mouse_forever(_, state, *args, **kwargs):
            state = state.display("Let the AI play against itself! \o/")
            raise StopPropagation(state)

        def receive_key(_, state, ev, *args, **kwargs):
            ev = ev.upper()
            if ev not in ('X', 'O', 'V', 'M'):
                raise StopPropagation(
                    state.display(
                        "Please, inform a valid player: X, O, V or M"
                    )
                )
            self.off(self.MOUSE_EVENT, disable_mouse)
            self.off(self.KEY_EVENT, receive_key)
            if ev == 'M':
                self.computer_player = ''
                state = state.display(
                    "You entered the manual mode. " +
                    "In this mode, " +
                    "we can battle with another person easily. " +
                    "Just remember that the first player is O, " +
                    "and the next is X. :)"
                )
            elif ev == 'V':
                self.computer_player = 'OX'
                self.on(self.MOUSE_EVENT, disable_mouse_forever)
                state = state.display(
                    "You entered the AI vs. AI mode. " +
                    "Sit down and let the computer battle against itself. :)"
                )
                state = self.trigger(self.IA_MOVE, state)
            elif ev == 'X':
                self.computer_player = 'O'
                state = self.trigger(self.IA_MOVE, state)
                state = state.display(
                    ("You selected the player %s\n" +
                     "Tip: You can undo your movements pressing the button "
                     "U in your keyboard") % ev)
            else:
                self.computer_player = 'X'
                state = state.display(
                    ("You selected the player %s\n" +
                     "Tip: You can undo your movements pressing the button " +
                     "U in your keyboard") % ev)
            raise StopPropagation(state)

        self.on(self.MOUSE_EVENT, disable_mouse)
        self.on(self.KEY_EVENT, receive_key)
        return state

    def loop(self, state):
        curses_err = False
        try:
            self.initialize()
            state = self.select_player(state)
            self.draw(state)
            while True:
                ev = self.window.getch()
                args = []
                if ev >= 0 and ev <= 255:
                    args.append(Key(chr(ev)))
                    ev = self.KEY_EVENT
                elif ev == curses.KEY_MOUSE:
                    args.append(Mouse.get_current())
                    ev = self.MOUSE_EVENT
                else:
                    ev = None
                if ev:
                    try:
                        state = self.trigger(ev, state, *args)
                    except GameWarning as e:
                        state = state.display(str(e))
                state = self.trigger(self.PREDRAW_EVENT, state)
                self.draw(state)
                state = self.trigger(self.POSDRAW_EVENT, state)
        except (KeyboardInterrupt, Quit):
            pass
        except curses.error as e:
            curses_err = e
        finally:
            self.close()
        if curses_err:
            print(
                "Curses returned error, so probably your terminal does not " +
                "support curses or the width/height of your terminal is not " +
                "suficient to the game run..Please, fix that!"
            )
            print("Original Curses error: %s" % curses_err)

        return state
