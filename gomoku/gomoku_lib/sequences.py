# encoding: utf-8
import collections
import copy
import bisect
from .constants import BOARD_WIDTH, BOARD_HEIGHT
from .sequence import Sequence
from .utilities import is_valid_position

BaseSequences = collections.namedtuple(
    "BaseSequences",
    ["sequences", "board", "can_append"]
)


class Sequences(BaseSequences):
    @classmethod
    def get_initial_sequences(cls):
        return cls(
            sequences=tuple(),
            board=tuple(
               tuple(tuple() for _ in range(BOARD_WIDTH))
               for _ in range(BOARD_HEIGHT)
            ),
            can_append=True
        )

    def __iter__(self):
        return iter(self.sequences)

    def __len__(self):
        return len(self.sequences)

    def get_by_position(self, py, px):
        """
        Retorna um iterator que contem apenas as sequencias presentes em um
        determinado ponto
        """
        sequences = (
            seq
            for seq in self
            if any(move.y == py and move.x == px for move in seq)
        )
        return Sequences(
            sequences=tuple(sequences), 
            board=None, 
            can_append=False
        )
    
    def get_largest_sequences(self, n, jump=None):
        """
        Retorna as N maiores sequencias, desconsiderando as ultimas JUMP 
        sequencias
        """
        sequences = self.sequences
        if jump is None:
            sequences = sequences[-n:]
        else:
            sequences = sequences[-n-jump:-n]
        return Sequences(
            sequences=sequences, 
            board=None, 
            can_append=False
        )
    

    def get_smallest_sequences(self, n, jump=None):
        """
        Retorna as N menores sequencias, desconsiderando as primeiras JUMP
        sequencias
        """
        sequences = self.sequences
        if jump is None:
            sequences = sequences[:n]
        else:
            sequences = sequences[jump:jump+n]
        return  Sequences(
            sequences=sequences, 
            board=None,
            can_append=False
        )
    

    def get_by_near_merge(self, state, sides, n=None):
        """
        Retorna um iterator que  podem fazer merges em ate "sides" lados, a "n"
        passos de distancia
        """
        sequences = (
            seq for seq in self if seq.count_near_merge(state, n) == sides
        )
        return Sequences(
            sequences=tuple(sequences), 
            board=None,
            can_append=False
        )

    def get_by_sides_blocked(self, state, sides, n=None):
        """
        Retorna um iterator que contem apenas sequencias que tem "sides" lados
        bloqueados numa margem de ate "n" passos
        """
        sequences = (
            seq for seq in self if seq.count_blocked(state, n) == sides
        )
        return Sequences(
            sequences=tuple(sequences),
            board=None,
            can_append=False
        )
    
    def get_by_not_blocked(self, state, n=None):
        """
        Retorna um objeto contendo apenas sequencias que nao estao totalmente 
        bloqueadas numa margem de ate "n" passos
        """
        sequences = (
            seq for seq in self if seq.count_blocked(state, n) < 2
        )
        return Sequences(
            sequences=tuple(sequences),
            board=None,
            can_append=False
        )

    def get_by_player(self, player):
        """
        Retorna um iterator que contem apenas as sequencias de um determinado
        jogador
        """
        sequences = (sequence for sequence in self
                     if sequence.player in player)
        return Sequences(
            sequences=tuple(sequences),
            board=None,
            can_append=False
        )

    def get_by_length(self, length):
        """
        Retorna um iterator que retorna apenas as sequencias com o tamanho
        especificado
        """
        sequences = (sequence for sequence in self if len(sequence) == length)
        return Sequences(
            sequences=tuple(sequences),
            board=None,
            can_append=False
        )

    def append(self, state, move):
        if not self.can_append:
            raise TypeError("Cannot append to a filtered Sequences object")
        sequences = list(self.sequences)
        # board = copy.copy(self.board)
        board = list(self.board)
        local_sequences = list(board[move.y][move.x])
        new_local_sequences = []
        # Consider adding the move to the sequences in the point already listed
        for sequence in local_sequences:
            if sequence.player != move.player:
                # The player of the move does not match the player of the
                # sequence..so ignore that sequence
                continue
            seq = sequence.append(move)
            assert seq != sequence, \
                "{} should modify {} when added to it, but it didn't".format(
                    move, sequence
                )
            sequence_move = sequence.bottom_end()
            if sequence_move != move:
                sequence_move = sequence.top_end()
            assert sequence_move == move, \
                ("{} does not match {}, " +
                 "so {} should not be in the {} position").format(
                    sequence_move, move, sequence_move, move
                )
            assert sequence in sequences, "{} is not in sequences list".format(
                sequence
            )
            # Remove the old sequence from the sequences list..
            sequences.remove(sequence)
            # Remove the old sequence from all the old positions
            for end in sequence.ends():
                if not state.is_valid_position(end.y, end.x):
                    continue
                y, x = end.y, end.x
                board[y] = list(board[y])
                board[y][x] = list(board[y][x])
                board[y][x].remove(sequence)
                board[y][x] = tuple(board[y][x])
                board[y] = tuple(board[y])
            # for seqmov in sequence:
            #     y, x = seqmov.y, seqmov.x
            #     assert sequence in board[y][x]
            #     board[y] = list(board[y])
            #     board[y][x] = list(board[y][x])
            #     board[y][x].remove(sequence)
            #     board[y][x] = tuple(board[y][x])
            #     board[y] = tuple(board[y])
            # Add the new sequence to the new lists..
            bisect.insort(sequences, seq)
            new_local_sequences.append(seq)
            # Add the new sequence to the new positions..
            for end in seq.ends():
                if not state.is_valid_position(end.y, end.x):
                    continue
                y, x = end.y, end.x
                board[y] = list(board[y])
                board[y][x] = list(board[y][x])
                board[y][x].append(seq)
                board[y][x] = tuple(board[y][x])
                board[y] = tuple(board[y])
            # for seqmov in seq:
            #     y, x = seqmov.y, seqmov.x
            #     assert seq not in board[y][x]
            #     board[y] = list(board[y])
            #     board[y][x] = list(board[y][x])
            #     board[y][x].append(seq)
            #     board[y][x] = tuple(board[y][x])
            #     board[y] = tuple(board[y])
        # Locate new "sequences" related to that move that can be considered..
        for sequence in Sequence.get_for_move(move):
            if sequence in new_local_sequences:
                continue
            bisect.insort(sequences, sequence)
            new_local_sequences.append(sequence)
            for end in sequence.ends():
                if not state.is_valid_position(end.y, end.x):
                    continue
                y, x = end.y, end.x
                board[y] = list(board[y])
                board[y][x] = list(board[y][x])
                board[y][x].append(sequence)
                board[y][x] = tuple(board[y][x])
                board[y] = tuple(board[y])
            # for seqmov in sequence:
            #     y, x = seqmov.y, seqmov.x
            #     assert sequence not in board[y][x]
            #     board[y] = list(board[y])
            #     board[y][x] = list(board[y][x])
            #     board[y][x].append(sequence)
            #     board[y][x] = tuple(board[y][x])
            #     board[y] = tuple(board[y])
        # Here, we filter possible sequences that can be merged with the move..
        seq_groups = {}
        for seq in new_local_sequences:
            # Group the sequences by directions :D
            seq_groups.setdefault(seq.directions, []).append(seq)
        seq_groups = seq_groups.values()
        # Well..if we want merges, we need to have more than a sequence in the
        # group..(grouped by directions)
        seq_groups = [seq_group for seq_group in seq_groups
                      if len(seq_group) > 1]
        for seq_group in seq_groups:
            merged = None
            seq = None
            while seq_group:
                seq = seq_group.pop()
                # Remove the old sequence that will be added to the merge from
                # the sequences list
                assert seq in sequences, \
                    ("{} should be in sequences list.." +
                     "but it does not exist in that list").format(seq)
                sequences.remove(seq)
                # Remove the endings of the old sequence that will be merged
                for end in seq.ends():
                    if not state.is_valid_position(end.y, end.x):
                        continue
                    y, x = end.y, end.x
                    board[y] = list(board[y])
                    board[y][x] = list(board[y][x])
                    assert seq in board[y][x], \
                        ("{} should have end in {} but it does not " +
                         "exist in it").format(
                            seq, end
                        )
                    board[y][x].remove(seq)
                    board[y][x] = tuple(board[y][x])
                    board[y] = tuple(board[y])
                # for seqmov in seq:
                #     y, x = seqmov.y, seqmov.x
                #     assert seq in board[y][x]
                #     board[y] = list(board[y])
                #     board[y][x] = list(board[y][x])
                #     board[y][x].remove(seq)
                #     board[y][x] = tuple(board[y][x])
                #     board[y] = tuple(board[y])
                if merged is None:
                    merged = seq
                    continue
                # Merge the sequence \o/
                new_merged = merged.merge(seq)
                assert new_merged != merged, \
                    (("{} when merged with {} should change, but it does not " +
                     "caused it to..").format(merged, seq))
                merged = new_merged
            if merged is not None:
                # Add the merged sequence to the sequences list...
                bisect.insort(sequences, merged)
                # ... and add it's endings to the positions..
                for end in merged.ends():
                    if not state.is_valid_position(end.y, end.x):
                        continue
                    y, x = end.y, end.x
                    board[y] = list(board[y])
                    board[y][x] = list(board[y][x])
                    board[y][x].append(merged)
                    board[y][x] = tuple(board[y][x])
                    board[y] = tuple(board[y])
                # for seqmov in merged:
                #     y, x = seqmov.y, seqmov.x
                #     assert merged not in board[y][x]
                #     board[y] = list(board[y])
                #     board[y][x] = list(board[y][x])
                #     board[y][x].append(merged)
                #     board[y][x] = tuple(board[y][x])
                #     board[y] = tuple(board[y])
        # Return the new Sequences object..
        return Sequences(
            sequences=tuple(sequences), 
            board=tuple(board),
            can_append=True
        )
