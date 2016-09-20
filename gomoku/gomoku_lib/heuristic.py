def evaluate_full_sequence(state, computer, player):
    result = 0
    if player is not None:
        seq = player.get_by_length(5)
        if len(seq):
            return -1000
        seq = player.get_by_length(4)
        if len(seq):
            free = len(seq.get_by_sides_blocked(state, 0))
            if free:
                return -5000
            half_blocked = len(seq.get_by_sides_blocked(state, 1))
            if half_blocked:
                result += 5000*half_blocked
        seq = player.get_by_length(3)
        if len(seq):
            free = len(seq.get_by_sides_blocked(state, 0))
            free *= (len(seq.get_by_near_merge(state, 2))+1)
            free *= (len(seq.get_by_near_merge(state, 1))+1)
            if free:
                result -= 2500*free
            half_blocked = len(seq.get_by_sides_blocked(state, 1))
            if half_blocked:
                result += 1000*half_blocked
        seq = player.get_by_length(2)
        if len(seq):
            free = len(seq.get_by_sides_blocked(state, 0))
            free *= (len(seq.get_by_near_merge(state, 2))+1)
            free *= (len(seq.get_by_near_merge(state, 1))+1)
            if free:
                result -= 500*free
            half_blocked = len(seq.get_by_sides_blocked(state, 1))
            if half_blocked:
                result += 250*half_blocked
    seq = computer.get_by_length(5)
    if len(seq):
        return 10000*len(seq)
    seq = computer.get_by_length(4)
    if len(seq):
        free = len(seq.get_by_sides_blocked(state, 0))
        free *= (len(seq.get_by_near_merge(state, 2))+1)
        free *= (len(seq.get_by_near_merge(state, 1))+1)
        if free:
            result += 10000*free
        half_blocked = len(seq.get_by_sides_blocked(state, 1))
        if half_blocked:
            result -= 500*half_blocked
    seq = computer.get_by_length(3)
    if len(seq):
        free = len(seq.get_by_sides_blocked(state, 0))
        free *= (len(seq.get_by_near_merge(state, 2))+1)
        free *= (len(seq.get_by_near_merge(state, 1))+1)
        if free:
            result += 250*free
        half_blocked = len(seq.get_by_sides_blocked(state, 1))
        if half_blocked:
            result -= 100*half_blocked
    seq = computer.get_by_length(2)
    if len(seq):
        free = seq.get_by_sides_blocked(state, 0)
        free *= (len(seq.get_by_near_merge(state, 2))+1)
        free *= (len(seq.get_by_near_merge(state, 1))+1)
        if len(free):
            result += 10*len(free)
        half_blocked = len(seq.get_by_sides_blocked(state, 1))
        if half_blocked:
            result -= 5*half_blocked
    seq = computer.get_by_length(1)
    if len(seq):
        free = len(seq.get_by_sides_blocked(state, 0))
        if free:
            result += free*2
        half_blocked = len(seq.get_by_sides_blocked(state, 1))
        if half_blocked:
            result -= half_blocked*2
    return result

def evaluate_player(state):
    result = 0
    return result

def evaluate(state):
    sequences = state.get_sequences()
    local = sequences.get_by_position(state.last_move.y, state.last_move.x)
    computer = sequences.get_by_player(state.last_move.player)
    player = sequences.get_by_player(state.player)
    result_computer = evaluate_full_sequence(state, player, computer)
    return result_computer
