import numpy as np
RED = [1, 0, 0]
GREEN = [0, 1, 0]
BLUE = [0, 0, 1]

CYAN = [0, 1, 1]
MAGENTA = [1, 0, 1]
YELLOW = [1, 1, 0]

WHITE = [1, 1, 1]
BLACK = [0, 0, 0]

GRAY = [0.5, 0.5, 0.5]
ORANGE = [1, 0.5, 0]
BROWN = [0.5, 0.25, 0]
LIGHT_BLUE = [0.5, 0.5, 1]
DARK_BLUE = [0, 0, 0.5]

Axes = {
    'position': [
        -10, 0, 0,
        10, 0, 0,
        0, -10, 0,
        0, 10, 0,
        0, 0, -10,
        0, 0, 10],
    'color': [
        *RED,
        *RED,
        *GREEN,
        *GREEN,
        *BLUE,
        *BLUE
    ]
}


Capsule = {
    'position': [
        -0.5, 0.5, 0.0,
        0.5, 0.5, 0.0,
        -0.5, -0.5, 0.0,
        0.5, -0.5, 0.0,
        0.0, 0.5, 0.0,
        0.0, -0.5, 0.0,
        -3/8, 0.72, 0.0,
        -1/8, 0.87, 0.0,
        1/8, 0.87, 0.0,
        3/8, 0.72, 0.0,
        -3/8, -0.72, 0.0,
        -1/8, -0.87, 0.0,
        1/8, -0.87, 0.0,
        3/8, -0.72, 0.0,
        -0.45, 0.62, 0.0,  # 14
        -0.45, -0.62, 0.0,
        -0.25, 0.83, 0.0,  # 16
        -0.25, -0.83, 0.0,
        0.25, 0.83, 0.0,  # 18
        0.25, -0.83, 0.0,
        0.45, 0.62, 0.0,  # 20
        0.45, -0.62, 0.0,
        0.0, 0.89, 0.0,  # 22
        0.0, -0.89, 0.0

    ],
    'indices': [
        0, 2, 3,
        0, 3, 1,
        0, 4, 14,
        14, 4, 6,
        6, 4, 16,
        16, 4, 7,
        7, 4, 22,
        22, 4, 8,
        8, 4, 18,
        18, 4, 9,
        9, 4, 20,
        20, 4, 1,
        2, 5, 15,
        15, 5, 10,
        10, 5, 17,
        17, 5, 11,
        11, 5, 23,
        23, 5, 12,
        12, 5, 19,
        19, 5, 13,
        13, 5, 21,
        21, 5, 3
    ],
    'color': [1, 0.5, 1]*24
}

Triangle = {
    'position': [
        -0.5, -0.5, 0.0,
        0.5, -0.5, 0.0,
        0.0,  0.5, 0.0],

    'color': [
        *RED,
        *GREEN,
        *BLUE
    ]
}

Square = {
    'position': [
        -0.5, 0.5, 0.0,
        0.5, 0.5, 0.0,
        0.5, -0.5, 0.0,
        -0.5, -0.5, 0.0
    ],
    'indices': [
        0, 1, 2,
        0, 3, 2
    ],
    'color': [
        *RED,
        *RED,
        *RED
    ]
}


Cube = {
    'position': [
        # Cara frontal
        -0.5, -0.5, 0.5,
        0.5, -0.5, 0.5,
        0.5,  0.5, 0.5,
        -0.5,  0.5, 0.5,
        # Cara trasera
        0.5, -0.5, -0.5,
        -0.5, -0.5, -0.5,
        -0.5,  0.5, -0.5,
        0.5,  0.5, -0.5,
        # Cara izquierda
        -0.5, -0.5, -0.5,
        -0.5, -0.5,  0.5,
        -0.5,  0.5,  0.5,
        -0.5,  0.5, -0.5,
        # Cara derecha
        0.5, -0.5,  0.5,
        0.5, -0.5, -0.5,
        0.5,  0.5, -0.5,
        0.5,  0.5,  0.5,
        # Cara superior
        -0.5,  0.5,  0.5,
        0.5,  0.5,  0.5,
        0.5,  0.5, -0.5,
        -0.5,  0.5, -0.5,
        # Cara inferior
        0.5, -0.5,  0.5,
        -0.5, -0.5,  0.5,
        -0.5, -0.5, -0.5,
        0.5, -0.5, -0.5],
    'color': [
        # Cara frontal
        *BLUE,
        *BLUE,
        *BLUE,
        *BLUE,
        # Cara trasera
        *YELLOW,
        *YELLOW,
        *YELLOW,
        *YELLOW,
        # Cara izquierda
        *CYAN,
        *CYAN,
        *CYAN,
        *CYAN,
        # Cara derecha
        *RED,
        *RED,
        *RED,
        *RED,
        # Cara superior
        *GREEN,
        *GREEN,
        *GREEN,
        *GREEN,
        # Cara inferior
        *MAGENTA,
        *MAGENTA,
        *MAGENTA,
        *MAGENTA],
    'uv': [
        # Cara frontal
        0, 0,
        1, 0,
        1, 1,
        0, 1,
        # Cara trasera
        0, 0,
        1, 0,
        1, 1,
        0, 1,
        # Cara izquierda
        0, 0,
        1, 0,
        1, 1,
        0, 1,
        # Cara derecha
        0, 0,
        1, 0,
        1, 1,
        0, 1,
        # Cara superior
        0, 0,
        1, 0,
        1, 1,
        0, 1,
        # Cara inferior
        0, 0,
        1, 0,
        1, 1,
        0, 1],
    'normal': [
        # Cara frontal
        *([0, 0, 1]*4),
        # Cara trasera
        *([0, 0, -1]*4),
        # Cara izquierda
        *([-1, 0, 0]*4),
        # Cara derecha
        *([1, 0, 0]*4),
        # Cara superior
        *([0, 1, 0]*4),
        # Cara inferior
        *([0, -1, 0]*4)],
    'indices': [
        # Cara frontal
        0, 1, 2,
        2, 3, 0,
        # Cara trasera
        4, 5, 6,
        6, 7, 4,
        # Cara izquierda
        8, 9, 10,
        10, 11, 8,
        # Cara derecha
        12, 13, 14,
        14, 15, 12,
        # Cara superior
        16, 17, 18,
        18, 19, 16,
        # Cara inferior
        20, 21, 22,
        22, 23, 20]
}
