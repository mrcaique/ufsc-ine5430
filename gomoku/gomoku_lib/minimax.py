from .heuristic import evaluate


def minimax(state, depth, alpha, beta, is_player):
    finished = object()
    next_states = state.get_next_states()

    best_state = None
    next_state = next(next_states, finished)

    if depth == 0 or next_state is finished:
        value = evaluate(state)
        return value, state
    else:
        while next_state is not finished:
            if is_player:
                value, _ = minimax(next_state, depth - 1, alpha, beta, False)
                if value > alpha:
                    alpha = value
                    best_state = next_state
            else:
                value, _ = minimax(next_state, depth - 1, alpha, beta, True)
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
