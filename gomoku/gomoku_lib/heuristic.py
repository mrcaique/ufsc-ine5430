def evaluate_sequence_length(sequence):
    l = len(sequence)
    if l >= 5:
        return 1e8
    if l == 4:
        return 1e5 
    if l == 3:
        return 1e3
    if l == 2:
        return 1e2 
    return 1e1

def evaluate_sequence_blocking(state, sequence):
    sides_blocked = sequence.count_blocked(state)
    l = len(sequence)
    if sides_blocked == 2:
        return -2
    elif sides_blocked == 1:
        return -4
    elif sides_blocked == 0:
        return 16

def evaluate_sequence_merging(state, sequence):
    l = len(sequence)
    sides_merged = sequence.count_near_merge(state)
    if sides_merged == 2:
        return 8
    elif sides_merged == 1:
        return 4
    elif sides_merged == 0:
        return 2
    
def evaluate_sequence(state, sequences, sequence):
    return (evaluate_sequence_length(sequence)*evaluate_sequence_blocking(state, sequence))*evaluate_sequence_merging(state, sequence)

def evaluate(player, state):
    sequences = state.get_sequences()
    if state.player == player:
        next_player = state.last_move.player
    else:
        next_player = state.player
    computer = sequences.get_by_player(player)
    player = sequences.get_by_player(next_player)
    cresult = sum(evaluate_sequence(state, computer, seq) for seq in computer)
    #cresult = cresult/float(len(computer))
    cplayer = sum(evaluate_sequence(state, player, seq) for seq in player)
    #cplayer = cplayer/float(len(player))
    result = cresult-cplayer
    return int(result/float(state.move_count))
