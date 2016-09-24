# First level: length
# Second level: If the sequence is blocked
# Third level: If there is a merge
HEURISTIC = {
    1: {
        0: {
            0: 6e2,
            1: 4e2,
            2: 2e2
        },
        1: {
            0: 2e2,
            1: 6e2
        },
        2: {
            0: 32e2
        }
    },
    2: {
        0: {
            0: 8e4,
            1: 4e4,
            2: 2e4
        },
        1: {
            0: 2e4,
            1: 6e4
        },
        2: {
            0: 64e4
        }
    },
    3: {
        0: {
            0: 6e8,
            1: 4e8,
            2: 1e8
        },
        1: {
            0: 2e8,
            1: 6e8
        },
        2: {
            0: 128e8
        }
    },
    4: {
        0: {
            0: 6e16,
            1: 4e16,
            2: 1e16
        },
        1: {
            0: 2e16,
            1: 6e16
        },
        2: {
            0: 64e16
        }
    },
    5: {
        0: {
            0: 6e32,
            1: 4e32,
            2: 1e32
        },
        1: {
            0: 2e32,
            1: 6e32
        },
        2: {
            0: 32e32
        }
    },
    6: {
        0: {
            0: 6e32,
            1: 4e32,
            2: 1e32
        },
        1: {
            0: 2e32,
            1: 6e32
        },
        2: {
            0: 3e32
        }
    },
    7: {
        0: {
            0: 6e32,
            1: 4e32,
            2: 1e32
        },
        1: {
            0: 6e32,
            1: 2e32
        },
        2: {
            0: 3e32
        }
    },
    8: {
        0: {
            0: 1e32,
            1: 4e32,
            2: 6e32
        },
        1: {
            0: 8e32,
            1: 2e32
        },
        2: {
            0: 3e32
        }
    },
    9: {
        0: {
            0: 1e32,
            1: 4e32,
            2: 6e32
        },
        1: {
            0: 8e32,
            1: 2e32
        },
        2: {
            0: 3e32
        }
    },
}
def evaluate_sequence_length(sequence):
    l = len(sequence)
    return 8*(10**l)

def evaluate_sequence_blocking(state, sequence):
    sides_blocked = sequence.count_blocked(state)
    if sides_blocked == 2:
        return 1
    elif sides_blocked == 1:
        return 4
    else:
        return 128

def evaluate_sequence_merging(state, sequence):
    sides_merged = sequence.count_near_merge(state)
    if sides_merged == 2:
        return 4
    elif sides_merged == 1:
        return 8
    else:
        return 16

def evaluate_sequence(state, sequences, sequence):
    l = len(sequence)
    sides_merged = sequence.count_near_merge(state)
    sides_blocked = sequence.count_blocked(state)
    # return HEURISTIC[l][sides_blocked][sides_merged]
    return evaluate_sequence_length(sequence) * \
        (evaluate_sequence_merging(state, sequence) * \
        evaluate_sequence_blocking(state, sequence))

def evaluate(player, state):
    sequences = state.get_sequences()
    if state.player == player:
        next_player = state.last_move.player
    else:
        next_player = state.player
    computer = sequences.get_by_player(player)
    player = sequences.get_by_player(next_player)
    cresult = sum(evaluate_sequence(state, computer, seq) for seq in computer)
    # cresult = cresult/float(len(computer))
    cplayer = sum(evaluate_sequence(state, player, seq) for seq in player)
    # cplayer = cplayer/float(len(player))
    result = cresult-(cplayer*2)
    return int(result/float(state.move_count))
