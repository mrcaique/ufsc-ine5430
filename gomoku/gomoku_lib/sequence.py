# encoding: utf-8
import collections
from .constants import ALL_DIRECTIONS
BaseSequence = collections.namedtuple("BaseSequence", ["moves", "directions"])


class Sequence(BaseSequence):
    def __eq__(self, other):
        if not isinstance(other, Sequence):
            raise TypeError("Cannot compare Sequence with %s" % type(other))
        if self.directions != other.directions:
            return False
        return all(move in other.moves for move in self.moves) or \
            all(move in self.moves for move in other.moves)

    def __len__(self):
        return len(self.moves)

    def __iter__(self):
        return iter(self.moves)

    def match_start(self, move):
        return self.bottom_end() == move

    def match_end(self, move):
        return self.top_end() == move

    def match(self, move):
        return move in self.ends()

    def ends(self):
        yield self.bottom_end()
        yield self.top_end()

    def bottom_end(self):
        return self.moves[0].apply_direction(self.directions[0])

    def top_end(self):
        return self.moves[-1].apply_direction(self.directions[-1])

    def can_merge_start(self, other):
        return self.directions == other.directions and \
            self.moves[0] == other.moves[-1]

    def can_merge_end(self, other):
        return self.directions == other.directions and \
            self.moves[-1] == other.moves[0]

    def can_merge(self, other):
        return (self.can_merge_start(other) or self.can_merge_end(other))

    def merge(self, other):
        if not self.can_merge(other):
            return self
        sequence = self
        moves = other.moves
        if self.can_merge_start(other):
            # We need to invert the order of the movements so we can join the
            # sequences naturally..
            moves = moves[::-1]
        # We ignore the first piece because it's the merge point
        moves = moves[1:]
        for move in moves:
            seq = sequence.append(move)
            assert seq != sequence, \
                "{} should modify {} when added to it, but it didn't".format(
                    move, sequence
                )
            sequence = seq
        return sequence

    def is_top_blocked(self, state, n):
        bottom = self.moves[0]
        top = self.moves[-1]
        top_move = self.directions[-1]
        player = self.player
        for i in range(n):
            top = top.apply_direction(top_move)
            if not state.is_valid_position(top.y, top.x):
                return True
            if state.is_marked(top.y, top.x) and not \
                    state.is_marked_by(top.y, top.x, player):
                return True
        return False

    def is_bottom_blocked(self, state, n):
        bottom = self.moves[0]
        bottom_move = self.directions[0]
        player = self.player
        for i in range(n):
            bottom = bottom.apply_direction(bottom_move)
            if not state.is_valid_position(bottom.y, bottom.x):
                return True
            if state.is_marked(bottom.y, bottom.x) and not \
                    state.is_marked_by(bottom.y, bottom.x, player):
                return True
        return False

    def is_blocked(self, state, n):
        """
        Retorna verdadeiro se este jogo estiver bloqueado em n casas na direcao
        proposta
        """
        return self.is_top_blocked(state, n) and \
            self.is_bottom_blocked(state, n)

    def append(self, move):
        if move.player != self.player or move in self.moves:
            return self
        if self.match_start(move):
            return Sequence((move, ) + self.moves, self.directions)
        elif self.match_end(move):
            return Sequence(self.moves + (move, ), self.directions)
        return self

    @property
    def player(self):
        return self.moves[0].player

    @classmethod
    def get_for_move(cls, move):
        for directions in zip(ALL_DIRECTIONS[::2], ALL_DIRECTIONS[1::2]):
            yield cls((move, ), directions)

    @classmethod
    def get_empty(cls):
        return cls(tuple(), tuple())

    def __repr__(self):
        return "Sequence(moves={})".format(self.moves)
