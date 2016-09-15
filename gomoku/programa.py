# encoding: utf-8
import curses, time, copy, textwrap, collections, random, math

__all__ = ["Display", "State"]

BOARD_WIDTH = 15
BOARD_HEIGHT = 15

ALL_DIRECTIONS = (
    lambda y, x, n: [y, x-n], # Esquerda
    lambda y, x, n: [y, x+n], # Direita
    lambda y, x, n: [y-n, x], # Superior
    lambda y, x, n: [y+n, x], # Inferior
    lambda y, x, n: [y-n, x-n], # Diagonal Superior Esquerda
    lambda y, x, n: [y+n, x+n], # Diagonal Inferior Direita
    lambda y, x, n: [y-n, x+n], # Diagonal Superior Direita
    lambda y, x, n: [y+n, x-n] # Diagonal Inferior Esquerda
)

###############################################
# Estas direcoes so devem ser usadas no caso ##
# de estar varrendo toda a matriz            ##
###############################################
OPTIMIZED_DIRECTIONS = (
    # lambda y, x, n: [y, x-n], # Esquerda
    lambda y, x, n: [y, x+n], # Direita
    # lambda y, x, n: [y-n, x], # Superior
    lambda y, x, n: [y+n, x], # Inferior
    # lambda y, x, n: [y-n, x-n], # Diagonal Superior Esquerda
    lambda y, x, n: [y+n, x+n], # Diagonal Inferior Direita
    # lambda y, x, n: [y-n, x+n], # Diagonal Superior Direita
    lambda y, x, n: [y+n, x-n] # Diagonal Inferior Esquerda
)

class GameWarning(Exception):
    """
    Essa exceção é emitida quando um aviso a respeito do jogo deve ser emitida
    """
    pass

class InvalidLocation(GameWarning):
    """
    Essa exceção é emitida quando uma posição é inválida
    """
    def __init__(self, y, x):
        super(InvalidLocation, self).__init__("Position y={} and x={} is not a valid position".format(y, x))

class AlreadyMarked(GameWarning):
    """
    Essa excecao é emitida quando uma posição no tabuleiro já está marcada
    """
    def __init__(self, y, x):
        super(AlreadyMarked, self).__init__("Position y={} and x={} is already marked".format(y, x))

class StopPropagation(Exception):
    """
    Emitir essa exceção faz um evento parar de executar os próximos handlers
    """
    def __init__(self, state=None):
        """
        Use o parametro state para setar o novo estado da aplicação.
        """
        super(StopPropagation, self).__init__("StopPropagation")
        self.state = state

class Quit(Exception):
    """
    Emitir essa exceção faz o programa terminar sua execucao
    """
    pass

class Mouse(object):
    __slots__ = ["x", "y", "button"]
    LEFT_CLICKED = curses.BUTTON1_CLICKED
    MIDDLE_CLICKED = curses.BUTTON2_CLICKED
    RIGHT_CLICKED = curses.BUTTON3_CLICKED

    def __init__(self, x, y, button):
        self.x = x
        self.y = y
        self.button = button

    @classmethod
    def get_current(cls):
        _, x, y, _, button = curses.getmouse()
        return cls(x, y, button)

    def match(self, m):
        return self.button | m

class Key(str):
    pass

Move = collections.namedtuple("Move", ["y", "x"])
BaseState = collections.namedtuple(
    "State",
    ["board", "player", "message", "parent", "last_move"]
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
            parent=None,
            last_move=None
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
        return State(
            board = self.board,
            player = self.player,
            message = message,
            parent = self,
            last_move = self.last_move
        )

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
        return State(board, player, self.message, self, Move(y, x))

    def max_sequence(self, py, px, player=None, directions=ALL_DIRECTIONS):
        """
        Dado um ponto, checa a maior sequencia possivel que eh possivel alcancar
        partindo deste ponto
        """
        if player is None:
            player = self.board[py][px]
        if not self.is_marked_by(py, px, player):
            return 0
        mseq = 1
        for direction in directions:
            seq = 1
            for n in range(1, 5):
                y2, x2 = direction(py, px, n)
                if not self.is_marked_by(y2, x2, player):
                    break
                seq += 1
            if seq > mseq:
                mseq = seq
        return mseq

    def won(self, py, px, player=None, directions=ALL_DIRECTIONS):
        """
        Checa se ha uma sequencia valida a partir de um ponto inicial no tabuleiro
        """
        if player is None:
            player = self.board[py][px]
        if not self.is_marked_by(py, px, player):
            return None
        for direction in directions:
            won = True
            for n in range(1, 5):
                y2, x2 = direction(py, px, n)
                if not self.is_marked_by(y2, x2, player):
                    won = False
                    break
            if won:
                return player
        return None

    def count_sequences(self, length, player=None):
        """
        Conta o numero de sequencias de determinado tamanho de um jogador especifico
        """
        result = 0
        # marked = []
        # for y in range(BOARD_HEIGHT):
        #     for x in range(BOARD_WIDTH):
        #         for direction in OPTIMIZED_DIRECTIONS:
        #             for n in range(1, 5):

        return result

    def check_won(self, player=None):
        """
        Checa se ha uma sequencia valida partindo de cada ponto do tabuleiro
        """
        # for y in range(BOARD_HEIGHT):
        #     for x in range(BOARD_WIDTH):
        #         result = self.won(y, x, player, OPTIMIZED_DIRECTIONS)
        #         if result:
        #             return result
        state = self
        while state and state.last_move:
            result = self.won(state.last_move.y, state.last_move.x, player)
            if result:
                return result
            state = state.parent

    def check_max_sequence(self, player=None):
        """
        Checa a maior sequencia encontrada partindo de cada ponto do tabuleiro
        """
        # mseq = 0
        # for y in range(BOARD_HEIGHT):
        #     for x in range(BOARD_WIDTH):
        #         seq = self.max_sequence(y, x, player, OPTIMIZED_DIRECTIONS)
        #         if seq > mseq:
        #             mseq = seq
        #         if mseq == 5:
        #             break
        #     if mseq == 5:
        #         break
        state = self
        mseq = 0
        while state and state.last_move:
            seq = self.max_sequence(state.last_move.y, state.last_move.x, player)
            if seq > mseq:
                mseq = seq
            if mseq == 5:
                break
            state = state.parent
        return mseq

    def get_next_states(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.is_marked(y, x):
                    continue
                yield self.mark(y, x)


class Display(object):
    __slots__ = ["window", "handlers", "has_colors", "computer_player"]

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
        lines = [s.center(width-2) for line in message.split("\n") for s in textwrap.wrap(line, width-2)]
        for i in range(len(lines)):
            lines[i] = "|".join(["", lines[i], ""])
        lines.insert(0, "="*width)
        lines.append("="*width)
        lines_count = len(lines)
        for i, line in enumerate(lines):
            self.window.addstr((height//2)-((lines_count//2))+i, width, line)

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
        self.handlers.setdefault(event, []).insert(0, fn)

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
            try:
                state = fn(self, state, *args, **kwargs)
            except StopPropagation as e:
                if e.state:
                    state = e.state
                break
        return state

    def select_player(self, state):
        state = state.display("Inform the player you want: \n - X \n - O \n (press in your keyboard)")
        def disable_mouse(_, state, ev, *args, **kwargs):
            state = state.display("Inform the player you want: \n - X \n - O \n (press the key in your keyboard)")
            raise StopPropagation(state)
        def receive_key(_, state, ev, *args, **kwargs):
            ev = ev.upper()
            if ev not in ('X', 'O'):
                return state.display("Please, inform a valid player: X or O")
            self.off(self.MOUSE_EVENT, disable_mouse)
            self.off(self.KEY_EVENT, receive_key)
            state = state.display("You selected the player %s"%ev)
            if ev == 'X':
                self.computer_player = 'O'
                return self.trigger(self.IA_MOVE, state)
            self.computer_player = 'X'
            return state
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
        except curses.error as e:
            curses_err = e
        finally:
            self.close()
        if curses_err:
            print("Curses returned error, so probably your terminal does not support curses or the width/height of your terminal is not suficient to the game run..Please, fix that!")
            print("Original Curses error: %s"%curses_err)

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
        raise StopPropagation(state)
    return state

def run_ia(display, state, *args, **kwargs):
    i = state.get_next_states()
    a = []
    if state.parent.last_move is not None:
        a.append(lambda s: max(ss.max_sequence(ss.last_move.y, ss.last_move.x, state.get_next_player()) for ss in s.get_next_states()))
        # a.append(lambda s: 3-max(sss.max_sequence(s.last_move.y, s.last_move.x, display.computer_player) for ss in s.get_next_states() for sss in ss.get_next_states()))
        # a.append(lambda s: math.sqrt(((state.parent.last_move.y-s.last_move.y)**2)+((state.parent.last_move.x-s.last_move.x)**2)))
    a.append(lambda s: 5-s.max_sequence(s.last_move.y, s.last_move.y, display.computer_player))
    a.append(lambda s: random.randint(0, 10000)) # Just a random factor
    s = min(i, key=lambda s: [c(s) for c in a])
    # Show what's the algorithm choice
    s = s.display(str([c(s) for c in a]))
    # s = s.display(str(s.check_won()))
    # time.sleep(1)

    # s[0] = s[0].display(str(s[0].max_sequence(state.parent.last_move.y, state.parent.last_move.x, display.computer_player)))
    return display.trigger(display.MARK_EVENT, s, s.last_move.y, s.last_move.x)

def should_ia_run(display, state, y, x):
    if state.player == display.computer_player:
        display.draw(state)
        return display.trigger(display.IA_MOVE, state)
    return state

if __name__ == "__main__":
    state = State.get_initial_state()
    display = Display()
    display.on(display.MOUSE_EVENT, process_mouse_click)
    display.on(display.MARK_EVENT, should_ia_run)
    display.on(display.MARK_EVENT, check_won)
    display.on(display.IA_MOVE, run_ia)
    display.loop(state)
