# encoding: utf-8
import collections
from .constants import ALL_DIRECTIONS
BaseSequence = collections.namedtuple("BaseSequence", ["moves", "directions"])
class Sequence(BaseSequence):
    def __eq__(self, other):
        if not isinstance(other, Sequence):
            raise TypeError("Cannot compare Sequence with %s"%type(other))
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
            assert seq != sequence, "{} should modify {} when added to it, but it didn't".format(move, sequence)
            sequence = seq
        return sequence

    def append(self, move):
        if move.player != self.player or move in self.moves:
            return self
        if self.match_start(move):
            return Sequence(
                tuple([move]+list(self.moves)),
                self.directions
            )
        elif self.match_end(move):
            return Sequence(
                tuple(list(self.moves)+[move]),
                self.directions
            )
        return self

    @property
    def player(self):
        return self.moves[0].player

    @classmethod
    def get_for_move(cls, move):
        for directions in zip(ALL_DIRECTIONS[::2], ALL_DIRECTIONS[1::2]):
            yield cls((move,), directions)

    def __repr__(self):
        return "Sequence(moves={})".format(self.moves)
