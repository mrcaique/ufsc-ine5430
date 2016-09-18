# encoding: utf-8
from gomoku_lib.display import  Display
from gomoku_lib.state import State
from gomoku_lib.events import Mouse
from gomoku_lib.exceptions import StopPropagation, Quit

__all__ = ["Display", "State"]


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

def run_ai(display, state, *args, **kwargs):
    i = state.get_next_states()
    a = []
    if state.parent.last_move is not None:
        a.append(lambda s: 1000*len(s.check_max_sequence(state.get_next_player())))
        # a.append(lambda s: 3-max(sss.max_sequence(s.last_move.y, s.last_move.x, display.computer_player) for ss in s.get_next_states() for sss in ss.get_next_states()))
        # a.append(lambda s: math.sqrt(((state.parent.last_move.y-s.last_move.y)**2)+((state.parent.last_move.x-s.last_move.x)**2)))

    a.append(lambda s: -1000*len(s.check_max_sequence(display.computer_player)))
    s = min(i, key=lambda s: [c(s) for c in a])
    # Show what's the algorithm choice
    s = s.display(str([c(s) for c in a]))
    # s = s.display(str(s.check_won()))
    # time.sleep(1)

    # s[0] = s[0].display(str(s[0].max_sequence(state.parent.last_move.y, state.parent.last_move.x, display.computer_player)))
    return display.trigger(display.MARK_EVENT, s, s.last_move.y, s.last_move.x)

def should_ia_run(display, state, y, x):
    if state.player == display.computer_player:
        # Update the screen so the user sees the click instantly..
        display.draw(state)
        return display.trigger(display.IA_MOVE, state)
    return state
state = State.get_initial_state()
display = Display()
display.on(display.MOUSE_EVENT, process_mouse_click)
display.on(display.MARK_EVENT, should_ia_run)
display.on(display.MARK_EVENT, check_won)
display.on(display.IA_MOVE, run_ai)
display.loop(state)
