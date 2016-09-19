# encoding: utf-8


class GameWarning(Exception):
    """
    Essa exceção é emitida quando um aviso a respeito do jogo deve ser emitida
    """
    pass


class InvalidLocation(GameWarning):
    """
    Essa exceção é emitida quando uma posição é inválida
    """

    def __init__(self, y, x):
        super(InvalidLocation, self).__init__(
            "Position y={} and x={} is not a valid position".format(y, x))


class AlreadyMarked(GameWarning):
    """
    Essa excecao é emitida quando uma posição no tabuleiro já está marcada
    """

    def __init__(self, y, x):
        super(AlreadyMarked, self).__init__(
            "Position y={} and x={} is already marked".format(y, x))


class StopPropagation(Exception):
    """
    Emitir essa exceção faz um evento parar de executar os próximos handlers
    """

    def __init__(self, state=None):
        """
        Use o parametro state para setar o novo estado da aplicação.
        """
        super(StopPropagation, self).__init__("StopPropagation")
        self.state = state


class Quit(Exception):
    """
    Emitir essa exceção faz o programa terminar sua execucao
    """
    pass
