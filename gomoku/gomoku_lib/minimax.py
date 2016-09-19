from .heuristic import evaluate

def minimax(state, depth, alpha, beta, is_player):
    next_states = list(state.get_next_states())

    best_state = None

    if depth == 0 or not next_states:
        value = evaluate(state)
        return value, best_state
    else:
        for next_state in next_states:
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
    if is_player:
        return alpha, best_state
    else:
        return beta, best_state

