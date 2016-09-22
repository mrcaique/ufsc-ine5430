from .heuristic import evaluate as evaluate_heuristic
from .utility import evaluate as evaluate_utility

def minimax(player, state, depth, alpha, beta, is_player):
    finished = object()
    next_states = state.get_next_states()

    best_state = None
    next_state = next(next_states, finished)

    if depth == 0 or next_state is finished:
        if depth == 0:
            value = evaluate_heuristic(player, state)
        else:
            value = evaluate_utility(player, state)
        return value, state
    while next_state is not finished:
        if is_player:
            value, _ = minimax(player, next_state, depth - 1, alpha, beta, False)
            if value > alpha:
                alpha = value
                best_state = next_state
        else:
            value, _ = minimax(player, next_state, depth - 1, alpha, beta, True)
            if value < beta:
                beta = value
                best_state = next_state
        if alpha >= beta:
            break
        next_state = next(next_states, finished)
    if is_player:
        return alpha, best_state
    else:
        return beta, best_state
