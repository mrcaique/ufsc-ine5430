def evaluate(player, state):
    sequences = state.get_sequences()
    if state.player == player:
        next_player = state.last_move.player
    else:
        next_player = state.player
    computer = sequences.get_by_player(player)
    player = sequences.get_by_player(next_player)
    
    pseq = len(player)
    cseq = len(computer)
    pmax = len(max(player, key=len))
    cmax = len(max(computer, key=len))
    
    if pseq > cseq:
        utlty = 100000
    else:
        utlty = 1000
    
    utlty /= float(state.move_count)
        
    if not state.check_won(player):
        utlty *= -1
    elif state.check_won(player):
        utlty *= 1
    else:
        utlty *= 0

    return utlty