# encoding: utf-8
import collections
from .constants import ALL_DIRECTIONS

BaseMove = collections.namedtuple("BaseMove", ["y", "x", "player"])

class Move(BaseMove):
    def neighborhood(self):
        for direction in ALL_DIRECTIONS:
            yield self.apply_direction(direction)
    def apply_direction(self, direction, n=1):
        assert direction in ALL_DIRECTIONS
        y, x = direction(self.y, self.x, n)
        return Move(y, x, self.player)
