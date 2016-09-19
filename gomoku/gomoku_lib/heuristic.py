def evaluate(state):
    mseq = len(state.check_max_sequence(state.player))
    #maseq = state.check_max_sequence(state.get_next_player)
    h = state.count_sequences(mseq, state.player) 
    
    if mseq == 2:
        h *= 5
    elif mseq == 3:
        h *= 100
    elif mseq == 4:
        h *= 100000
    elif mseq == 5:
        h *= 100000000
        
    return h

