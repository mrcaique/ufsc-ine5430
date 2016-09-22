# encoding: utf-8
import collections
import copy
import time
from .sequences import Sequences
from .sequence import Sequence
from .constants import BOARD_WIDTH, BOARD_HEIGHT, WINNING_CONDITION
from .move import Move
from .exceptions import AlreadyMarked

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
            tuple("+" for _ in range(BOARD_WIDTH))
            for _ in range(BOARD_HEIGHT)),
                   player="O",
                   started_at=time.time(),
                   move_count=0,
                   message=None,
                   parent=None,
                   last_move=None,
                   sequences=Sequences.get_initial_sequences())

    def get_next_player(self):
        if self.player == "X":
            return "O"
        else:
            return "X"

    def finished(self):
        """
        Retorna se o jogo ja terminou
        """
        return self.check_won() or \
            self.move_count == BOARD_WIDTH * BOARD_HEIGHT

    def is_valid_position(self, y, x):
        return y >= 0 and x >= 0 and y < BOARD_HEIGHT and x < BOARD_WIDTH

    def is_marked(self, y, x):
        return self.is_valid_position(y, x) and self.board[y][x] in ("X", "O")

    def is_marked_by(self, y, x, player):
        return self.is_valid_position(
            y, x) and player in ("X", "O") and self.board[y][x] == player

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
        if y >= BOARD_HEIGHT or y < 0 or x >= BOARD_WIDTH or x < 0:
            raise InvalidLocation(y, x)
        #board = copy.copy(self.board)
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
        sequences = self.sequences
        # sequences = sorted(sequences, key=lambda seq: len, reverse=True)
        if sequences and len(sequences[0]) >= len(sequences[-1]) and len(sequences[-1]) == 1:
            sequences = [seq for seq in sequences if len(seq) > 1]
        for sequence in sequences: 
            moves.extend((move.y, move.x) for move in sequence.ends() if (move.y, move.x) not in moves and self.is_valid_position(move.y, move.x))
        if not moves:
           moves.append((int(BOARD_HEIGHT/2), int(BOARD_WIDTH/2)))
        # moves = moves[:10]
        d = [-1, 0, 1]
        visited = []
        # We scan the possible movements first..:)
        for move in moves:
            xn = int(move[1])
            yn = int(move[0])
            if self.is_marked(yn, xn) or \
                not self.is_valid_position(yn, xn) or \
                (yn, xn) in visited:
                continue
            visited.append((yn, xn))
            yield self.mark(yn, xn)
        # And after scanning the possible movements we scan the neighborhood :)
        for move in moves:
            for v in d:
                for h in d:
                    yn = int(move[0]+v)
                    xn = int(move[1]+h)
                    if not self.is_valid_position(yn, xn)  or \
                        self.is_marked(yn, xn) or \
                        (yn, xn) in visited:
                        continue
                    visited.append((yn, xn))
                    yield self.mark(yn, xn)
            # for y in range(1, 3):
            #     for v in d:
            #         yn = int(move[0]+(y*v))
            #         if not self.is_valid_position(yn, 0):
            #             # If out of bound vertically, we let the program jump
            #             # All the x range...
            #             continue
            #         for x in range(1, 3):
            #             for h in d:
            #                 xn = int(move[1]+(x*h))
            #                 if not self.is_valid_position(yn, xn)  or \
            #                     self.is_marked(yn, xn) or \
            #                     (yn, xn) in visited:
            #                     continue
            #                 visited.append((yn, xn))
            #                 yield self.mark(yn, xn)
