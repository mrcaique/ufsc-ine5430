# encoding: utf-8
BOARD_WIDTH = 15
BOARD_HEIGHT = 15

ALL_DIRECTIONS = (
    lambda y, x, n: [y, x-n],   # Esquerda
    lambda y, x, n: [y, x+n],   # Direita
    lambda y, x, n: [y-n, x],   # Superior
    lambda y, x, n: [y+n, x],   # Inferior
    lambda y, x, n: [y-n, x-n], # Diagonal Superior Esquerda
    lambda y, x, n: [y+n, x+n], # Diagonal Inferior Direita
    lambda y, x, n: [y-n, x+n], # Diagonal Superior Direita
    lambda y, x, n: [y+n, x-n]  # Diagonal Inferior Esquerda
)

###############################################
# Estas direcoes so devem ser usadas no caso ##
# de estar varrendo toda a matriz            ##
###############################################
OPTIMIZED_DIRECTIONS = (
    # lambda y, x, n: [y, x-n], # Esquerda
    lambda y, x, n: [y, x+n], # Direita
    # lambda y, x, n: [y-n, x], # Superior
    lambda y, x, n: [y+n, x], # Inferior
    # lambda y, x, n: [y-n, x-n], # Diagonal Superior Esquerda
    lambda y, x, n: [y+n, x+n], # Diagonal Inferior Direita
    # lambda y, x, n: [y-n, x+n], # Diagonal Superior Direita
    lambda y, x, n: [y+n, x-n] # Diagonal Inferior Esquerda
)
