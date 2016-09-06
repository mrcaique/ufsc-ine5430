# encoding: utf-8
import curses, time, copy, textwrap, collections

__all__ = ["Display", "State"]

BOARD_WIDTH = 15
BOARD_HEIGHT = 15

DIRECTIONS = (
    lambda y, x, n: [y, x-n], # Esquerda
    lambda y, x, n: [y, x+n], # Direita
    lambda y, x, n: [y-n, x], # Superior
    lambda y, x, n: [y+n, x], # Inferior
    lambda y, x, n: [y-n, x-n], # Diagonal Superior Esquerda
    lambda y, x, n: [y+n, x+n], # Diagonal Inferior Direita
    lambda y, x, n: [y-n, x+n], # Diagonal Superior Direita
    lambda y, x, n: [y+n, x-n] # Diagonal Inferior Esquerda
)

class GameWarning(Exception):
    pass

class InvalidLocation(GameWarning):
    def __init__(self, y, x):
        super(InvalidLocation, self).__init__("Position y={} and x={} is not a valid position".format(y, x))

class AlreadyMarked(GameWarning):
    def __init__(self, y, x):
        super(AlreadyMarked, self).__init__("Position y={} and x={} is already marked".format(y, x))

class Quit(Exception):
    pass

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
    def get_initial_state(cls):
        return cls(
            board=tuple(tuple("+" for _ in range(BOARD_WIDTH)) for _ in range(BOARD_HEIGHT)),
            player="O",
            message=None,
            parent=None
        )

    def get_next_player(self):
        if self.player == "X":
            return "O"
        else:
            return "X"

    def is_valid_position(self, y, x):
        return y >= 0 and x >= 0 and y < BOARD_HEIGHT and x < BOARD_WIDTH

    def is_marked(self, y, x):
        return self.is_valid_position(y, x) and self.board[y][x] in ("X", "O")

    def is_marked_by(self, y, x, player):
        return self.is_valid_position(y, x) and player in ("X", "O") and self.board[y][x] == player

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

    def max_sequence(self, py, px, player=None):
        """
        Dado um ponto, checa a maior sequencia possivel que eh possivel alcancar
        partindo deste ponto
        """
        if player is None:
            player = self.board[py][px]
        if not self.is_marked_by(py, px):
            return 0
        mseq = 1
        for i, direction in enumerate(DIRECTIONS):
            seq = 1
            for n in range(1, 5):
                y2, x2 = direction(py, px, n)
                if not self.is_marked_by(y2, x2, player):
                    break
                seq += 1
            if seq > mseq:
                mseq = seq
        return mseq

    def won(self, py, px, player=None):
        """
        Checa se ha uma sequencia valida a partir de um ponto inicial no tabuleiro
        """
        if player is None:
            player = self.board[py][px]
        if not self.is_marked_by(py, px, player):
            return None
        for i, direction in enumerate(DIRECTIONS):
            won = True
            for n in range(1, 5):
                y2, x2 = direction(py, px, n)
                if not self.is_marked_by(y2, x2, player):
                    won = False
                    break
            if won:
                return player
        return None

    def check_won(self, player=None):
        """
        Checa se ha uma sequencia valida partindo de cada ponto do tabuleiro
        """
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                result = self.won(y, x, player)
                if result:
                    return result

    def check_max_sequence(self, player=None):
        """
        Checa a maior sequencia encontrada partindo de cada ponto do tabuleiro
        """
        mseq = 0
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                seq = self.max_sequence(y, x, player)
                if seq > mseq:
                    mseq = seq
                if seq == 5:
                    break
            if mseq == 5:
                break
        return mseq

    def get_next_states(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.is_marked(y, x):
                    continue
                yield self.mark(y, x)


class Display(object):
    __slots__ = ["window", "handlers", "has_colors"]

    MOUSE_EVENT = object()
    KEY_EVENT = object()
    PREDRAW_EVENT = object()
    POSDRAW_EVENT = object()
    MARK_EVENT = object()

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
            self.display(state.message)
        self.window.refresh()

    def on(self, event, fn):
        self.handlers.setdefault(event, []).append(fn)

    def once(self, event, fn):
        def cb(*args, **kwargs):
            self.off(event, cb)
            return fn(*args,**kwargs)
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
        try:
            self.initialize()
            self.draw(state)
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
                except GameWarning as e:
                    state = state.display(str(e))
                state = self.trigger(self.PREDRAW_EVENT, state)
                self.draw(state)
                state = self.trigger(self.POSDRAW_EVENT, state)
                if state.message:
                    state = state.display(None)
        except (KeyboardInterrupt, Quit):
            pass
        finally:
            self.close()
        return state


def process_mouse_click(display, state, ev):
    if not ev.match(Mouse.LEFT_CLICKED):
        return state
    y, x = display.locate(ev.y, ev.x)
    state = state.mark(y, x)
    return display.trigger(display.MARK_EVENT, state, y=y, x=x)

def finish(display, state, *args, **kwargs):
    raise Quit()
    return state

def check_won(display, state, y, x):
    won = state.won(y, x)
    if won:
        state = state.display("The player {} won".format(won))
        display.off(display.MOUSE_EVENT)
        display.once(display.MOUSE_EVENT, finish)
    return state
if __name__ == "__main__":
    state = State.get_initial_state()
    display = Display()
    display.on(display.MOUSE_EVENT, process_mouse_click)
    display.on(display.MARK_EVENT, check_won)
    display.loop(state)
