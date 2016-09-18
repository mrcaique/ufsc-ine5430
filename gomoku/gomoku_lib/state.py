# encoding: utf-8
import collections, copy
from .sequences import Sequences
from .constants import BOARD_WIDTH, BOARD_HEIGHT
from .move import Move
from .exceptions import AlreadyMarked

BaseState = collections.namedtuple(
    "BaseState",
    ["board", "player", "message", "parent", "last_move", "sequences"]
)

class State(BaseState):
    """
    This class represents a state in the gomoku game
    """

    @classmethod
    def get_initial_state(cls):
        return cls(
            board=tuple(tuple("+" for _ in range(BOARD_WIDTH)) for _ in range(BOARD_HEIGHT)),
            player="O",
            message=None,
            parent=None,
            last_move=None,
            sequences=Sequences.get_initial_sequences()
        )

    def get_next_player(self):
        if self.player == "X":
            return "O"
        else:
            return "X"

    def is_valid_position(self, y, x):
        return y >= 0 and x >= 0 and y < BOARD_HEIGHT and x < BOARD_WIDTH

    def is_marked(self, y, x):
        return self.is_valid_position(y, x) and self.board[y][x] in ("X", "O")

    def is_marked_by(self, y, x, player):
        return self.is_valid_position(y, x) and player in ("X", "O") and self.board[y][x] == player

    def display(self, message):
        return State(
            board = self.board,
            player = self.player,
            message = message,
            parent = self,
            last_move = self.last_move,
            sequences = self.sequences
        )

    def mark(self, y, x):
        if self.is_marked(y, x):
            raise AlreadyMarked(y, x)
        if y >= BOARD_HEIGHT or y < 0 or x >= BOARD_WIDTH or x < 0:
            raise InvalidLocation(y, x)
        board = copy.copy(self.board)
        board = list(board)
        board[y] = list(board[y])
        board[y][x] = self.player
        board[y] = tuple(board[y])
        board = tuple(board)
        player = self.get_next_player()
        move = Move(y, x, self.player)
        return State(
            board = board,
            player = player,
            message = self.message,
            parent = self,
            last_move = move,
            sequences = self.sequences.append(self, move)
        )

    def max_sequence(self, py, px, player=None):
        """
        Dado um ponto, checa a maior sequencia possivel que eh possivel alcancar
        partindo deste ponto
        """
        sequences = self.sequences
        if player is not None:
            sequences = sequences.get_by_player(player)
        sequences = sequences.get_by_position(py, px)
        if not sequences:
            return 0
        return max(sequences, key=len)

    def won(self, py, px, player=None):
        """
        Checa se ha uma sequencia vencedora a partir de um ponto inicial no tabuleiro
        """
        seq = self.max_sequence(py, px, player)
        if len(seq) >= 5:
            return seq.player

    def count_sequences(self, length, player=None):
        """
        Conta o numero de sequencias de determinado tamanho de um jogador especifico
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
        if seq >= 5:
            return seq.player

    def check_max_sequence(self, player=None):
        """
        Checa a maior sequencia encontrada partindo de cada ponto do tabuleiro
        """
        sequences = self.sequences
        if player is not None:
            sequences = sequences.get_by_player(player)
        if not sequences:
            return 0
        return max(sequences, key=len)

    def get_next_states(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.is_marked(y, x):
                    continue
                yield self.mark(y, x)
