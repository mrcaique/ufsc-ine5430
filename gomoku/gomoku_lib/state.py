# encoding: utf-8
import collections
import copy
import time
from .sequences import Sequences
from .sequence import Sequence
from .constants import BOARD_WIDTH, BOARD_HEIGHT, WINNING_CONDITION, EMPTY, \
                        X_PLAYER, O_PLAYER
from .move import Move
from .exceptions import AlreadyMarked, InvalidLocation
from .utilities import is_valid_position

BaseState = collections.namedtuple(
    "BaseState", ["board", "player", "move_count", "message", "parent",
                  "last_move", "sequences", "started_at"])


class State(BaseState):
    """
    This class represents a state in the gomoku game
    """

    @classmethod
    def get_initial_state(cls):
        return cls(board=tuple(
            tuple(EMPTY for _ in range(BOARD_WIDTH))
            for _ in range(BOARD_HEIGHT)),
                   player=O_PLAYER,
                   started_at=time.time(),
                   move_count=0,
                   message=None,
                   parent=None,
                   last_move=None,
                   sequences=Sequences.get_initial_sequences())

    def get_next_player(self):
        if self.player is X_PLAYER:
            return O_PLAYER
        else:
            return X_PLAYER

    def finished(self):
        """
        Retorna se o jogo ja terminou
        """
        return self.check_won() or \
            self.move_count == BOARD_WIDTH * BOARD_HEIGHT

    def is_valid_position(self, y, x):
        return is_valid_position(y, x)

    def is_marked(self, y, x):
        return self.is_valid_position(y, x) and self.board[y][x] is not EMPTY

    def is_marked_by(self, y, x, player):
        return self.is_valid_position(
            y, x) and player in (X_PLAYER, O_PLAYER) and self.board[y][x] == player

    def display(self, message):
        return State(
            board=self.board,
            started_at=self.started_at,
            move_count=self.move_count,
            player=self.player,
            message=message,
            parent=self,
            last_move=self.last_move,
            sequences=self.sequences)

    def mark(self, y, x):
        if self.is_marked(y, x):
            raise AlreadyMarked(y, x)
        if not is_valid_position(y, x):
            raise InvalidLocation(y, x)
        board = list(self.board)
        board[y] = list(board[y])
        board[y][x] = self.player
        board[y] = tuple(board[y])
        board = tuple(board)
        player = self.get_next_player()
        move = Move(y, x, self.player)
        return State(
            board=board,
            started_at=self.started_at,
            move_count=self.move_count + 1,
            player=player,
            message=self.message,
            parent=self,
            last_move=move,
            sequences=self.sequences.append(self, move))

    def max_sequence(self, py, px, player=None):
        """
        Dado um ponto, checa a maior sequencia possivel que eh possivel
        alcancar partindo deste ponto
        """
        sequences = self.sequences
        if player is not None:
            sequences = sequences.get_by_player(player)
        sequences = sequences.get_by_position(py, px)
        if not sequences:
            return Sequence.get_empty()
        return max(sequences, key=len)

    def won(self, py, px, player=None):
        """
        Checa se ha uma sequencia vencedora a partir de um ponto inicial no
        tabuleiro
        """
        seq = self.max_sequence(py, px, player)
        return len(seq) >= WINNING_CONDITION

    def count_sequences(self, length, player=None):
        """
        Conta o numero de sequencias de determinado tamanho de um jogador
        especifico
        """
        sequences = self.sequences
        if player is not None:
            sequences = sequences.get_by_player(player)
        return len(sequences.get_by_length(length))

    def get_sequences(self):
        return self.sequences

    def check_won(self, player=None):
        """
        Checa se ha uma sequencia vencedora partindo de cada ponto do tabuleiro
        """
        seq = self.check_max_sequence(player)
        return len(seq) >= WINNING_CONDITION

    def check_max_sequence(self, player=None):
        """
        Checa a maior sequencia encontrada partindo de cada ponto do tabuleiro
        """
        sequences = self.sequences
        if player is not None:
            sequences = sequences.get_by_player(player)
        if not sequences:
            return Sequence.get_empty()
        return max(sequences, key=len)

    def get_next_states(self):
        if self.finished():
            return
        moves = []
        c = 100
        if len(self.sequences):
            sequences = self.sequences
            n = 10
            jump = None
            sequences_found = []
            while True:
                sequences = sequences.get_largest_sequences(n, jump)
                sequences = sequences.get_by_not_blocked(self)
                if jump is not None and not len(sequences):
                    # There is nothing to paginate..stop here
                    break
                if len(sequences):
                    sequences_found.extend(sequences)
                    if len(sequences_found) > 10:
                        break
                else:
                    if jump is None:
                        jump = n
                    else:
                        jump += n
                    sequences = self.sequences
            sequences = list(sequences_found)
            sequences.sort(key=lambda seq: (len(seq), seq.player != self.player, -seq.count_blocked(self), seq.count_near_merge(self)), reverse=True)
            if self.last_move:
                sequences.extend((seq for seq in self.sequences.get_by_position(self.last_move.y, self.last_move.x).get_by_not_blocked(self) if seq not in sequences))
            sequences.extend(self.sequences.get_by_not_blocked(self, 1).sequences[:10])
            for sequence in sequences:
                for move in sequence.ends():
                     if (move.y, move.x) not in moves and self.is_valid_position(move.y, move.x) and not self.is_marked(move.y, move.x) and c > 0:
                         yield self.mark(move.y, move.x)
                         moves.append((move.y, move.x))
                         c -= 1

        CENTER_Y, CENTER_X = int(BOARD_HEIGHT/2), int(BOARD_WIDTH/2)
        if self.is_valid_position(CENTER_Y, CENTER_X)  and \
            not self.is_marked(CENTER_Y, CENTER_X) and c > 0:
            yield self.mark(CENTER_Y, CENTER_X)
            moves.append((CENTER_Y, CENTER_X))
            c -= 1
        d = [-1, 1]
        visited = []
        while moves and c > 0:
            move = moves.pop()
            for v in d:
                if c < 0:
                    break
                for h in d:
                    if v == h and v == 0:
                        continue
                    if c < 0:
                        break
                    yn = int(move[0]+v)
                    xn = int(move[1]+h)
                    if not self.is_valid_position(yn, xn)  or \
                        self.is_marked(yn, xn) or \
                        (yn, xn) in visited:
                        continue
                    visited.append((yn, xn))
                    yield self.mark(yn, xn)
